import base64
import json
from urllib.parse import parse_qs, urlparse

from apex.commander.clickhouse_http_client import ClickHouseHttpClient


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


class RecordingOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append({"request": request, "timeout": timeout})
        return FakeResponse(self.responses.pop(0))


def query_params(request):
    return parse_qs(urlparse(request.full_url).query)


def test_command_sends_sql_with_basic_auth():
    opener = RecordingOpener([b""])
    client = ClickHouseHttpClient(
        "http://clickhouse.local:8123",
        user="commander",
        password="secret",
        opener=opener,
        timeout=3,
    )

    client.command("SELECT 1")

    sent = opener.requests[0]
    request = sent["request"]
    assert sent["timeout"] == 3
    assert query_params(request)["query"] == ["SELECT 1"]
    expected = base64.b64encode(b"commander:secret").decode("ascii")
    assert request.headers["Authorization"] == f"Basic {expected}"


def test_insert_sends_json_each_row_body():
    opener = RecordingOpener([b""])
    client = ClickHouseHttpClient("http://clickhouse.local:8123", opener=opener)

    client.insert(
        "commander_telemetry",
        [("schema", "job-42")],
        column_names=("schema_version", "job_id"),
    )

    request = opener.requests[0]["request"]
    assert query_params(request)["query"] == [
        "INSERT INTO commander_telemetry (schema_version, job_id) FORMAT JSONEachRow"
    ]
    assert json.loads(request.data.decode("utf-8").strip()) == {
        "schema_version": "schema",
        "job_id": "job-42",
    }


def test_query_parses_json_each_row_response():
    body = b'{"envelope_json":"{\\"job_id\\": \\"job-42\\"}"}\n'
    opener = RecordingOpener([body])
    client = ClickHouseHttpClient("http://clickhouse.local:8123", opener=opener)

    result = client.query(
        "SELECT envelope_json FROM commander_telemetry WHERE job_id = {job_id:String}",
        parameters={"job_id": "job-42"},
    )

    request = opener.requests[0]["request"]
    params = query_params(request)
    assert params["param_job_id"] == ["job-42"]
    assert params["query"][0].endswith("FORMAT JSONEachRow")
    assert result.result_rows == [['{"job_id": "job-42"}']]
