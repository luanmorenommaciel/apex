#!/usr/bin/env bash
# Slice vertical do Apex: contrato -> codigo -> log fiel -> deteccao -> acceptance.
set -e
S="${1:-scenarios/skew_on_join_30x.yaml}"
echo "▶ 1/3 gerar codigo (sentinela -> manifesto)"; python3 generators/code_generator.py "$S" job_demo.py
echo "▶ 2/3 gerar log sintetico fiel";               python3 generators/plan_generator.py "$S" synthetic_log.ndjson
echo "▶ 3/3 Watcher detecta + valida acceptance";     python3 watchers/skew_watcher.py "$S" synthetic_log.ndjson
echo "🟢 SLICE COMPLETO"
