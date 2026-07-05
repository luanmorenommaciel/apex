"""
Testes end-to-end do crew_diagnose.py com mock (sem API real).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-test-fake'

from unittest.mock import patch, MagicMock
from analysis.crew_diagnose import diagnose, _validate_against_contract

SKEW_FINDING = {
    "pattern": "skew",
    "severity": "high",
    "confidence": 0.87,
    "bottleneck_stage_id": 2,
    "root_cause": "HOT_KEY possui 4x mais registros, causando skew no stage 2",
    "recommendation": "Use salting: df.withColumn('salt', (rand()*10).cast(IntegerType())).repartition(20)",
    "evidence": {
        "key_metric": "max_task_ms / avg_task_ms",
        "key_value": "8.5",
        "expected_value": "< 3.0"
    }
}


def make_mock_crew(raw_output: str):
    mock_output = MagicMock()
    mock_output.raw = raw_output
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = mock_output
    return mock_crew_instance


def test_10_end_to_end_skew():
    print("=== TESTE 10: End-to-end mock (skew) ===")
    raw = json.dumps(SKEW_FINDING)

    with patch('analysis.crew_diagnose.Crew') as MockCrew:
        MockCrew.return_value = make_mock_crew(raw)
        finding = diagnose('app-20260704-skew-001', model='claude-sonnet-4-6')

    assert finding['pattern'] == 'skew',             f"Expected skew, got {finding['pattern']}"
    assert finding['severity'] == 'high',             f"Expected high, got {finding['severity']}"
    assert finding['confidence'] == 0.87
    assert finding['needs_judge'] == False
    assert finding['bottleneck_stage_id'] == 2
    assert finding['app_id'] == 'app-20260704-skew-001'
    assert finding['pipeline'] == 'crewai-1x'
    print(f"PASS: pattern={finding['pattern']}, confidence={finding['confidence']}, needs_judge={finding['needs_judge']}")


def test_11_markdown_fence_stripping():
    print("=== TESTE 11: JSON com markdown fences ===")
    raw = "```json\n" + json.dumps(SKEW_FINDING) + "\n```"

    with patch('analysis.crew_diagnose.Crew') as MockCrew:
        MockCrew.return_value = make_mock_crew(raw)
        finding = diagnose('app-fence-test', model='claude-sonnet-4-6')

    assert finding['pattern'] == 'skew'
    print(f"PASS: markdown fence stripped corretamente — pattern={finding['pattern']}")


def test_12_low_confidence_needs_judge():
    print("=== TESTE 12: Confidence < 0.6 → needs_judge ===")
    low_conf = {
        "pattern": "spill",
        "severity": "medium",
        "confidence": 0.42,
        "bottleneck_stage_id": 3,
        "root_cause": "Possível spill detectado, evidência limitada",
        "recommendation": "Aumente spark.executor.memory de 2g para 4g. Use repartition antes do join.",
        "evidence": {"key_metric": "disk_spill", "key_value": "150MB", "expected_value": "0"}
    }

    with patch('analysis.crew_diagnose.Crew') as MockCrew:
        MockCrew.return_value = make_mock_crew(json.dumps(low_conf))
        finding = diagnose('app-low-conf', model='claude-sonnet-4-6')

    assert finding['needs_judge'] == True
    assert 'judge_reason' in finding
    print(f"PASS: confidence=0.42 → needs_judge=True, reason={finding['judge_reason']}")


def test_13_invalid_json_regex_fallback():
    print("=== TESTE 13: JSON inválido → fallback regex ===")
    valid_json = json.dumps(SKEW_FINDING)
    raw_with_preamble = f"Aqui está o resultado da análise:\n\n{valid_json}\n\nEspero que ajude."

    with patch('analysis.crew_diagnose.Crew') as MockCrew:
        MockCrew.return_value = make_mock_crew(raw_with_preamble)
        finding = diagnose('app-regex-fallback', model='claude-sonnet-4-6')

    assert finding['pattern'] == 'skew'
    print(f"PASS: regex fallback extraiu JSON corretamente — pattern={finding['pattern']}")


def test_14_invalid_pattern_override():
    print("=== TESTE 14: Pattern inválido → override 'other' ===")
    bad_pattern = {**SKEW_FINDING, "pattern": "not_a_real_pattern"}

    with patch('analysis.crew_diagnose.Crew') as MockCrew:
        MockCrew.return_value = make_mock_crew(json.dumps(bad_pattern))
        finding = diagnose('app-bad-pattern', model='claude-sonnet-4-6')

    assert finding['pattern'] == 'other'
    print(f"PASS: padrão inválido → 'other'")


if __name__ == '__main__':
    tests = [
        test_10_end_to_end_skew,
        test_11_markdown_fence_stripping,
        test_12_low_confidence_needs_judge,
        test_13_invalid_json_regex_fallback,
        test_14_invalid_pattern_override,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as e:
            print(f"FAIL: {t.__name__} → {e}")
            failed += 1
    print()
    print(f"{'='*50}")
    print(f"{'TODOS OS TESTES PASSARAM' if failed == 0 else f'{failed} TESTE(S) FALHARAM'}")
    print(f"{'='*50}")
    sys.exit(failed)
