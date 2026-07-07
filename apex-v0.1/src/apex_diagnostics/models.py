from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

SEVERITY_RANK = {"info": 0, "warning": 1, "critical": 2}


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Finding(BaseModel):
    detector: Literal["skew", "shuffle", "plans", "gc", "oom"]
    severity: Severity
    app_id: str
    stage_id: int | None = None
    execution_id: int | None = None
    title: str
    evidence: dict[str, float | int | str] = Field(default_factory=dict)


class Recommendation(BaseModel):
    conf_key: str
    suggested_value: str
    rationale: str
    related_stage_ids: list[int] = Field(default_factory=list)


class DiagnosticReport(BaseModel):
    app_id: str
    status: Literal["full", "detectors_only"]
    summary: str
    findings: list[Finding] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)

    def max_severity(self) -> str:
        if not self.findings:
            return "none"
        return max((f.severity.value for f in self.findings), key=SEVERITY_RANK.__getitem__)
