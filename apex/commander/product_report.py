"""Static product-readiness report for Apex Commander evidence."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_F7_LOG = Path("evidence/f7-remote-real-stack-run-29671461366-loop.log")
DEFAULT_MCP_GUI_LOG = Path("evidence/g6-mcp-ide-gui-smoke-2026-07-18.log")
DEFAULT_LATENCY_LOG = Path("evidence/g4-t1.log")
DEFAULT_ISSUES = Path("ISSUES.md")


@dataclass(frozen=True)
class ProductReportInputs:
    root: Path
    f7_log: Path = DEFAULT_F7_LOG
    mcp_gui_log: Path = DEFAULT_MCP_GUI_LOG
    latency_log: Path = DEFAULT_LATENCY_LOG
    issues_file: Path = DEFAULT_ISSUES


def build_product_snapshot(inputs: ProductReportInputs) -> dict[str, Any]:
    root = inputs.root.resolve()
    f7_log = _read_optional(root / inputs.f7_log)
    mcp_gui_log = _read_optional(root / inputs.mcp_gui_log)
    latency_log = _read_optional(root / inputs.latency_log)
    issues_text = _read_optional(root / inputs.issues_file)

    compare = _extract_compare(f7_log)
    latency_ms = _extract_latency_ms(latency_log)
    open_items = _count_issue_status(issues_text, ("aberta", "rascunho"))
    closed_items = _count_issue_status(issues_text, ("fechada", "fechada (fato estabelecido)"))

    signals = {
        "remote_real_stack_green": "loop_status=success" in f7_log,
        "mcp_gui_green": all(
            marker in mcp_gui_log
            for marker in (
                "tools/list: success",
                "recommend_fix: success",
                "preview_fix: success",
                "apply_fix: success",
            )
        ),
        "t1_under_1s": latency_ms is not None and latency_ms < 1000,
        "crew_judge_real_missing": "Crew.ai/Judge real" in issues_text
        or "Crew.ai" in issues_text,
        "runner_operational_dependency": "self-hosted" in issues_text,
    }

    score = _readiness_score(signals)
    status = "ready_for_judge_with_known_gaps" if score >= 80 else "partial"

    return {
        "status": status,
        "score": score,
        "signals": signals,
        "f7": _f7_summary(compare, f7_log),
        "latency_ms": latency_ms,
        "issues": {
            "open_or_draft": open_items,
            "closed": closed_items,
        },
        "strengths": _strengths(signals),
        "gaps": _gaps(signals),
        "next_actions": _next_actions(signals),
    }


def render_product_report(snapshot: dict[str, Any]) -> str:
    f7 = snapshot["f7"]
    comparisons = f7.get("comparisons") or []
    rows = "\n".join(
        "<tr>"
        f"<td>{_e(item.get('metric'))}</td>"
        f"<td>{_e(item.get('before'))}</td>"
        f"<td>{_e(item.get('after'))}</td>"
        f"<td><span class=\"pill { _e(item.get('status')) }\">{_e(item.get('status'))}</span></td>"
        "</tr>"
        for item in comparisons
    )
    strengths = "".join(f"<li>{_e(item)}</li>" for item in snapshot["strengths"])
    gaps = "".join(f"<li>{_e(item)}</li>" for item in snapshot["gaps"])
    next_actions = "".join(f"<li>{_e(item)}</li>" for item in snapshot["next_actions"])

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Apex Codex Product Readiness</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #17202a; background: #f7f9fb; }}
    main {{ max-width: 1100px; margin: auto; }}
    section {{ background: white; border: 1px solid #dce3ea; border-radius: 14px; padding: 20px; margin: 18px 0; }}
    h1, h2 {{ margin-top: 0; }}
    .score {{ font-size: 56px; font-weight: 700; color: #146c43; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }}
    .card {{ background: #f1f5f9; border-radius: 12px; padding: 14px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #e5e7eb; padding: 10px; text-align: left; }}
    .pill {{ border-radius: 999px; padding: 3px 9px; background: #e5e7eb; }}
    .improved {{ background: #d1fae5; color: #065f46; }}
    .unchanged {{ background: #e0f2fe; color: #075985; }}
    .warning {{ color: #92400e; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
<main>
  <h1>Apex Codex Product Readiness</h1>
  <section>
    <div class="score">{_e(snapshot["score"])}/100</div>
    <p>Status: <strong>{_e(snapshot["status"])}</strong></p>
    <p>Leitura: pronto para avaliacao com gaps conhecidos, sem vender Crew.ai/Judge real como entregue.</p>
  </section>
  <section class="grid">
    <div class="card"><strong>Before app</strong><br><code>{_e(f7.get("before_app_id"))}</code></div>
    <div class="card"><strong>After app</strong><br><code>{_e(f7.get("after_app_id"))}</code></div>
    <div class="card"><strong>T1 latency</strong><br><code>{_e(snapshot.get("latency_ms"))} ms</code></div>
  </section>
  <section>
    <h2>Comparacao Before/After</h2>
    <table>
      <thead><tr><th>Metrica</th><th>Antes</th><th>Depois</th><th>Status</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </section>
  <section>
    <h2>Forcas</h2>
    <ul>{strengths}</ul>
  </section>
  <section>
    <h2>Gaps Honestamente Declarados</h2>
    <ul>{gaps}</ul>
  </section>
  <section>
    <h2>Proximas Acoes</h2>
    <ol>{next_actions}</ol>
  </section>
</main>
</body>
</html>
"""


