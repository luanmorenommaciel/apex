import json
from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field

from apex_diagnostics import detectors
from apex_diagnostics.clickhouse import CHClient
from apex_diagnostics.config import DiagnosticsThresholds


class DetectorToolInput(BaseModel):
    app_id: str = Field(description="Spark application id, e.g. app-20260706120000-0001")


class _DetectorTool(BaseTool):
    """Exposes one deterministic detector to the crew, built from a DetectorSpec.

    The LLM only chooses the app_id; the SQL is canned inside the detector
    layer (design layering rule: the crew never sees or writes SQL). Name,
    description and the detector call all come from the shared registry
    (detectors.DETECTORS), so the crew always sees exactly the detectors that
    run_all and the MCP server expose — no more 3-vs-5 drift.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    args_schema: Type[BaseModel] = DetectorToolInput
    client: Any
    thresholds: DiagnosticsThresholds
    spec: Any

    def _run(self, app_id: str) -> str:
        findings = self.spec.run(self.client, app_id, self.thresholds)
        return json.dumps([finding.model_dump() for finding in findings])


def build_detector_tools(client: CHClient, thresholds: DiagnosticsThresholds) -> list[BaseTool]:
    return [
        _DetectorTool(name=spec.name, description=spec.description, spec=spec, client=client, thresholds=thresholds)
        for spec in detectors.DETECTORS
    ]
