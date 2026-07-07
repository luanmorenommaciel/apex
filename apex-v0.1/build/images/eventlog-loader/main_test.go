package main

import (
	"reflect"
	"strings"
	"testing"
)

// eventLogFixture is a minimal but realistic single-SQL-execution event log:
// app start, a SQL execution, one job (linked to the execution) with two stages,
// one completed stage, one task, an adaptive-plan update, job end, SQL end, and a
// final malformed line to exercise the skip path.
var eventLogFixture = strings.Join([]string{
	`{"Event":"SparkListenerApplicationStart","App Name":"smoke","App ID":"app-20260101010101-0001","Timestamp":1700000000000}`,
	`{"Event":"org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionStart","executionId":0,"description":"select customers","details":"detail-text","physicalPlanDescription":"== Physical Plan ==\nScan json","sparkPlanInfo":{"nodeName":"Scan json"},"time":1700000001000}`,
	`{"Event":"SparkListenerJobStart","Job ID":0,"Submission Time":1700000001500,"Stage Infos":[{"Stage ID":0}],"Stage IDs":[0,1],"Properties":{"spark.sql.execution.id":"0","spark.app.name":"smoke"}}`,
	`{"Event":"SparkListenerStageCompleted","Stage Info":{"Stage ID":0,"Stage Attempt ID":0,"Stage Name":"json scan","Number of Tasks":2,"Submission Time":1700000001600,"Completion Time":1700000002000}}`,
	`{"Event":"SparkListenerTaskEnd","Stage ID":0,"Stage Attempt ID":0,"Task Type":"ResultTask","Task End Reason":{"Reason":"Success"},"Task Info":{"Task ID":10,"Index":0,"Attempt":0,"Launch Time":1700000001700,"Finish Time":1700000001900,"Executor ID":"0","Host":"worker-1","Successful":true},"Task Metrics":{"Executor Run Time":150,"Executor CPU Time":120000000,"Peak Execution Memory":1048576,"JVM GC Time":7,"Memory Bytes Spilled":11111,"Disk Bytes Spilled":22222,"Input Metrics":{"Bytes Read":2048,"Records Read":5},"Output Metrics":{"Bytes Written":0,"Records Written":0},"Shuffle Read Metrics":{"Local Bytes Read":100,"Remote Bytes Read":200,"Remote Bytes Read To Disk":0},"Shuffle Write Metrics":{"Shuffle Bytes Written":300}}}`,
	`{"Event":"org.apache.spark.sql.execution.ui.SparkListenerSQLAdaptiveExecutionUpdate","executionId":0,"physicalPlanDescription":"== Physical Plan (AQE) ==\nAdaptiveSparkPlan","sparkPlanInfo":{"nodeName":"AdaptiveSparkPlan"}}`,
	`{"Event":"SparkListenerJobEnd","Job ID":0,"Completion Time":1700000002100,"Job Result":{"Result":"JobSucceeded"}}`,
	`{"Event":"org.apache.spark.sql.execution.ui.SparkListenerSQLExecutionEnd","executionId":0,"time":1700000002200}`,
	`{ this is not valid json }`,
}, "\n")

