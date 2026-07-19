"""Static, read-only Apex Commander UI built from local evidence files."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


DEFAULT_READINESS = Path("evidence/apex-product-readiness-2026-07-19-summary.json")
DEFAULT_TELEMETRY = Path("evidence/generated/mcp-ide-subprocess-smoke/store.ndjson")
DEFAULT_FINDINGS = Path("evidence/generated/mcp-ide-subprocess-smoke/findings.ndjson")
DEFAULT_JUDGE = Path("evidence/crew-judge-external-llm-success-final-2026-07-19.json")


def build_commander_ui_snapshot(
    root: str | Path,
    *,
    readiness_file: str | Path = DEFAULT_READINESS,
    telemetry_file: str | Path = DEFAULT_TELEMETRY,
    findings_file: str | Path = DEFAULT_FINDINGS,
    judge_file: str | Path = DEFAULT_JUDGE,
) -> dict[str, Any]:
    """Load only the approved local evidence sources into a UI-safe snapshot."""
    base = Path(root).resolve()
    readiness = _read_json(base / readiness_file)
    telemetry = _read_ndjson(base / telemetry_file)
    finding_records = _read_ndjson(base / findings_file)
    judge_payload = _read_json(base / judge_file)

    findings = [_ui_finding(item) for item in finding_records if isinstance(item, dict)]
    jobs = [_ui_job(item) for item in telemetry if isinstance(item, dict)]
    compare = readiness.get("f7", {}) if isinstance(readiness, dict) else {}

    return _scrub_sensitive(
        {
            "read_only": True,
            "overview": {
                "status": readiness.get("status", "not_available"),
                "score": readiness.get("score", 0),
                "latency_ms": readiness.get("latency_ms"),
                "before_app_id": compare.get("before_app_id"),
                "after_app_id": compare.get("after_app_id"),
                "strengths": readiness.get("strengths", []),
                "gaps": readiness.get("gaps", []),
            },
            "comparison": {
                "status": compare.get("status", "not_available"),
                "comparisons": compare.get("comparisons", []),
                "summary": compare.get("summary", {}),
            },
            "jobs": jobs,
            "findings": findings,
            "judge": _ui_judge(judge_payload),
            "fix_center": _fix_center(findings),
        }
    )


def render_commander_ui(snapshot: dict[str, Any]) -> str:
    """Render a self-contained HTML page; every external value is escaped."""
    overview = snapshot["overview"]
    navigation = "".join(
        f'<a href="#{anchor}">{label}</a>'
        for anchor, label in (
            ("overview", "Visao geral"),
            ("findings", "Findings"),
            ("telemetry", "Telemetria"),
            ("judge", "Crew/Judge"),
            ("compare", "Before/After"),
            ("fix-center", "Fix Center"),
        )
    )
    finding_rows = "".join(
        "<tr>"
        f"<td>{_e(finding.get('job_id'))}</td>"
        f"<td>{_e(finding.get('kind'))}</td>"
        f"<td>{_badge(finding.get('severity'))}</td>"
        f"<td>{_e(finding.get('confidence'))}</td>"
        f"<td>{_e(_compact_evidence(finding.get('evidence')))}</td>"
        "</tr>"
        for finding in snapshot["findings"]
    ) or '<tr><td colspan="5">Nenhum finding persistido.</td></tr>'
    job_rows = "".join(_job_row(job) for job in snapshot["jobs"]) or (
        '<tr><td colspan="8">Nenhuma telemetria disponivel.</td></tr>'
    )
    comparison_rows = "".join(
        "<tr>"
        f"<td>{_e(item.get('metric'))}</td>"
        f"<td>{_e(item.get('before'))}</td>"
        f"<td>{_e(item.get('after'))}</td>"
        f"<td>{_badge(item.get('status'))}</td>"
        "</tr>"
        for item in snapshot["comparison"]["comparisons"]
    ) or '<tr><td colspan="4">Comparacao indisponivel.</td></tr>'
    judge = snapshot["judge"]
    fix = snapshot["fix_center"]

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Apex Commander UI MVP</title>
  <style>
    :root {{ color-scheme: light; --ink:#172033; --muted:#526176; --line:#dce4ee; --bg:#f5f7fb; --card:#fff; --blue:#155eef; --good:#067647; --warn:#b54708; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; font:15px/1.5 Arial,sans-serif; color:var(--ink); background:var(--bg); }}
    header {{ background:#101828; color:#fff; padding:26px max(24px,calc((100% - 1180px)/2)); }} header p {{ color:#d0d5dd; margin:5px 0 0; }}
    nav {{ display:flex; flex-wrap:wrap; gap:8px; padding:14px max(24px,calc((100% - 1180px)/2)); background:#fff; border-bottom:1px solid var(--line); }} nav a {{ color:var(--blue); text-decoration:none; padding:5px 8px; }}
    main {{ max-width:1180px; margin:0 auto; padding:24px; }} section {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:20px; margin:16px 0; }}
    h1,h2,h3 {{ margin:0 0 10px; }} .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; }} .card {{ border:1px solid var(--line); border-radius:10px; padding:14px; }}
    .label {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }} .value {{ font-size:24px; font-weight:700; overflow-wrap:anywhere; }}
    table {{ width:100%; border-collapse:collapse; }} th,td {{ padding:10px; text-align:left; vertical-align:top; border-bottom:1px solid var(--line); overflow-wrap:anywhere; }} th {{ color:var(--muted); font-size:12px; text-transform:uppercase; }}
    .scroll {{ overflow-x:auto; }} .badge {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#e8eefc; color:#1849a9; font-weight:700; font-size:12px; }} .badge.improved,.badge.high,.badge.critical {{ background:#d1fadf; color:var(--good); }} .badge.warning,.badge.medium {{ background:#fef0c7; color:var(--warn); }}
    pre {{ white-space:pre-wrap; overflow-wrap:anywhere; background:#101828; color:#e4e7ec; padding:14px; border-radius:9px; }} ul {{ margin:8px 0; padding-left:20px; }} .notice {{ border-left:4px solid var(--blue); padding-left:12px; color:var(--muted); }}
  </style>
</head>
<body>
<header><h1>Apex Commander UI</h1><p>MVP local. Evidencia, recomendacao e preview sem acionar mutacoes.</p></header>
<nav>{navigation}</nav>
<main>
  <section id="overview"><h2>Visao Geral</h2><div class="grid">
    {_card('Status', overview.get('status'))}{_card('Score', f"{overview.get('score')}/100")}{_card('T1', _format_ms(overview.get('latency_ms')))}{_card('App antes', overview.get('before_app_id'))}{_card('App depois', overview.get('after_app_id'))}
  </div><h3>Forcas</h3>{_list(overview.get('strengths'))}<h3>Gaps declarados</h3>{_list(overview.get('gaps'))}</section>
  <section id="findings"><h2>Jobs e Findings</h2><div class="scroll"><table><thead><tr><th>Job</th><th>Tipo</th><th>Severidade</th><th>Confianca</th><th>Evidencia</th></tr></thead><tbody>{finding_rows}</tbody></table></div></section>
  <section id="telemetry"><h2>Telemetria por Stage</h2><div class="scroll"><table><thead><tr><th>Job</th><th>App</th><th>Stage</th><th>Tasks</th><th>Skew ratio</th><th>Disk spill</th><th>GC</th><th>Evidence</th></tr></thead><tbody>{job_rows}</tbody></table></div></section>
  <section id="judge"><h2>Crew/Judge</h2><div class="grid">{_card('Provider', judge.get('provider'))}{_card('Decisao', judge.get('decision'))}{_card('Status', judge.get('status'))}</div><h3>Rationale</h3><p>{_e(judge.get('rationale'))}</p><h3>Citacoes verificaveis</h3>{_list(judge.get('cited_evidence'))}<p class="notice">O Judge e read-only: nao aplica alteracoes e deve citar evidencia existente.</p></section>
  <section id="compare"><h2>Comparacao Before/After</h2><p>Status: {_badge(snapshot['comparison'].get('status'))}</p><div class="scroll"><table><thead><tr><th>Metrica</th><th>Antes</th><th>Depois</th><th>Resultado</th></tr></thead><tbody>{comparison_rows}</tbody></table></div></section>
  <section id="fix-center"><h2>Fix Center</h2><p class="notice">Demonstrativo e somente leitura. Esta tela nao chama MCP, nao cria approval token e nao modifica arquivos.</p><div class="grid">{_card('Recomendacao', fix.get('recommendation'))}{_card('Finding relacionado', fix.get('finding_kind'))}{_card('Estado do preview', fix.get('preview_status'))}</div><h3>Diff</h3><pre>{_e(fix.get('diff'))}</pre></section>
  <section id="live-demo"><h2>Demo MCP Segura</h2><p class="notice">Usa o contrato real de recomendacao e preview para o job de demonstracao. Nao aceita caminho livre, nao exibe approval token e nao chama apply_fix.</p><p><button id="load-recommendation" type="button">Carregar recomendacao real</button> <button id="load-preview" type="button">Gerar preview real</button></p><pre id="live-result">Aguardando uma acao read-only.</pre></section>
</main>
<script>
  const result = document.getElementById("live-result");
  async function loadDemo(endpoint) {{
    result.textContent = "Consultando Commander...";
    try {{
      const response = await fetch(endpoint, {{ method: "GET", cache: "no-store" }});
      const payload = await response.json();
      result.textContent = JSON.stringify(payload, null, 2);
    }} catch (error) {{
      result.textContent = "Nao foi possivel consultar a demo local: " + error.message;
    }}
  }}
  document.getElementById("load-recommendation").addEventListener("click", () => loadDemo("/api/recommendations"));
  document.getElementById("load-preview").addEventListener("click", () => loadDemo("/api/preview"));
</script>
</body>
</html>"""