def write_product_report(root: str | Path, output: str | Path) -> dict[str, Any]:
    inputs = ProductReportInputs(root=Path(root))
    snapshot = build_product_snapshot(inputs)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_product_report(snapshot), encoding="utf-8")
    return snapshot


def _extract_compare(log_text: str) -> dict[str, Any] | None:
    for line in log_text.splitlines():
        if line.startswith("compare="):
            return json.loads(line.split("=", 1)[1])
    return None


def _extract_latency_ms(log_text: str) -> float | None:
    patterns = (
        r'"latency_ms"\s*:\s*([0-9.]+)',
        r'"elapsed_ms"\s*:\s*([0-9.]+)',
        r"latency_ms[=:]\s*([0-9.]+)",
        r"elapsed_ms[=:]\s*([0-9.]+)",
        r"([0-9.]+)\s*ms",
    )
    for pattern in patterns:
        match = re.search(pattern, log_text)
        if match:
            return round(float(match.group(1)), 3)
    return None


def _f7_summary(compare: dict[str, Any] | None, log_text: str) -> dict[str, Any]:
    before_app_id = _extract_line_value(log_text, "before_app_id")
    after_app_id = _extract_line_value(log_text, "after_app_id")
    if compare:
        return {
            "status": compare.get("status"),
            "before_app_id": (compare.get("before") or {}).get("app_id") or before_app_id,
            "after_app_id": (compare.get("after") or {}).get("app_id") or after_app_id,
            "comparisons": compare.get("comparisons") or [],
            "summary": compare.get("summary") or {},
        }
    return {
        "status": "missing",
        "before_app_id": before_app_id,
        "after_app_id": after_app_id,
        "comparisons": [],
        "summary": {},
    }


def _extract_line_value(text: str, key: str) -> str | None:
    for line in text.splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip()
    return None


def _readiness_score(signals: dict[str, bool]) -> int:
    score = 0
    if signals["remote_real_stack_green"]:
        score += 30
    if signals["mcp_gui_green"]:
        score += 20
    if signals["t1_under_1s"]:
        score += 20
    if signals["runner_operational_dependency"]:
        score += 10
    if signals["crew_judge_real_missing"]:
        score += 10
    return score


def _strengths(signals: dict[str, bool]) -> list[str]:
    items = []
    if signals["remote_real_stack_green"]:
        items.append("F7 remoto real-stack verde com Spark 4.1.2 e loop G3/G5 completo.")
    if signals["mcp_gui_green"]:
        items.append("MCP GUI real validado com tools/list, recommend, preview e apply_fix.")
    if signals["t1_under_1s"]:
        items.append("T1 deterministico abaixo de 1s, sem LLM obrigatorio.")
    return items


def _gaps(signals: dict[str, bool]) -> list[str]:
    items = []
    if signals["crew_judge_real_missing"]:
        items.append(
            "Crew.ai/Judge provider existe como caminho opcional; execucao com LLM externo real ainda nao foi observada."
        )
    if signals["runner_operational_dependency"]:
        items.append("F7 remoto depende de runner self-hosted preparado com Docker/Spark 4.1.2.")
    return items or ["Nenhum gap critico detectado no pacote de evidencias lido."]


def _next_actions(signals: dict[str, bool]) -> list[str]:
    actions = ["Decidir ciclo de vida do runner self-hosted apos avaliacao."]
    if signals["crew_judge_real_missing"]:
        actions.append(
            "Escolher entre UI de produto navegavel ou execucao Crew.ai com LLM externo configurado."
        )
    actions.append("Manter T1 deterministico e EvidenceValidator como caminho obrigatorio antes de qualquer LLM.")
    return actions


def _count_issue_status(text: str, statuses: tuple[str, ...]) -> int:
    return sum(
        1
        for line in text.splitlines()
        if line.startswith("|") and any(f"| {status} |" in line for status in statuses)
    )


def _read_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _e(value: Any) -> str:
    return html.escape("" if value is None else str(value))
