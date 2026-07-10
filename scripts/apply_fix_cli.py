#!/usr/bin/env python3
"""
apply_fix (CLI) — "aplica nossa sugestao" fora do IDE. [G5]

Mesmo caminho da tool MCP apply_fix (v1-skeleton/mcp/server.py): le o finding
mais recente do ClickHouse, pede ao Claude o codigo corrigido, salva backup e
mostra o diff. Use --dry-run para ver o diff sem tocar no arquivo.

Uso:
    python scripts/apply_fix_cli.py --app-id <app_id> --file demo_job.py [--dry-run]

Env: APEX_CH_HOST/PORT/USER/PASSWORD + ANTHROPIC_API_KEY
"""
import argparse
import datetime
import difflib
import os
import shutil
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--app-id", required=True)
    p.add_argument("--file", required=True, help="arquivo PySpark a corrigir")
    p.add_argument("--dry-run", action="store_true", help="so mostra o diff, nao altera o arquivo")
    args = p.parse_args()

    import clickhouse_connect
    ch = clickhouse_connect.get_client(
        host=os.getenv("APEX_CH_HOST", "localhost"),
        port=int(os.getenv("APEX_CH_PORT", "28123")),
        username=os.getenv("APEX_CH_USER", "spv0"),
        password=os.getenv("APEX_CH_PASSWORD", "spv0clickhouse123"))
    rows = list(ch.query("""
        SELECT pattern, severity, confidence, root_cause, recommendation
        FROM apex.findings WHERE app_id = {app_id:String}
        ORDER BY created_at DESC LIMIT 1
    """, parameters={"app_id": args.app_id}).named_results())
    if not rows:
        sys.exit(f"Sem finding para {args.app_id}. Rode crew_diagnose primeiro.")
    finding = rows[0]
    print(f"finding: {finding['pattern']} | {finding['severity']} | confidence={finding['confidence']}")

    original_code = open(args.file, encoding="utf-8").read()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY nao configurada.")
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=4096,
        messages=[{"role": "user", "content": (
            f"Você é um Spark performance engineer. Aplique o fix abaixo no código PySpark.\n\n"
            f"DIAGNÓSTICO: padrão={finding['pattern']} | severidade={finding['severity']}\n"
            f"CAUSA RAIZ: {finding['root_cause']}\n"
            f"RECOMENDAÇÃO: {finding['recommendation']}\n\n"
            f"CÓDIGO ({args.file}):\n```python\n{original_code}\n```\n\n"
            f"Retorne APENAS o código corrigido, sem markdown fences."
        )}])
    fixed_code = msg.content[0].text.strip()
    if fixed_code.startswith("```"):
        lines = fixed_code.split("\n")
        fixed_code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    diff = "".join(difflib.unified_diff(
        original_code.splitlines(keepends=True), fixed_code.splitlines(keepends=True),
        fromfile=f"{args.file} (original)", tofile=f"{args.file} (apex fix)")) or "(sem alteracoes)"

    if args.dry_run:
        print(f"\nDRY RUN — diff ({finding['pattern']}):\n\n{diff}")
        return

    backup = args.file + f".apex_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(args.file, backup)
    with open(args.file, "w", encoding="utf-8") as f:
        f.write(fixed_code)
    print(f"\n✅ Fix aplicado — {finding['pattern']} ({finding['severity']})")
    print(f"Backup: {backup}\n\nDiff:\n{diff}")


if __name__ == "__main__":
    main()
