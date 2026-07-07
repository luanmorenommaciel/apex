from spark_platform.jobs import SparkPlatJob


class MinimalJob(SparkPlatJob):
    app_name = "unit-job"
    entity_name = "customer"
    layer = "bronze"

    def __init__(self):
        super().__init__()
        self.events = []

    def extract(self):
        self.events.append("extract")
        return "raw"

    def transform(self, data):
        self.events.append(("transform", data))
        return "transformed"

    def load(self, data):
        self.events.append(("load", data))


def test_spark_plat_job_runs_template_sequence(monkeypatch):
    stopped = []

    monkeypatch.setattr("spark_platform.jobs.base.load_config", lambda env=None: {"app": {"log_level": "INFO"}})
    monkeypatch.setattr(
        "spark_platform.jobs.base.SparkSessionFactory.get_or_create",
        lambda config, app_name: "spark-session",
    )
    monkeypatch.setattr("spark_platform.jobs.base.SparkSessionFactory.stop_active", lambda: stopped.append(True))

    job = MinimalJob()

    assert job.run() == 0
    assert job.spark == "spark-session"
    assert job.events == ["extract", ("transform", "raw"), ("load", "transformed")]
    assert stopped == [True]
