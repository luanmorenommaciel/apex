import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def write_log(tmp_path, name, events):
    path = tmp_path / name
    path.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
    return path


def test_dynamic_map_entries_are_grouped():
    from tools import coverage_inventory

    event = {
        "Event": "SparkListenerEnvironmentUpdate",
        "Classpath Entries": {
            "/opt/spark/jars/a.jar": "System Classpath",
            "/opt/spark/jars/b.jar": "System Classpath",
        },
    }

    fields = {path for path, _ in coverage_inventory.walk(event)}

    assert "Classpath Entries.<entry>" in fields
    assert not any("a.jar" in field or "b.jar" in field for field in fields)


def test_inventory_counts_sources_and_applications(tmp_path):
    from tools import coverage_inventory

    first = write_log(
        tmp_path,
        "first.ndjson",
        [
            {"Event": "SparkListenerApplicationStart", "App ID": "app-1"},
            {"Event": "SparkListenerTaskEnd", "Stage ID": 1},
        ],
    )
    second = write_log(
        tmp_path,
        "second.ndjson",
        [
            {"Event": "SparkListenerApplicationStart", "App ID": "app-2"},
            {"Event": "SparkListenerTaskEnd", "Stage ID": 2},
        ],
    )

    result = coverage_inventory.inventory([str(first), str(second)])

    assert result.source_count == 2
    assert result.application_ids == {"app-1", "app-2"}


def test_small_corpus_warning_uses_application_count(tmp_path):
    from tools import coverage_inventory

    events = [{"Event": f"event-{index}"} for index in range(17)]
    events.append({"Event": "SparkListenerApplicationStart", "App ID": "app-1"})
    log = write_log(tmp_path, "one-app.ndjson", events)

    result = coverage_inventory.inventory([str(log)])
    text = coverage_inventory.report(result)

    assert "Corpus parcial: 1 aplicacao" in text
    assert "18 tipos de evento" in text


def test_spark_plan_info_descendants_are_high_value():
    from tools import coverage_inventory

    assert coverage_inventory.classify("sparkPlanInfo.nodeName") == "B*"
    assert coverage_inventory.classify("sparkPlanInfo.children.nodeName") == "B*"
    assert coverage_inventory.classify("sparkPlanInfo.metrics.name") == "B*"


def test_recursive_spark_plan_paths_are_collapsed():
    from tools import coverage_inventory

    plan = {
        "sparkPlanInfo": {
            "nodeName": "Project",
            "children": [
                {
                    "nodeName": "Filter",
                    "children": [
                        {
                            "nodeName": "Scan",
                            "children": [],
                        }
                    ],
                }
            ],
        }
    }

    fields = {path for path, _ in coverage_inventory.walk(plan)}

    assert "sparkPlanInfo.children.nodeName" in fields
    assert not any(".children.children." in field for field in fields)


def test_report_separates_evidence_categories(tmp_path):
    from tools import coverage_inventory

    log = write_log(
        tmp_path,
        "sample.ndjson",
        [
            {"Event": "SparkListenerApplicationStart", "App ID": "app-1"},
            {
                "Event": "SparkListenerTaskEnd",
                "Stage ID": 1,
                "Task Metrics": {"Executor CPU Time": 10},
            },
        ],
    )

    text = coverage_inventory.report(coverage_inventory.inventory([str(log)]))

    assert "## [C] Depende de configuracao ou runtime" in text
    assert "## [D] Nao observado neste corpus" in text
    assert "## [E] Ausente do event log padrao" in text
    assert "## [F] Inferivel, sem causalidade comprovada" in text
    assert "nao esta em log algum" not in text


def test_report_does_not_count_dynamic_keys_as_separate_fields(tmp_path):
    from tools import coverage_inventory

    log = write_log(
        tmp_path,
        "environment.ndjson",
        [
            {
                "Event": "SparkListenerEnvironmentUpdate",
                "Classpath Entries": {
                    f"/opt/spark/jars/lib-{index}.jar": "System Classpath"
                    for index in range(100)
                },
            }
        ],
    )

    result = coverage_inventory.inventory([str(log)])
    fields = {
        field
        for event_fields in result.by_event.values()
        for field in event_fields
    }

    assert len(fields) < 10
    assert "Classpath Entries.<entry>" in fields


def test_zero_metrics_do_not_count_as_exercised_scenarios(tmp_path):
    from tools import coverage_inventory

    log = write_log(
        tmp_path,
        "zero-signals.ndjson",
        [
            {"Event": "SparkListenerApplicationStart", "App ID": "app-1"},
            {
                "Event": "SparkListenerStageSubmitted",
                "Stage Info": {"Stage Attempt ID": 0},
            },
            {
                "Event": "SparkListenerTaskEnd",
                "Task Info": {"Attempt": 0},
                "Task End Reason": {"Reason": "Success"},
                "Task Metrics": {
                    "Memory Bytes Spilled": 0,
                    "Disk Bytes Spilled": 0,
                },
            },
        ],
    )

    text = coverage_inventory.report(coverage_inventory.inventory([str(log)]))

    assert "spill efetivo (> 0)" in text
    assert "falha, retry ou tentativa especulativa real" in text


def test_validation_architecture_keeps_required_views():
    doc = (
        ROOT
        / "docs"
        / "architecture"
        / "validation-evidence-flow.md"
    ).read_text(encoding="utf-8")

    required_sections = [
        "## Fluxo de validacao",
        "## Arquitetura proposta",
        "## Diagrama de sequencia",
        "## Cadeia de valor",
        "## Gargalos e pontos de ruptura",
    ]

    for section in required_sections:
        assert section in doc
    assert doc.count("```mermaid") >= 5

    required_validation_concepts = [
        "Attempts efetivos e zeros",
        "applicationId e leitura incremental",
        "Sintetico preserva estrutura observada?",
        "fidelidade apenas agregada",
        "saida ASCII portavel",
    ]
    for concept in required_validation_concepts:
        assert concept in doc
