"""Pure execution-to-stage attribution over normalized stage observations.

The v0.6 producer deliberately makes ``execution_id`` optional: an RDD or a
historical event has no SQL execution identity.  This module preserves that
absence rather than using a numeric sentinel, and leaves fetching/parsing the
observations to a later Engine-store integration.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum


class AttributionStatus(str, Enum):
    """The complete outcome set for a scoped execution lookup."""

    ATTRIBUTED = "attributed"
    EXECUTION_ID_ABSENT = "execution_id_absent"
    EXECUTION_ID_NOT_FOUND = "execution_id_not_found"
    CONFLICT = "conflict"


def _require_identity(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name}_required")


def _require_nonnegative_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name}_must_be_nonnegative_int")


@dataclass(frozen=True)
class StageExecutionObservation:
    """The identity-only projection of one completed stage observation."""

    app_id: str
    job_id: str
    stage_id: int
    stage_attempt: int
    execution_id: int | None

    def __post_init__(self) -> None:
        _require_identity(self.app_id, "app_id")
        _require_identity(self.job_id, "job_id")
        _require_nonnegative_int(self.stage_id, "stage_id")
        _require_nonnegative_int(self.stage_attempt, "stage_attempt")
        if self.execution_id is not None and (
            isinstance(self.execution_id, bool) or not isinstance(self.execution_id, int)
        ):
            raise ValueError("execution_id_must_be_int_or_none")


@dataclass(frozen=True)
class ExecutionStageRequest:
    """Exact application/job scope and SQL execution identity to resolve."""

    app_id: str
    job_id: str
    execution_id: int

    def __post_init__(self) -> None:
        _require_identity(self.app_id, "app_id")
        _require_identity(self.job_id, "job_id")
        if isinstance(self.execution_id, bool) or not isinstance(self.execution_id, int):
            raise ValueError("execution_id_must_be_int")


@dataclass(frozen=True)
class StageAttribution:
    """Deterministic attribution result; conflicts deliberately withhold IDs."""

    status: AttributionStatus
    stage_ids: tuple[int, ...] = ()
    conflicting_stage_ids: tuple[int, ...] = ()


def resolve_stage_ids(
    observations: Iterable[StageExecutionObservation],
    request: ExecutionStageRequest,
) -> StageAttribution:
    """Resolve one SQL execution to its exact distinct stages within one app/job.

    A retry is not a second membership: ``stage_attempt`` is retained on the
    observation for provenance but the result is keyed by ``stage_id``.  If a
    target stage carries another non-null execution identity in the same scope,
    the result is withheld rather than returning a potentially partial set.
    """

    scoped = [
        observation
        for observation in observations
        if observation.app_id == request.app_id and observation.job_id == request.job_id
    ]
    target_stage_ids = {
        observation.stage_id
        for observation in scoped
        if observation.execution_id == request.execution_id
    }

    if not target_stage_ids:
        status = (
            AttributionStatus.EXECUTION_ID_ABSENT
            if scoped and all(observation.execution_id is None for observation in scoped)
            else AttributionStatus.EXECUTION_ID_NOT_FOUND
        )
        return StageAttribution(status=status)

    conflicting_stage_ids = tuple(
        sorted(
            {
                observation.stage_id
                for observation in scoped
                if observation.stage_id in target_stage_ids
                and observation.execution_id is not None
                and observation.execution_id != request.execution_id
            }
        )
    )
    if conflicting_stage_ids:
        return StageAttribution(
            status=AttributionStatus.CONFLICT,
            conflicting_stage_ids=conflicting_stage_ids,
        )

    return StageAttribution(
        status=AttributionStatus.ATTRIBUTED,
        stage_ids=tuple(sorted(target_stage_ids)),
    )
