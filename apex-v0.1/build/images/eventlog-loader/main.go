package main

import (
	"bufio"
	"context"
	"crypto/sha256"
	_ "embed"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/ClickHouse/clickhouse-go/v2"
	"github.com/ClickHouse/clickhouse-go/v2/lib/driver"
	"github.com/klauspost/compress/zstd"
	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

//go:embed schema.sql
var schemaSQL string

type rawRow struct {
	EventUID    string
	AppID       string
	EventType   string
	EventTimeMS uint64
	Bucket      string
	ObjectKey   string
	LineNo      uint64
	Raw         string
}

type sqlStartRow struct {
	AppID        string
	ExecutionID  uint64
	Description  string
	Details      string
	PhysicalPlan string
	StartTimeMS  uint64
	EventUID     string
}

type sqlEndRow struct {
	AppID        string
	ExecutionID  uint64
	EndTimeMS    uint64
	ErrorMessage string
	EventUID     string
}

type stageRow struct {
	AppID            string
	StageID          uint64
	StageAttemptID   uint64
	StageName        string
	NumTasks         uint64
	SubmissionTimeMS uint64
	CompletionTimeMS uint64
	EventUID         string
}

type taskRow struct {
	AppID               string
	StageID             uint64
	StageAttemptID      uint64
	TaskID              uint64
	TaskIndex           uint64
	TaskAttempt         uint64
	ExecutorID          string
	Host                string
	LaunchTimeMS        uint64
	FinishTimeMS        uint64
	DurationMS          uint64
	TaskType            string
	Successful          uint8
	Reason              string
	ExecutorRunTimeMS   uint64
	ExecutorCPUTimeNS   uint64
	PeakExecutionMemory uint64
	InputBytes          uint64
	InputRecords        uint64
	OutputBytes         uint64
	OutputRecords       uint64
	ShuffleReadBytes    uint64
	ShuffleWriteBytes   uint64
	ShuffleFetchWaitMS  uint64
	ShuffleWriteTimeNS  uint64
	JVMGCTimeMS         uint64
	MemoryBytesSpilled  uint64
	DiskBytesSpilled    uint64
	EventUID            string
}

type jobRow struct {
	AppID            string
	JobID            uint64
	SQLExecutionID   int64
	SubmissionTimeMS uint64
	CompletionTimeMS uint64
	Result           string
	NumStages        uint64
	StageIDs         []uint64
	EventUID         string
}

type sqlExecutionJobRow struct {
	AppID       string
	ExecutionID uint64
	JobID       uint64
	EventUID    string
}

type adaptivePlanRow struct {
	AppID         string
	ExecutionID   uint64
	PhysicalPlan  string
	SparkPlanInfo string
	EventUID      string
}

type ingestResult struct {
	RawRows          []rawRow
	SQLStarts        []sqlStartRow
	SQLEnds          []sqlEndRow
	Stages           []stageRow
	Tasks            []taskRow
	Jobs             []jobRow
	SQLExecutionJobs []sqlExecutionJobRow
	AdaptivePlans    []adaptivePlanRow
	LineCount        uint64
	SkippedLines     uint64
}

var appIDRE = regexp.MustCompile(`app-[0-9]+-[0-9]+`)

func main() {
	ctx := context.Background()
	logger := log.New(os.Stdout, "eventlog-loader ", log.LstdFlags|log.LUTC)

	ch, err := connectClickHouse(ctx)
	if err != nil {
		logger.Fatalf("connect clickhouse: %v", err)
	}
	if err := ensureSchema(ctx, ch); err != nil {
		logger.Fatalf("ensure schema: %v", err)
	}

	mc, err := connectMinIO()
	if err != nil {
		logger.Fatalf("connect minio: %v", err)
	}

	once := envBool("LOADER_ONCE", false)
	interval := time.Duration(envInt("LOADER_INTERVAL_SECONDS", 10)) * time.Second
	for {
		if err := ingestOnce(ctx, logger, ch, mc); err != nil {
			logger.Printf("ingest error: %v", err)
		}
		if once {
			return
		}
		time.Sleep(interval)
	}
}

func connectClickHouse(ctx context.Context) (driver.Conn, error) {
	addr := env("CLICKHOUSE_ADDR", "clickhouse:9000")
	db := env("CLICKHOUSE_DB", "spark_observability")
	// The loader is the single source of truth for the observability store: it
	// creates the target database here and the tables in ensureSchema(). This
	// makes it idempotent against any ClickHouse data-dir state (fresh or a
	// stale bind mount missing the DB), instead of relying on the image's
	// CLICKHOUSE_DB env, which only runs on a first-boot empty data dir.
	if err := ensureDatabase(ctx, addr, db); err != nil {
		return nil, err
	}
	conn, err := clickhouse.Open(&clickhouse.Options{
		Addr: strings.Split(addr, ","),
		Auth: clickhouse.Auth{
			Database: db,
			Username: mustEnv("CLICKHOUSE_USER"),
			Password: mustEnv("CLICKHOUSE_PASSWORD"),
		},
		DialTimeout:     10 * time.Second,
		MaxOpenConns:    4,
		MaxIdleConns:    2,
		ConnMaxLifetime: time.Hour,
	})
	if err != nil {
		return nil, err
	}
	var lastErr error
	for i := 0; i < 60; i++ {
		if err := conn.Ping(ctx); err == nil {
			return conn, nil
		} else {
			lastErr = err
		}
		time.Sleep(time.Second)
	}
	return nil, lastErr
}

// ensureDatabase creates the target database if it does not exist, using an
// admin connection scoped to the always-present "default" database (a scoped
// connection to a missing DB would fail its Ping before any statement runs).
func ensureDatabase(ctx context.Context, addr, db string) error {
	admin, err := clickhouse.Open(&clickhouse.Options{
		Addr: strings.Split(addr, ","),
		Auth: clickhouse.Auth{
			Database: "default",
			Username: mustEnv("CLICKHOUSE_USER"),
			Password: mustEnv("CLICKHOUSE_PASSWORD"),
		},
		DialTimeout:     10 * time.Second,
		MaxOpenConns:    1,
		ConnMaxLifetime: time.Hour,
	})
	if err != nil {
		return err
	}
	defer admin.Close()
	var lastErr error
	for i := 0; i < 60; i++ {
		if err := admin.Ping(ctx); err == nil {
			lastErr = nil
			break
		} else {
			lastErr = err
		}
		time.Sleep(time.Second)
	}
	if lastErr != nil {
		return lastErr
	}
	return admin.Exec(ctx, "CREATE DATABASE IF NOT EXISTS "+db)
}

func connectMinIO() (*minio.Client, error) {
	return minio.New(env("MINIO_ENDPOINT", "minio:9000"), &minio.Options{
		Creds:  credentials.NewStaticV4(mustEnv("MINIO_ACCESS_KEY"), mustEnv("MINIO_SECRET_KEY"), ""),
		Secure: envBool("MINIO_USE_SSL", false),
	})
}

func ensureSchema(ctx context.Context, conn driver.Conn) error {
	for _, stmt := range splitSQLStatements(schemaSQL) {
		if err := conn.Exec(ctx, stmt); err != nil {
			return err
		}
	}
	return nil
}

// splitSQLStatements breaks the embedded schema into individual statements.
// ClickHouse executes one statement per call. Blank and "--" comment lines are
// dropped first (so a ";" inside a comment cannot split a statement), then the
// remaining DDL is split on ";".
func splitSQLStatements(script string) []string {
	var builder strings.Builder
	for _, line := range strings.Split(script, "\n") {
		trimmed := strings.TrimSpace(line)
		if trimmed == "" || strings.HasPrefix(trimmed, "--") {
			continue
		}
		builder.WriteString(line)
		builder.WriteString("\n")
	}
	var statements []string
	for _, chunk := range strings.Split(builder.String(), ";") {
		if stmt := strings.TrimSpace(chunk); stmt != "" {
			statements = append(statements, stmt)
		}
	}
	return statements
}

func ingestOnce(ctx context.Context, logger *log.Logger, conn driver.Conn, mc *minio.Client) error {
	bucket := env("MINIO_BUCKET", "spark-logs")
	prefix := env("MINIO_PREFIX", "events/")
	objects := mc.ListObjects(ctx, bucket, minio.ListObjectsOptions{Prefix: prefix, Recursive: true})
	for obj := range objects {
		if obj.Err != nil {
			return obj.Err
		}
		if !isEventLogObject(obj.Key) {
			continue
		}
		ingested, err := alreadyIngested(ctx, conn, bucket, obj.Key, obj.ETag)
		if err != nil {
			return err
		}
		if ingested {
			continue
		}
		result, err := readEventLog(ctx, mc, bucket, obj.Key)
		if err != nil {
			logger.Printf("skip %s: %v", obj.Key, err)
			continue
		}
		// Loud failure over silent loss: if the object had content but nothing
		// decoded as event JSON (wrong codec, corruption), do NOT mark it
		// ingested — leave it to be retried and surfaced, instead of recording
		// an empty file that is never reprocessed.
		if len(result.RawRows) == 0 && result.SkippedLines > 0 {
			logger.Printf("skip %s: %d line(s) present but none decoded as event JSON (wrong codec or corrupt); not marking ingested", obj.Key, result.SkippedLines)
			continue
		}
		if err := insertResult(ctx, conn, result); err != nil {
			return fmt.Errorf("insert %s: %w", obj.Key, err)
		}
		if err := markFile(ctx, conn, bucket, obj, result.LineCount); err != nil {
			return err
		}
		logger.Printf("ingested object=%s lines=%d raw=%d sql=%d stages=%d tasks=%d jobs=%d aqe=%d skipped=%d", obj.Key, result.LineCount, len(result.RawRows), len(result.SQLStarts), len(result.Stages), len(result.Tasks), len(result.Jobs), len(result.AdaptivePlans), result.SkippedLines)
	}
	return nil
}

func isEventLogObject(key string) bool {
	if strings.HasSuffix(key, "/") || strings.Contains(key, "appstatus_") {
		return false
	}
	base := key[strings.LastIndex(key, "/")+1:]
	// Rolling logs are named events_*; some are tagged "eventlog". Single-file
	// logs (rolling disabled) are named after the application id (app-<ts>-<n>),
	// which the previous prefix/substring check missed — silently ignoring them.
	return strings.HasPrefix(base, "events_") || strings.Contains(base, "eventlog") || appIDRE.MatchString(base)
}

func alreadyIngested(ctx context.Context, conn driver.Conn, bucket, key, etag string) (bool, error) {
	var count uint64
	err := conn.QueryRow(ctx, "SELECT count() FROM spark_eventlog_files WHERE bucket = ? AND object_key = ? AND etag = ?", bucket, key, etag).Scan(&count)
	return count > 0, err
}

func readEventLog(ctx context.Context, mc *minio.Client, bucket, key string) (ingestResult, error) {
	obj, err := mc.GetObject(ctx, bucket, key, minio.GetObjectOptions{})
	if err != nil {
		return ingestResult{}, err
	}
	defer obj.Close()

	var reader io.Reader = obj
	switch {
	case strings.HasSuffix(key, ".zstd"):
		zstdReader, zerr := zstd.NewReader(obj)
		if zerr != nil {
			return ingestResult{}, zerr
		}
		defer zstdReader.Close()
		reader = zstdReader
	case strings.HasSuffix(key, ".lz4"), strings.HasSuffix(key, ".lzf"),
		strings.HasSuffix(key, ".snappy"), strings.HasSuffix(key, ".gz"):
		// Spark can write event logs with these codecs
		// (spark.eventLog.compression.codec), but this loader only bundles zstd.
		// Fail loudly instead of reading compressed bytes as text — that would
		// silently skip every line and mark the file ingested-with-zero-rows.
		return ingestResult{}, fmt.Errorf("unsupported event-log compression codec for %s (only .zstd is supported)", key)
	}

	return parseEventLog(bucket, key, reader)
}

// parseEventLog reads decompressed Spark event-log JSON lines and normalizes them
// into ingestResult. It is decoupled from MinIO so it can be unit tested with any
// io.Reader of event-log content.
func parseEventLog(bucket, key string, reader io.Reader) (ingestResult, error) {
	appID := appIDFromKey(key)
	result := ingestResult{}
	jobs := map[uint64]*jobRow{}
	var jobOrder []uint64
	// bufio.Reader (not Scanner) so a single oversized line — e.g. a huge AQE
	// physical-plan event — is read in full instead of tripping Scanner's token
	// cap and aborting the WHOLE file (which would then be retried forever,
	// never ingested). ReadString has no per-line length limit.
	bufReader := bufio.NewReaderSize(reader, 1024*1024)
	for {
		line, readErr := bufReader.ReadString('\n')
		if readErr != nil && len(line) == 0 {
			if readErr == io.EOF {
				break
			}
			return ingestResult{}, readErr
		}
		line = strings.TrimRight(line, "\r\n")
		result.LineCount++
		if strings.TrimSpace(line) == "" {
			if readErr != nil {
				break
			}
			continue
		}
		var event map[string]any
		decoder := json.NewDecoder(strings.NewReader(line))
		decoder.UseNumber()
		if err := decoder.Decode(&event); err != nil {
			result.SkippedLines++
			continue
		}
		if id := stringAt(event, "App ID"); id != "" {
			appID = id
		}
		eventType := stringAt(event, "Event")
		uid := eventUID(bucket, key, result.LineCount, line)
		result.RawRows = append(result.RawRows, rawRow{EventUID: uid, AppID: appID, EventType: eventType, EventTimeMS: eventTimeMillis(eventType, event), Bucket: bucket, ObjectKey: key, LineNo: result.LineCount, Raw: line})
		switch {
		case strings.HasSuffix(eventType, "SparkListenerSQLExecutionStart"):
			result.SQLStarts = append(result.SQLStarts, sqlStartRow{AppID: appID, ExecutionID: uintAt(event, "executionId"), Description: stringAt(event, "description"), Details: stringAt(event, "details"), PhysicalPlan: stringAt(event, "physicalPlanDescription"), StartTimeMS: uintAt(event, "time"), EventUID: uid})
		case strings.HasSuffix(eventType, "SparkListenerSQLExecutionEnd"):
			result.SQLEnds = append(result.SQLEnds, sqlEndRow{AppID: appID, ExecutionID: uintAt(event, "executionId"), EndTimeMS: uintAt(event, "time"), ErrorMessage: valueString(event["errorMessage"]), EventUID: uid})
		case strings.HasSuffix(eventType, "SparkListenerSQLAdaptiveExecutionUpdate"):
			result.AdaptivePlans = append(result.AdaptivePlans, adaptivePlanRow{AppID: appID, ExecutionID: uintAt(event, "executionId"), PhysicalPlan: stringAt(event, "physicalPlanDescription"), SparkPlanInfo: valueString(event["sparkPlanInfo"]), EventUID: uid})
		case eventType == "SparkListenerStageCompleted":
			if row, ok := stageFromEvent(appID, uid, event); ok {
				result.Stages = append(result.Stages, row)
			}
		case eventType == "SparkListenerTaskEnd":
			if row, ok := taskFromEvent(appID, uid, event); ok {
				result.Tasks = append(result.Tasks, row)
			}
		case eventType == "SparkListenerJobStart":
			jobID := uintAt(event, "Job ID")
			job := upsertJob(jobs, &jobOrder, jobID, appID, uid)
			job.AppID = appID
			job.SubmissionTimeMS = uintAt(event, "Submission Time")
			job.StageIDs = uintSliceAt(event, "Stage IDs")
			job.NumStages = uint64(len(job.StageIDs))
			job.EventUID = uid
			if execID, ok := sqlExecutionID(event); ok {
				job.SQLExecutionID = int64(execID)
				result.SQLExecutionJobs = append(result.SQLExecutionJobs, sqlExecutionJobRow{AppID: appID, ExecutionID: execID, JobID: jobID, EventUID: uid})
			}
		case eventType == "SparkListenerJobEnd":
			jobID := uintAt(event, "Job ID")
			job := upsertJob(jobs, &jobOrder, jobID, appID, uid)
			job.CompletionTimeMS = uintAt(event, "Completion Time")
			job.Result = stringAt(mapAt(event, "Job Result"), "Result")
		}
		if readErr != nil {
			break
		}
	}
	for _, id := range jobOrder {
		result.Jobs = append(result.Jobs, *jobs[id])
	}
	return result, nil
}

// upsertJob returns the in-progress job row for jobID, creating it (in first-seen
// order) when a JobStart or JobEnd is encountered first.
func upsertJob(jobs map[uint64]*jobRow, order *[]uint64, jobID uint64, appID, uid string) *jobRow {
	if job, ok := jobs[jobID]; ok {
		return job
	}
	job := &jobRow{AppID: appID, JobID: jobID, SQLExecutionID: -1, EventUID: uid}
	jobs[jobID] = job
	*order = append(*order, jobID)
	return job
}

// sqlExecutionID extracts spark.sql.execution.id from a JobStart's Properties map.
func sqlExecutionID(event map[string]any) (uint64, bool) {
	value := stringAt(mapAt(event, "Properties"), "spark.sql.execution.id")
	if value == "" {
		return 0, false
	}
	parsed, err := strconv.ParseUint(value, 10, 64)
	if err != nil {
		return 0, false
	}
	return parsed, true
}

func insertResult(ctx context.Context, conn driver.Conn, result ingestResult) error {
	if len(result.RawRows) > 0 {
		batch, err := conn.PrepareBatch(ctx, "INSERT INTO spark_raw_events (event_uid, app_id, event_type, event_time_ms, bucket, object_key, line_no, raw)")
		if err != nil {
			return err
		}
		for _, row := range result.RawRows {
			if err := batch.Append(row.EventUID, row.AppID, row.EventType, row.EventTimeMS, row.Bucket, row.ObjectKey, row.LineNo, row.Raw); err != nil {
				return err
			}
		}
		if err := batch.Send(); err != nil {
			return err
		}
	}
	if len(result.SQLStarts) > 0 {
		batch, err := conn.PrepareBatch(ctx, "INSERT INTO spark_sql_executions (app_id, execution_id, description, details, physical_plan, start_time_ms, event_uid)")
		if err != nil {
			return err
		}
		for _, row := range result.SQLStarts {
			if err := batch.Append(row.AppID, row.ExecutionID, row.Description, row.Details, row.PhysicalPlan, row.StartTimeMS, row.EventUID); err != nil {
				return err
			}
		}
		if err := batch.Send(); err != nil {
			return err
		}
	}
	if len(result.SQLEnds) > 0 {
		batch, err := conn.PrepareBatch(ctx, "INSERT INTO spark_sql_execution_ends (app_id, execution_id, end_time_ms, error_message, event_uid)")
		if err != nil {
			return err
		}
		for _, row := range result.SQLEnds {
			if err := batch.Append(row.AppID, row.ExecutionID, row.EndTimeMS, row.ErrorMessage, row.EventUID); err != nil {
				return err
			}
		}
		if err := batch.Send(); err != nil {
			return err
		}
	}
	if len(result.Stages) > 0 {
		batch, err := conn.PrepareBatch(ctx, "INSERT INTO spark_stages (app_id, stage_id, stage_attempt_id, stage_name, num_tasks, submission_time_ms, completion_time_ms, event_uid)")
		if err != nil {
			return err
		}
		for _, row := range result.Stages {
			if err := batch.Append(row.AppID, row.StageID, row.StageAttemptID, row.StageName, row.NumTasks, row.SubmissionTimeMS, row.CompletionTimeMS, row.EventUID); err != nil {
				return err
			}
		}
		if err := batch.Send(); err != nil {
			return err
		}
	}
	if len(result.Tasks) > 0 {
		batch, err := conn.PrepareBatch(ctx, "INSERT INTO spark_tasks (app_id, stage_id, stage_attempt_id, task_id, task_index, task_attempt, executor_id, host, launch_time_ms, finish_time_ms, duration_ms, task_type, successful, reason, executor_run_time_ms, executor_cpu_time_ns, peak_execution_memory, input_bytes, input_records, output_bytes, output_records, shuffle_read_bytes, shuffle_write_bytes, shuffle_fetch_wait_ms, shuffle_write_time_ns, jvm_gc_time_ms, memory_bytes_spilled, disk_bytes_spilled, event_uid)")
		if err != nil {
			return err
		}
		for _, row := range result.Tasks {
			if err := batch.Append(row.AppID, row.StageID, row.StageAttemptID, row.TaskID, row.TaskIndex, row.TaskAttempt, row.ExecutorID, row.Host, row.LaunchTimeMS, row.FinishTimeMS, row.DurationMS, row.TaskType, row.Successful, row.Reason, row.ExecutorRunTimeMS, row.ExecutorCPUTimeNS, row.PeakExecutionMemory, row.InputBytes, row.InputRecords, row.OutputBytes, row.OutputRecords, row.ShuffleReadBytes, row.ShuffleWriteBytes, row.ShuffleFetchWaitMS, row.ShuffleWriteTimeNS, row.JVMGCTimeMS, row.MemoryBytesSpilled, row.DiskBytesSpilled, row.EventUID); err != nil {
				return err
			}
		}
		if err := batch.Send(); err != nil {
			return err
		}
	}
	if len(result.Jobs) > 0 {
		batch, err := conn.PrepareBatch(ctx, "INSERT INTO spark_jobs (app_id, job_id, sql_execution_id, submission_time_ms, completion_time_ms, result, num_stages, stage_ids, event_uid)")
		if err != nil {
			return err
		}
		for _, row := range result.Jobs {
			if err := batch.Append(row.AppID, row.JobID, row.SQLExecutionID, row.SubmissionTimeMS, row.CompletionTimeMS, row.Result, row.NumStages, row.StageIDs, row.EventUID); err != nil {
				return err
			}
		}
		if err := batch.Send(); err != nil {
			return err
		}
	}
	if len(result.SQLExecutionJobs) > 0 {
		batch, err := conn.PrepareBatch(ctx, "INSERT INTO spark_sql_execution_jobs (app_id, execution_id, job_id, event_uid)")
		if err != nil {
			return err
		}
		for _, row := range result.SQLExecutionJobs {
			if err := batch.Append(row.AppID, row.ExecutionID, row.JobID, row.EventUID); err != nil {
				return err
			}
		}
		if err := batch.Send(); err != nil {
			return err
		}
	}
	if len(result.AdaptivePlans) > 0 {
		batch, err := conn.PrepareBatch(ctx, "INSERT INTO spark_sql_adaptive_plans (app_id, execution_id, physical_plan, spark_plan_info, event_uid)")
		if err != nil {
			return err
		}
		for _, row := range result.AdaptivePlans {
			if err := batch.Append(row.AppID, row.ExecutionID, row.PhysicalPlan, row.SparkPlanInfo, row.EventUID); err != nil {
				return err
			}
		}
		if err := batch.Send(); err != nil {
			return err
		}
	}
	return nil
}

func markFile(ctx context.Context, conn driver.Conn, bucket string, obj minio.ObjectInfo, lineCount uint64) error {
	batch, err := conn.PrepareBatch(ctx, "INSERT INTO spark_eventlog_files (bucket, object_key, etag, size, last_modified, line_count)")
	if err != nil {
		return err
	}
	if err := batch.Append(bucket, obj.Key, obj.ETag, uint64(maxInt64(obj.Size, 0)), obj.LastModified.UTC(), lineCount); err != nil {
		return err
	}
	return batch.Send()
}

func stageFromEvent(appID, uid string, event map[string]any) (stageRow, bool) {
	info := mapAt(event, "Stage Info")
	if info == nil {
		return stageRow{}, false
	}
	return stageRow{AppID: appID, StageID: uintAt(info, "Stage ID"), StageAttemptID: uintAt(info, "Stage Attempt ID"), StageName: stringAt(info, "Stage Name"), NumTasks: uintAt(info, "Number of Tasks"), SubmissionTimeMS: uintAt(info, "Submission Time"), CompletionTimeMS: uintAt(info, "Completion Time"), EventUID: uid}, true
}

func taskFromEvent(appID, uid string, event map[string]any) (taskRow, bool) {
	info := mapAt(event, "Task Info")
	metrics := mapAt(event, "Task Metrics")
	if info == nil {
		return taskRow{}, false
	}
	launch := uintAt(info, "Launch Time")
	finish := uintAt(info, "Finish Time")
	input := mapAt(metrics, "Input Metrics")
	output := mapAt(metrics, "Output Metrics")
	shuffleRead := mapAt(metrics, "Shuffle Read Metrics")
	shuffleWrite := mapAt(metrics, "Shuffle Write Metrics")
	successful := uint8(0)
	if boolAt(info, "Successful") || strings.Contains(valueString(event["Task End Reason"]), "Success") {
		successful = 1
	}
	return taskRow{
		AppID:               appID,
		StageID:             uintAt(event, "Stage ID"),
		StageAttemptID:      uintAt(event, "Stage Attempt ID"),
		TaskID:              uintAt(info, "Task ID"),
		TaskIndex:           uintAt(info, "Index"),
		TaskAttempt:         uintAt(info, "Attempt"),
		ExecutorID:          stringAt(info, "Executor ID"),
		Host:                stringAt(info, "Host"),
		LaunchTimeMS:        launch,
		FinishTimeMS:        finish,
		DurationMS:          durationMillis(launch, finish),
		TaskType:            stringAt(event, "Task Type"),
		Successful:          successful,
		Reason:              valueString(event["Task End Reason"]),
		ExecutorRunTimeMS:   uintAt(metrics, "Executor Run Time"),
		ExecutorCPUTimeNS:   uintAt(metrics, "Executor CPU Time"),
		PeakExecutionMemory: uintAt(metrics, "Peak Execution Memory"),
		InputBytes:          uintAt(input, "Bytes Read"),
		InputRecords:        uintAt(input, "Records Read"),
		OutputBytes:         uintAt(output, "Bytes Written"),
		OutputRecords:       uintAt(output, "Records Written"),
		ShuffleReadBytes:    uintAt(shuffleRead, "Local Bytes Read") + uintAt(shuffleRead, "Remote Bytes Read") + uintAt(shuffleRead, "Remote Bytes Read To Disk"),
		ShuffleWriteBytes:   uintAt(shuffleWrite, "Shuffle Bytes Written"),
		ShuffleFetchWaitMS:  uintAt(shuffleRead, "Fetch Wait Time"),
		ShuffleWriteTimeNS:  uintAt(shuffleWrite, "Shuffle Write Time"),
		JVMGCTimeMS:         uintAt(metrics, "JVM GC Time"),
		MemoryBytesSpilled:  uintAt(metrics, "Memory Bytes Spilled"),
		DiskBytesSpilled:    uintAt(metrics, "Disk Bytes Spilled"),
		EventUID:            uid,
	}, true
}

func eventTimeMillis(eventType string, event map[string]any) uint64 {
	switch {
	case strings.HasSuffix(eventType, "SparkListenerSQLExecutionStart") || strings.HasSuffix(eventType, "SparkListenerSQLExecutionEnd"):
		return uintAt(event, "time")
	case eventType == "SparkListenerApplicationStart" || eventType == "SparkListenerApplicationEnd":
		return uintAt(event, "Timestamp")
	case eventType == "SparkListenerStageCompleted":
		info := mapAt(event, "Stage Info")
		if t := uintAt(info, "Completion Time"); t > 0 {
			return t
		}
		return uintAt(info, "Submission Time")
	case eventType == "SparkListenerTaskEnd":
		return uintAt(mapAt(event, "Task Info"), "Finish Time")
	case eventType == "SparkListenerTaskStart":
		return uintAt(mapAt(event, "Task Info"), "Launch Time")
	case eventType == "SparkListenerStageSubmitted":
		return uintAt(mapAt(event, "Stage Info"), "Submission Time")
	case eventType == "SparkListenerJobStart":
		return uintAt(event, "Submission Time")
	case eventType == "SparkListenerJobEnd":
		return uintAt(event, "Completion Time")
	// ExecutorAdded/Removed, BlockManagerAdded/Removed and similar lifecycle
	// events carry a top-level "Timestamp". (SparkListenerBlockUpdated has no
	// timestamp in the Spark schema and stays 0 — the spark_cache_blocks view
	// falls back to ingested_at for its time axis.)
	case uintAt(event, "Timestamp") > 0:
		return uintAt(event, "Timestamp")
	default:
		return 0
	}
}

func eventUID(bucket, key string, lineNo uint64, raw string) string {
	sum := sha256.Sum256([]byte(fmt.Sprintf("%s\n%s\n%d\n%s", bucket, key, lineNo, raw)))
	return hex.EncodeToString(sum[:])
}

func appIDFromKey(key string) string {
	return appIDRE.FindString(key)
}

func mapAt(m map[string]any, key string) map[string]any {
	if m == nil {
		return nil
	}
	if child, ok := m[key].(map[string]any); ok {
		return child
	}
	return nil
}

func stringAt(m map[string]any, key string) string {
	if m == nil {
		return ""
	}
	return valueString(m[key])
}

func valueString(v any) string {
	switch x := v.(type) {
	case nil:
		return ""
	case string:
		return x
	case json.Number:
		return x.String()
	case bool:
		return strconv.FormatBool(x)
	default:
		bytes, err := json.Marshal(x)
		if err != nil {
			return fmt.Sprintf("%v", x)
		}
		return string(bytes)
	}
}

func uintAt(m map[string]any, key string) uint64 {
	if m == nil {
		return 0
	}
	return toUint(m[key])
}

func uintSliceAt(m map[string]any, key string) []uint64 {
	if m == nil {
		return nil
	}
	values, ok := m[key].([]any)
	if !ok {
		return nil
	}
	out := make([]uint64, 0, len(values))
	for _, value := range values {
		out = append(out, toUint(value))
	}
	return out
}

func toUint(v any) uint64 {
	switch x := v.(type) {
	case nil:
		return 0
	case json.Number:
		if u, err := strconv.ParseUint(x.String(), 10, 64); err == nil {
			return u
		}
		if f, err := strconv.ParseFloat(x.String(), 64); err == nil && f > 0 {
			return uint64(f)
		}
	case float64:
		if x > 0 {
			return uint64(x)
		}
	case int:
		if x > 0 {
			return uint64(x)
		}
	case int64:
		if x > 0 {
			return uint64(x)
		}
	case uint64:
		return x
	}
	return 0
}

func boolAt(m map[string]any, key string) bool {
	if m == nil {
		return false
	}
	b, _ := m[key].(bool)
	return b
}

func durationMillis(start, end uint64) uint64 {
	if end > start {
		return end - start
	}
	return 0
}

func maxInt64(a int64, min int64) int64 {
	if a < min {
		return min
	}
	return a
}

func env(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}

// mustEnv returns a required credential from the environment and aborts if it
// is missing. Credentials must never have a committed default: an in-code
// fallback silently connects with a public, known secret when the variable is
// unset, defeating the compose-level `${VAR:?}` guard. The loader always runs
// under compose, which supplies these, so a Fatalf here is the intended, loud
// failure for a misconfigured environment.
func mustEnv(key string) string {
	value := os.Getenv(key)
	if value == "" {
		log.Fatalf("required environment variable %s is not set", key)
	}
	return value
}

func envBool(key string, fallback bool) bool {
	value := strings.ToLower(strings.TrimSpace(os.Getenv(key)))
	if value == "" {
		return fallback
	}
	return value == "1" || value == "true" || value == "yes"
}

func envInt(key string, fallback int) int {
	value := strings.TrimSpace(os.Getenv(key))
	if value == "" {
		return fallback
	}
	parsed, err := strconv.Atoi(value)
	if err != nil || parsed <= 0 {
		return fallback
	}
	return parsed
}