def write_commander_ui(root: str | Path, output: str | Path) -> dict[str, Any]:
    snapshot = build_commander_ui_snapshot(root)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_commander_ui(snapshot), encoding="utf-8")
    return snapshot


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _read_ndjson(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _ui_job(envelope: dict[str, Any]) -> dict[str, Any]:
    stages = []
    for stage in envelope.get("stages", []):
        if isinstance(stage, dict):
            stages.append({key: stage.get(key) for key in (
                "stage_id", "task_count", "ratio", "disk_bytes_spilled", "memory_bytes_spilled",
                "jvm_gc_time_ms", "executor_run_time_ms", "evidence_status", "failure_reasons",
            )})
    return {"job_id": envelope.get("job_id"), "app_id": envelope.get("app_id"), "stages": stages}


def _ui_finding(record: dict[str, Any]) -> dict[str, Any]:
    finding = record.get("finding") or record
    return {
        "job_id": finding.get("job_id"), "kind": finding.get("kind") or finding.get("title"),
        "severity": finding.get("severity"), "confidence": finding.get("confidence"),
        "evidence": finding.get("evidence") or {}, "validated": bool((record.get("validation") or {}).get("accepted")),
    }


def _ui_judge(payload: dict[str, Any]) -> dict[str, Any]:
    decision = payload.get("crew_ai") or {}
    return {key: decision.get(key, "not_available") for key in ("provider", "decision", "status", "rationale", "cited_evidence")}


def _fix_center(findings: list[dict[str, Any]]) -> dict[str, str]:
    finding = findings[0] if findings else {}
    kind = finding.get("kind", "not_available")
    recommendation = "Review skew-safe join mitigation" if kind == "shuffle_skew_candidate" else "Manual review required"
    return {
        "finding_kind": str(kind), "recommendation": recommendation,
        "preview_status": "not_persisted_in_approved_sources",
        "diff": "No persisted preview diff is available in the approved local evidence. Use MCP preview_fix for an explicitly reviewed diff.",
    }


def _scrub_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _scrub_sensitive(item) for key, item in value.items() if not any(word in key.lower() for word in ("token", "secret", "password", "api_key", "authorization", "environment"))}
    if isinstance(value, list):
        return [_scrub_sensitive(item) for item in value]
    return value


