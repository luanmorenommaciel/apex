"""Testes da composicao V1 — EvidenceValidator (kimi-Py) + telemetria job_id (codex)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from apex import evidence_validator as ev, telemetry  # noqa: E402


def tasks(n=8, dur=100, recs=50, jitter=True):
    return [{"duration_ms": dur + (i if jitter else 0),
             "shuffle_records": recs + (i if jitter else 0)} for i in range(n)]


# ---------------- EvidenceValidator (7 regras) ----------------
def test_validator_bundle_saudavel_7de7():
    r = ev.validate_rows([{"stage_id": 4, "num_tasks": 8}], {4: tasks()})
    assert r["status"] == "valid" and r["passed"] == 7


def test_validator_bundle_vazio_invalido():
    r = ev.validate_rows([], {})
    assert r["status"] == "invalid"
    assert any(x["rule"] == "R1_provenance" and x["status"] == "invalid" for x in r["rules"])


def test_validator_colapso_invalido():
    # 1 task = colapso (a regra que teria pego o bug historico do ratio 15392x)
    r = ev.validate_rows([{"stage_id": 4, "num_tasks": 8}], {4: tasks(n=1)})
    assert r["status"] == "invalid"
    assert any(x["rule"] == "R5_distribution" and x["status"] == "invalid" for x in r["rules"])


def test_validator_variancia_zero_indeterminado():
    r = ev.validate_rows([{"stage_id": 4, "num_tasks": 8}], {4: tasks(jitter=False)})
    assert r["status"] == "indeterminate"
    assert any(x["rule"] == "R4_correlation" and x["status"] == "indeterminate" for x in r["rules"])


def test_validator_multiplos_apps_invalido():
    r = ev.validate_rows([{"stage_id": 4, "num_tasks": 8}], {4: tasks()},
                         app_ids=["app-1", "app-2"])
    assert any(x["rule"] == "R7_single_app" and x["status"] == "invalid" for x in r["rules"])


# ---------------- Telemetria job_id (contrato codex) ----------------
def test_job_id_prefere_app_id():
    assert telemetry.infer_job_id([{"App ID": "app-9"}, {"Job ID": 3}]) == "app-9"


def test_job_id_fallback_spark_job():
    assert telemetry.infer_job_id([{"Job ID": 3}]) == "spark-job-3"


def test_job_id_fallback_local():
    assert telemetry.infer_job_id([{"Event": "x"}]) == "local-job"


def test_envelope_estrutura():
    evs = [{"Event": "SparkListenerApplicationStart", "App ID": "app-1"},
           {"Event": "SparkListenerTaskEnd", "Stage ID": 2, "Task Info": {"Task ID": 0},
            "Task Metrics": {"Executor Run Time": 10,
                             "Shuffle Read Metrics": {"Total Records Read": 5}}}]
    env = telemetry.build_envelope(evs)
    assert env["schema_version"] == "apex.telemetry.v1"
    assert env["job_id"] == "app-1" and env["stages"][0]["stage_id"] == 2


# ---------------- Integracao: validator bloqueia T1 ----------------
def test_t1_bloqueia_diagnostico_com_evidencia_invalida(monkeypatch):
    sys.path.insert(0, str(ROOT / "v1-skeleton" / "analysis"))
    import t1_triage
    # bundle colapsado (1 task) -> validator INVALID -> zero findings
    monkeypatch.setattr(t1_triage, "fetch_rows",
                        lambda app_id: ([{"stage_id": 4, "num_tasks": 8,
                                          "failed_tasks": 0, "duration_ms": 20000,
                                          "input_bytes": 0, "shuffle_read": 0,
                                          "shuffle_write": 0, "memory_spill": 0,
                                          "disk_spill": 0, "gc_time_ms": 9000}],
                                        {4: [{"duration_ms": 20000, "shuffle_records": 999999}]}))
    findings, _ = t1_triage.triage("app-x")
    assert findings == []  # gc 45% + "skew" gigante, mas evidencia colapsada: bloqueado
