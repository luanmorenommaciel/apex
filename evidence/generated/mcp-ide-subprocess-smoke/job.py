# Smoke-only Spark job used by apex-commander IDE GUI validation.
# Safe AQE skew join mitigation preview.
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