def _job_row(job: dict[str, Any]) -> str:
    rows = []
    for stage in job.get("stages", []):
        rows.append("<tr>" + "".join(f"<td>{_e(value)}</td>" for value in (
            job.get("job_id"), job.get("app_id"), stage.get("stage_id"), stage.get("task_count"),
            stage.get("ratio"), stage.get("disk_bytes_spilled"), stage.get("jvm_gc_time_ms"), stage.get("evidence_status"),
        )) + "</tr>")
    return "".join(rows)


def _compact_evidence(evidence: Any) -> str:
    if not isinstance(evidence, dict):
        return ""
    return ", ".join(f"{key}={value}" for key, value in evidence.items())


def _card(label: str, value: Any) -> str:
    return f'<div class="card"><div class="label">{_e(label)}</div><div class="value">{_e(value)}</div></div>'


def _list(items: Any) -> str:
    values = items if isinstance(items, list) else []
    return "<ul>" + "".join(f"<li>{_e(item)}</li>" for item in values) + "</ul>"


def _badge(value: Any) -> str:
    text = "" if value is None else str(value)
    return f'<span class="badge {html.escape(text.lower(), quote=True)}">{_e(text)}</span>'


def _format_ms(value: Any) -> str:
    return f"{value} ms" if value not in (None, "") else "not_available"


def _e(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)
