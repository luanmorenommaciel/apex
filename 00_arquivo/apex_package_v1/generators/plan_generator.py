#!/usr/bin/env python3
import yaml
import sys
import json
from datetime import datetime

def generate_plan(scenario_path, output_path):
    with open(scenario_path, 'r') as f:
        config = yaml.safe_load(f)

    signals = config['plan_generator']['expected_signals']
    scenario_id = config['scenario_id']

    # Cria um event log sintético mínimo contendo os sinais esperados
    synthetic_log = [
        {
            "event": "SparkListenerApplicationStart",
            "appName": scenario_id,
            "timestamp": datetime.now().isoformat()
        },
        {
            "event": "SparkListenerSQLExecutionStart",
            "sqlExecutionId": 1,
            "description": "join",
            "physicalPlanDescription": signals.get('join_operator', 'SortMergeJoin')
        },
        {
            "event": "SparkListenerStageSubmitted",
            "stageId": signals.get('hot_partition', {}).get('stage', 4),
            "numTasks": 100
        },
        {
            "event": "SparkListenerTaskEnd",
            "stageId": signals.get('hot_partition', {}).get('stage', 4),
            "taskInfo": {"taskId": 42},
            "taskMetrics": {
                "shuffleReadMetrics": {
                    "recordsRead": signals.get('hot_partition', {}).get('single_task_shuffle_read_records', 200100)
                }
            }
        },
        {
            "event": "SparkListenerApplicationEnd",
            "timestamp": datetime.now().isoformat()
        }
    ]

    with open(output_path, 'w') as f:
        for event in synthetic_log:
            f.write(json.dumps(event) + '\n')
    print(f"✅ Gerado event log sintético {output_path} a partir de {scenario_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python plan_generator.py <scenario.yaml> <output_ndjson>")
        sys.exit(1)
    generate_plan(sys.argv[1], sys.argv[2])
