import pytest

from apex_engine.attribution import (
    AttributionStatus,
    ExecutionStageRequest,
    StageAttribution,
    StageExecutionObservation,
    resolve_stage_ids,
)


def observation(stage_id, attempt=0, execution_id=42, *, app_id="app-1", job_id="job-1"):
    return StageExecutionObservation(
        app_id=app_id,
        job_id=job_id,
        stage_id=stage_id,
        stage_attempt=attempt,
        execution_id=execution_id,
    )


def request(execution_id=42, *, app_id="app-1", job_id="job-1"):
    return ExecutionStageRequest(app_id=app_id, job_id=job_id, execution_id=execution_id)


def test_attributed_stages_are_sorted_distinct_across_attempts_and_duplicates():
    result = resolve_stage_ids(
        [
            observation(7, attempt=0),
            observation(2, attempt=0),
            observation(7, attempt=1),
            observation(2, attempt=0),
        ],
        request(),
    )

    assert result == StageAttribution(
        status=AttributionStatus.ATTRIBUTED,
        stage_ids=(2, 7),
    )


def test_foreign_application_with_same_job_cannot_bleed_into_result():
    result = resolve_stage_ids(
        [observation(8, app_id="other-app"), observation(3)],
        request(),
    )

    assert result.status is AttributionStatus.ATTRIBUTED
    assert result.stage_ids == (3,)


@pytest.mark.parametrize(
    "in_scope, expected",
    [
        ([observation(1, execution_id=None)], StageAttribution(AttributionStatus.EXECUTION_ID_ABSENT)),
        ([observation(1, execution_id=99)], StageAttribution(AttributionStatus.EXECUTION_ID_NOT_FOUND)),
        (
            [observation(1), observation(2), observation(1, attempt=1, execution_id=99)],
            StageAttribution(AttributionStatus.CONFLICT, conflicting_stage_ids=(1,)),
        ),
    ],
)
def test_foreign_application_and_job_rows_cannot_change_scoped_outcomes(in_scope, expected):
    foreign = [
        observation(20, execution_id=None, app_id="other-app"),
        observation(21, execution_id=42, app_id="other-app"),
        observation(22, execution_id=99, job_id="other-job"),
        observation(23, execution_id=None, job_id="other-job"),
    ]

    assert resolve_stage_ids(in_scope, request()) == expected
    assert resolve_stage_ids([*foreign, *in_scope], request()) == expected


@pytest.mark.parametrize(
    "in_scope, foreign, expected",
    [
        (
            [observation(1)],
            [
                observation(1, execution_id=99, app_id="other-app"),
                observation(1, execution_id=99, job_id="other-job"),
            ],
            StageAttribution(AttributionStatus.ATTRIBUTED, stage_ids=(1,)),
        ),
        (
            [observation(2, execution_id=99)],
            [
                observation(2, app_id="other-app"),
                observation(2, job_id="other-job"),
            ],
            StageAttribution(AttributionStatus.EXECUTION_ID_NOT_FOUND),
        ),
        (
            [observation(3), observation(3, attempt=1, execution_id=99), observation(4)],
            [
                observation(4, app_id="other-app"),
                observation(4, execution_id=99, app_id="other-app"),
                observation(4, job_id="other-job"),
                observation(4, execution_id=99, job_id="other-job"),
            ],
            StageAttribution(AttributionStatus.CONFLICT, conflicting_stage_ids=(3,)),
        ),
        (
            [],
            [
                observation(5, execution_id=None, app_id="other-app"),
                observation(5, execution_id=None, job_id="other-job"),
            ],
            StageAttribution(AttributionStatus.EXECUTION_ID_NOT_FOUND),
        ),
    ],
)
def test_foreign_scope_collisions_cannot_change_attribution_outcomes(in_scope, foreign, expected):
    assert resolve_stage_ids([*foreign, *in_scope], request()) == expected


def test_all_optional_execution_ids_absent_is_explicit_not_a_sentinel():
    result = resolve_stage_ids(
        [observation(2, execution_id=None), observation(7, execution_id=None)],
        request(),
    )

    assert result == StageAttribution(status=AttributionStatus.EXECUTION_ID_ABSENT)


@pytest.mark.parametrize(
    "observations",
    [[], [observation(2, execution_id=99)]],
)
def test_missing_scope_or_other_present_execution_is_not_found(observations):
    result = resolve_stage_ids(observations, request())

    assert result == StageAttribution(status=AttributionStatus.EXECUTION_ID_NOT_FOUND)


def test_conflicting_non_null_mapping_withholds_partial_attribution():
    result = resolve_stage_ids(
        [observation(2, execution_id=42), observation(3, execution_id=42), observation(2, attempt=1, execution_id=99)],
        request(),
    )

    assert result == StageAttribution(
        status=AttributionStatus.CONFLICT,
        conflicting_stage_ids=(2,),
    )


def test_missing_observation_does_not_conflict_with_present_target_identity():
    result = resolve_stage_ids(
        [observation(2, execution_id=42), observation(2, attempt=1, execution_id=None)],
        request(),
    )

    assert result.status is AttributionStatus.ATTRIBUTED
    assert result.stage_ids == (2,)


def test_none_mixed_with_non_target_identity_is_not_found():
    result = resolve_stage_ids(
        [observation(2, execution_id=None), observation(7, execution_id=99)],
        request(),
    )

    assert result == StageAttribution(status=AttributionStatus.EXECUTION_ID_NOT_FOUND)


def test_zero_is_a_real_execution_identity():
    result = resolve_stage_ids([observation(2, execution_id=0)], request(0))

    assert result.status is AttributionStatus.ATTRIBUTED
    assert result.stage_ids == (2,)


@pytest.mark.parametrize(
    "factory",
    [
        lambda: StageExecutionObservation("", "job", 0, 0, None),
        lambda: StageExecutionObservation("app", "", 0, 0, None),
        lambda: StageExecutionObservation("app", "job", -1, 0, None),
        lambda: StageExecutionObservation("app", "job", 0, -1, None),
        lambda: ExecutionStageRequest("", "job", 0),
        lambda: ExecutionStageRequest("app", "", 0),
    ],
)
def test_invalid_observation_or_request_is_rejected(factory):
    with pytest.raises(ValueError):
        factory()
