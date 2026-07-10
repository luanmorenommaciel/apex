#!/usr/bin/env python3
"""
Pattern Watcher (v4) — runner generico dos detectores deterministicos [G2 / ISSUE-A01].

Roda TODOS os detectores de apex/detectors.py sobre o event log e aplica o
acceptance do scenario:
- anti_pattern.class == none  -> verde se NENHUM finding warning/critical (G1 extendido)
- caso contrario              -> verde se o detector esperado disparou com a
                                 severidade minima declarada no acceptance.

Uso: pattern_watcher.py <scenario.yaml> <event-log.ndjson|.zstd|dir>
"""
import sys
import json
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apex import apexlib, detectors

SEV_ORDER = {"info": 0, "warning": 1, "critical": 2}


def main(scenario_path, log_path):
    scenario = yaml.safe_load(open(scenario_path))
    events = apexlib.read_events(log_path)

    try:
        h = apexlib.validate_provenance(events, scenario_path)
        if h:
            print(f"provenance: validada — hash {h}")
    except ValueError as e:
        print(f"\n❌ {e}")
        sys.exit(2)

    findings = detectors.run_all(events)
    print(json.dumps(findings, indent=2, ensure_ascii=False))
    print("\n--- ACCEPTANCE ---")

    klass = scenario.get("anti_pattern", {}).get("class", "none")
    acc = scenario.get("acceptance", {})

    if klass == "none":
        bad = [f for f in findings if SEV_ORDER[f["severity"]] >= SEV_ORDER["warning"]]
        if bad:
            print(f"❌ FALSO POSITIVO: {len(bad)} finding(s) >= warning em job saudavel: "
                  f"{[f['detector'] for f in bad]}. GATE VERMELHO.")
            sys.exit(1)
        print("✅ Baseline limpo em todos os detectores. GATE VERDE.")
        return

    expected_detector = acc["expected_detector"]
    min_severity = acc.get("min_severity", "warning")
    hits = [f for f in findings
            if f["detector"] == expected_detector
            and SEV_ORDER[f["severity"]] >= SEV_ORDER[min_severity]]
    if not hits:
        print(f"❌ Detector '{expected_detector}' NAO disparou >= {min_severity}. GATE VERMELHO.")
        sys.exit(1)
    terms = acc.get("title_includes", [])
    blob = " ".join(f["title"] for f in hits).lower()
    missing = [t for t in terms if t.lower() not in blob]
    if missing:
        print(f"❌ Finding nao menciona termos esperados: {missing}. GATE VERMELHO.")
        sys.exit(1)
    print(f"✅ '{expected_detector}' disparou {hits[0]['severity']} — {hits[0]['title']}. GATE VERDE.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: pattern_watcher.py <scenario.yaml> <event-log.ndjson|.zstd|dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
