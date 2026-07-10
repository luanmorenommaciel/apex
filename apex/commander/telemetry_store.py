"""Store-neutral telemetry query helpers."""

from apex.commander.clickstack_mvp import query_by_job_id as query_ndjson_by_job_id


def query_envelopes(store, job_id):
    if hasattr(store, "query_by_job_id"):
        return store.query_by_job_id(job_id)
    return query_ndjson_by_job_id(store, job_id)
