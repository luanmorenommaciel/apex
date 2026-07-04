#!/usr/bin/env python3
import sys
import json
from datetime import datetime
import re

def extract_yaml_field(yaml_text, key_path):
    parts = key_path.split('.')
    current = yaml_text
    for part in parts:
        pattern = rf'(?m)^\s*{re.escape(part)}\s*:\s*(.*)$'
        match = re.search(pattern, current)
        if not match:
            return None
        value = match.group(1).strip()
        if value.startswith('{') and value.endswith('}'):
            result = {}
            for kv in value[1:-1].split(','):
                if ':' in kv:
                    k, v = kv.split(':', 1)
                    result[k.strip()] = v.strip()
            current = result
        else:
            return value
    return current

def generate_plan(scenario_path, output_path):
    with open(scenario_path, 'r') as f:
        yaml_text = f.read()
    
    scenario_id = extract_yaml_field(yaml_text, 'scenario_id')
    join_operator = extract_yaml_field(yaml_text, 'plan_generator.expected_signals.join_operator')
    stage = extract_yaml_field(yaml_text, 'plan_generator.expected_signals.hot_partition.stage')
    shuffle_records = extract_yaml_field(yaml_text, 'plan_generator.expected_signals.hot_partition.single_task_shuffle_read_records')
    
    synthetic_log = [
        {"event": "SparkListenerApplicationStart", "appName": scenario_id, "timestamp": datetime.now().isoformat()},
        {"event": "SparkListenerSQLExecutionStart", "sqlExecutionId": 1, "description": "join", "physicalPlanDescription": join_operator or "SortMergeJoin"},
        {"event": "SparkListenerStageSubmitted", "stageId": int(stage or 4), "numTasks": 100},
        {"event": "SparkListenerTaskEnd", "stageId": int(stage or 4), "taskInfo": {"taskId": 42}, "taskMetrics": {"shuffleReadMetrics": {"recordsRead": int(shuffle_records or 200100)}}},
        {"event": "SparkListenerApplicationEnd", "timestamp": datetime.now().isoformat()}
    ]
    
    with open(output_path, 'w') as f:
        for event in synthetic_log:
            f.write(json.dumps(event) + '\n')
    print(f"✅ Gerado event log sintético {output_path} a partir de {scenario_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python plan_generator_no_yaml.py <scenario.yaml> <output_ndjson>")
        sys.exit(1)
    generate_plan(sys.argv[1], sys.argv[2])
