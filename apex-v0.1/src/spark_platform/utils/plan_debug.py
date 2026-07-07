"""
Notes for optional Spark physical-plan debugging.

The platform should not call this helper in normal smoke jobs. Spark SQL physical
plans are already emitted to Spark event logs. The supported observability path is:

Spark SQL execution -> Spark event logs -> `make spark-logs` -> ClickHouse
`spark_sql_executions.physical_plan` plus `spark_raw_events.raw`.

This commented helper is kept only as a reference for local script development,
when someone wants to inspect a formatted physical plan directly from a DataFrame.
It uses PySpark private JVM handles (`_sc`, `_jdf`), so it should not become part
of the stable public utility API without a stronger reason.

# def formatted_plan(dataframe) -> str:
#     return dataframe._sc._jvm.PythonSQLUtils.explainString(
#         dataframe._jdf.queryExecution(),
#         "formatted",
#     )
"""