func TestParseEventLogNormalizesEvents(t *testing.T) {
	result, err := parseEventLog("spark-logs", "events/eventlog_v2_app-20260101010101-0001/events_1_app-20260101010101-0001", strings.NewReader(eventLogFixture))
	if err != nil {
		t.Fatalf("parseEventLog returned error: %v", err)
	}

	if result.LineCount != 9 {
		t.Errorf("LineCount = %d, want 9", result.LineCount)
	}
	if result.SkippedLines != 1 {
		t.Errorf("SkippedLines = %d, want 1", result.SkippedLines)
	}
	if len(result.RawRows) != 8 {
		t.Fatalf("RawRows = %d, want 8", len(result.RawRows))
	}
	if got := result.RawRows[0].AppID; got != "app-20260101010101-0001" {
		t.Errorf("RawRows[0].AppID = %q, want app id from App ID field", got)
	}

	if len(result.SQLStarts) != 1 {
		t.Fatalf("SQLStarts = %d, want 1", len(result.SQLStarts))
	}
	start := result.SQLStarts[0]
	if start.ExecutionID != 0 || start.Description != "select customers" {
		t.Errorf("SQLStart fields unexpected: %+v", start)
	}
	if !strings.Contains(start.PhysicalPlan, "Physical Plan") {
		t.Errorf("SQLStart.PhysicalPlan = %q, want it to contain the plan text", start.PhysicalPlan)
	}

	if len(result.SQLEnds) != 1 || result.SQLEnds[0].EndTimeMS != 1700000002200 {
		t.Errorf("SQLEnds unexpected: %+v", result.SQLEnds)
	}

	if len(result.Stages) != 1 {
		t.Fatalf("Stages = %d, want 1", len(result.Stages))
	}
	stage := result.Stages[0]
	if stage.NumTasks != 2 || stage.StageName != "json scan" || stage.CompletionTimeMS != 1700000002000 {
		t.Errorf("Stage fields unexpected: %+v", stage)
	}

	if len(result.Tasks) != 1 {
		t.Fatalf("Tasks = %d, want 1", len(result.Tasks))
	}
	task := result.Tasks[0]
	if task.StageID != 0 || task.TaskID != 10 || task.Successful != 1 {
		t.Errorf("Task identity unexpected: %+v", task)
	}
	if task.DurationMS != 200 || task.ExecutorRunTimeMS != 150 {
		t.Errorf("Task timing unexpected: duration=%d run=%d", task.DurationMS, task.ExecutorRunTimeMS)
	}
	if task.InputBytes != 2048 || task.InputRecords != 5 {
		t.Errorf("Task input unexpected: bytes=%d records=%d", task.InputBytes, task.InputRecords)
	}
	if task.ShuffleReadBytes != 300 || task.ShuffleWriteBytes != 300 {
		t.Errorf("Task shuffle unexpected: read=%d write=%d", task.ShuffleReadBytes, task.ShuffleWriteBytes)
	}
	if task.JVMGCTimeMS != 7 || task.MemoryBytesSpilled != 11111 || task.DiskBytesSpilled != 22222 {
		t.Errorf("Task GC/spill unexpected: gc=%d memSpill=%d diskSpill=%d", task.JVMGCTimeMS, task.MemoryBytesSpilled, task.DiskBytesSpilled)
	}

	if len(result.Jobs) != 1 {
		t.Fatalf("Jobs = %d, want 1", len(result.Jobs))
	}
	job := result.Jobs[0]
	if job.JobID != 0 || job.SQLExecutionID != 0 {
		t.Errorf("Job identity unexpected: %+v", job)
	}
	if job.SubmissionTimeMS != 1700000001500 || job.CompletionTimeMS != 1700000002100 {
		t.Errorf("Job timing unexpected: submit=%d complete=%d", job.SubmissionTimeMS, job.CompletionTimeMS)
	}
	if job.Result != "JobSucceeded" {
		t.Errorf("Job.Result = %q, want JobSucceeded", job.Result)
	}
	if job.NumStages != 2 || !reflect.DeepEqual(job.StageIDs, []uint64{0, 1}) {
		t.Errorf("Job stages unexpected: num=%d ids=%v", job.NumStages, job.StageIDs)
	}

	if len(result.SQLExecutionJobs) != 1 {
		t.Fatalf("SQLExecutionJobs = %d, want 1", len(result.SQLExecutionJobs))
	}
	link := result.SQLExecutionJobs[0]
	if link.ExecutionID != 0 || link.JobID != 0 {
		t.Errorf("SQL execution-to-job link unexpected: %+v", link)
	}

	if len(result.AdaptivePlans) != 1 {
		t.Fatalf("AdaptivePlans = %d, want 1", len(result.AdaptivePlans))
	}
	plan := result.AdaptivePlans[0]
	if plan.ExecutionID != 0 || !strings.Contains(plan.PhysicalPlan, "AQE") {
		t.Errorf("Adaptive plan text unexpected: %+v", plan)
	}
	if !strings.Contains(plan.SparkPlanInfo, "AdaptiveSparkPlan") {
		t.Errorf("Adaptive plan info = %q, want serialized sparkPlanInfo", plan.SparkPlanInfo)
	}
}

func TestParseEventLogJobWithoutSQLExecution(t *testing.T) {
	fixture := strings.Join([]string{
		`{"Event":"SparkListenerJobStart","Job ID":7,"Submission Time":10,"Stage IDs":[3],"Properties":{"spark.app.name":"x"}}`,
		`{"Event":"SparkListenerJobEnd","Job ID":7,"Completion Time":20,"Job Result":{"Result":"JobSucceeded"}}`,
	}, "\n")

	result, err := parseEventLog("spark-logs", "events/eventlog_v2_app-1/events_1_app-1", strings.NewReader(fixture))
	if err != nil {
		t.Fatalf("parseEventLog returned error: %v", err)
	}

	if len(result.Jobs) != 1 {
		t.Fatalf("Jobs = %d, want 1", len(result.Jobs))
	}
	job := result.Jobs[0]
	if job.SQLExecutionID != -1 {
		t.Errorf("Job.SQLExecutionID = %d, want -1 (no SQL execution)", job.SQLExecutionID)
	}
	if job.NumStages != 1 || !reflect.DeepEqual(job.StageIDs, []uint64{3}) {
		t.Errorf("Job stages unexpected: num=%d ids=%v", job.NumStages, job.StageIDs)
	}
	if len(result.SQLExecutionJobs) != 0 {
		t.Errorf("SQLExecutionJobs = %d, want 0 for a non-SQL job", len(result.SQLExecutionJobs))
	}
}

func TestSplitSQLStatementsMatchesEmbeddedSchema(t *testing.T) {
	statements := splitSQLStatements(schemaSQL)
	if len(statements) != 17 {
		t.Fatalf("splitSQLStatements returned %d statements, want 17 (10 CREATE TABLE + 2 CREATE VIEW + 5 migration ALTER TABLE)", len(statements))
	}
	var creates, views, alters int
	for _, stmt := range statements {
		switch {
		case strings.HasPrefix(stmt, "CREATE TABLE"):
			creates++
		case strings.HasPrefix(stmt, "CREATE VIEW"):
			views++
		case strings.HasPrefix(stmt, "ALTER TABLE"):
			alters++
		default:
			t.Errorf("unexpected statement (comments should be stripped): %q", stmt)
		}
	}
	if creates != 10 {
		t.Errorf("CREATE TABLE statements = %d, want 10", creates)
	}
	if views != 2 {
		t.Errorf("CREATE VIEW statements = %d, want 2", views)
	}
	if alters != 5 {
		t.Errorf("ALTER TABLE statements = %d, want 5", alters)
	}
}
