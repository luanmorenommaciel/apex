"""Execute the production dispatch slice with harmless handlers, never the package.

DryRun checks the Handler label. These tests independently check Command and its
arguments. PowerShell parses apex.ps1 without loading any product functions; only
the top-level action assignment and invocation are evaluated, after an allowlist
check. This proves routing, not Docker/Spark/ClickHouse behavior.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apex.ps1"
EXPECTED = {
    "bootstrap": ["Start-Package"],
    "doctor": ["Assert-Prerequisites", "Invoke-Doctor"],
    "smoke": ["Assert-Prerequisites", "Invoke-ProductGate:False"],
    "e2e": ["Assert-Prerequisites", "Invoke-ProductGate:True"],
    "tail-outlier": ["Assert-Prerequisites", "Invoke-TailOutlierGate"],
    "pilot-clean": ["Invoke-CleanPilot"],
    "status": ["Show-Status"],
    "down": ["Stop-Package"],
    "help": ["Show-Help"],
}

PROBE = r"""
param([string]$Source, [string]$Action)
$ErrorActionPreference = 'Stop'
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $Source, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw 'Package source has parse errors' }
$assignments = @($ast.EndBlock.Statements | Where-Object {
    $_ -is [System.Management.Automation.Language.AssignmentStatementAst] -and
    $_.Left -is [System.Management.Automation.Language.VariableExpressionAst] -and
    $_.Left.VariablePath.UserPath -eq 'actionPlan'
})
$invocations = @($ast.EndBlock.Statements | Where-Object {
    $_ -is [System.Management.Automation.Language.PipelineAst] -and
    $_.PipelineElements.Count -eq 1 -and
    $_.PipelineElements[0] -is [System.Management.Automation.Language.CommandAst] -and
    $_.PipelineElements[0].InvocationOperator -eq 'Ampersand' -and
    $_.PipelineElements[0].CommandElements.Count -eq 1 -and
    $_.PipelineElements[0].CommandElements[0].Extent.Text -eq '$actionPlan.Command'
})
if ($assignments.Count -ne 1 -or $invocations.Count -ne 1) {
    throw 'Expected one production action plan and one Command invocation'
}
$allowed = @('Start-Package', 'Assert-Prerequisites', 'Invoke-Doctor',
    'Invoke-ProductGate', 'Invoke-TailOutlierGate', 'Invoke-CleanPilot',
    'Show-Status', 'Stop-Package', 'Show-Help')
$calls = $assignments[0].FindAll({param($node)
    $node -is [System.Management.Automation.Language.CommandAst]
}, $true)
foreach ($call in $calls) {
    if ($call.GetCommandName() -notin $allowed -or
        $call.InvocationOperator -ne 'Unknown') {
        throw 'Dispatch contains a call outside the harmless handler allowlist'
    }
}
# These are all the functions available to the dispatch. Product functions were
# parsed as data above, never dot-sourced, so no prerequisites or services run.
$script:trace = [System.Collections.Generic.List[string]]::new()
function Start-Package { $script:trace.Add('Start-Package') }
function Assert-Prerequisites { $script:trace.Add('Assert-Prerequisites') }
function Invoke-Doctor { $script:trace.Add('Invoke-Doctor') }
function Invoke-ProductGate {
    param([switch]$Full)
    $script:trace.Add("Invoke-ProductGate:$Full")
}
function Invoke-TailOutlierGate { $script:trace.Add('Invoke-TailOutlierGate') }
function Invoke-CleanPilot { $script:trace.Add('Invoke-CleanPilot') }
function Show-Status { $script:trace.Add('Show-Status') }
function Stop-Package { $script:trace.Add('Stop-Package') }
function Show-Help { $script:trace.Add('Show-Help') }
. ([scriptblock]::Create($assignments[0].Extent.Text))
. ([scriptblock]::Create($invocations[0].Extent.Text))
ConvertTo-Json -Compress -InputObject @($script:trace.ToArray())
"""


def _probe(tmp_path: Path, action: str, source: Path = SCRIPT) -> subprocess.CompletedProcess:
    pwsh = shutil.which("pwsh")
    if not pwsh:
        pytest.fail("PowerShell 7 is required for command dispatch coverage")
    harness = tmp_path / "dispatch probe.ps1"
    harness.write_text(PROBE, encoding="utf-8")
    return subprocess.run(
        [pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(harness),
         "-Source", str(source), "-Action", action],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def _assert_dispatch(result: subprocess.CompletedProcess, action: str) -> None:
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == EXPECTED[action]


@pytest.mark.parametrize("action", EXPECTED)
def test_real_dispatch_invokes_expected_handlers(tmp_path: Path, action: str) -> None:
    _assert_dispatch(_probe(tmp_path, action), action)


@pytest.mark.parametrize(
    ("old", "new", "action"),
    [
        ("Command = { Start-Package }", "Command = { Show-Status }", "bootstrap"),
        ("Invoke-ProductGate -Full", "Invoke-ProductGate", "e2e"),
        ("Assert-Prerequisites; Invoke-Doctor", "Invoke-Doctor", "doctor"),
    ],
)
def test_probe_detects_command_regressions_with_unchanged_handler(
    tmp_path: Path, old: str, new: str, action: str,
) -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert source.count(old) == 1
    mutated = tmp_path / "mutated package.ps1"
    mutated.write_text(source.replace(old, new), encoding="utf-8")
    # A mislabeled route, missing argument or skipped prerequisite must fail
    # the same assertion used by the positive tests, not merely change a label.
    result = _probe(tmp_path, action, mutated)
    assert result.returncode == 0, result.stderr
    with pytest.raises(AssertionError):
        _assert_dispatch(result, action)


def test_probe_refuses_calls_outside_harmless_handlers(tmp_path: Path) -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    mutated = tmp_path / "refused package.ps1"
    mutated.write_text(
        source.replace("Command = { Start-Package }", "Command = { docker info }"),
        encoding="utf-8",
    )
    result = _probe(tmp_path, "bootstrap", mutated)
    assert result.returncode != 0
    assert "outside the harmless handler allowlist" in result.stderr
