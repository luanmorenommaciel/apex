# Spark Platform App Template

Use this template when creating a new Spark script under `src/apps`.

## Script Header

Every app script should start with a docstring that includes:

- Short job purpose.
- Manual `spark-submit` command.
- Execution sequence.
- Target entity/layer when applicable.

Example command shape. Assumes the Compose stack is already running:

```bash
docker exec -it spv0-spark-master \
  env PYTHONPATH=/opt/spark/src /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --conf spark.executorEnv.PYTHONPATH=/opt/spark/src \
  /opt/spark/src/apps/sample_scripts/<script_name>.py
```

## Job Contract

Use `SparkPlatJob` so config loading, logging, Spark session lifecycle, default read/write helpers, and clean shutdown are handled consistently.

```python
from spark_platform.jobs import SparkPlatJob
from spark_platform.utils.logger import logger


class ExampleJob(SparkPlatJob):
    app_name = "spark-plat-v0-example"
    entity_name = "customer"
    layer = "bronze"

    def extract(self):
        # Return a DataFrame. You can generate data or call self.read_dataset().
        return self.read_dataset()

    def transform(self, data):
        # Keep business logic here.
        return data

    def load(self, data) -> None:
        # Default SparkPlatJob.load(data) writes to entity/layer with write_dataset.
        self.write_dataset(data)
        logger.info("Example job completed write")


def main() -> int:
    return ExampleJob().run()


if __name__ == "__main__":
    raise SystemExit(main())
```

## Rules

- Do not use `collect()`, `toPandas()`, `show()`, or broad `take()` in normal jobs.
- Do not use `orderBy()` unless the output contract explicitly requires sorted rows.
- Use `logger`, not `print`.
- Put the Spark app name in the runner script, not in YAML.
- Keep transformation logic in `transform()` when possible.
- Use `self.read_dataset()` and `self.write_dataset()` for configured entity/layer IO.
- Spark physical plans should come from event logs and ClickHouse, not driver debug output.
- Prefer DataFrame APIs over SQL strings for app smoke examples.

## Transform Styles

Both styles below are valid. Prefer `.transform(...)` when the transformation is reusable, named, or likely to be tested directly.

### Without `.transform(...)`

```python
def transform(self, data):
    return data.groupBy("country").agg(
        F.count("*").alias("customer_count"),
        F.round(F.sum("lifetime_value"), 2).alias("total_lifetime_value"),
    )
```

### With `.transform(...)`

```python
def build_country_summary(dataframe):
    return dataframe.groupBy("country").agg(
        F.count("*").alias("customer_count"),
        F.round(F.sum("lifetime_value"), 2).alias("total_lifetime_value"),
    )


class ExampleJob(SparkPlatJob):
    def transform(self, data):
        return data.transform(build_country_summary)
```

Do not add `orderBy()` to these examples unless the downstream output must be sorted. Sorting usually creates avoidable shuffle/cost and is not needed for event-log observability.
