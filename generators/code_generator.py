#!/usr/bin/env python3
"""
Gerador de codigo (v4) — sentinela + cadeia de custodia.
[G1] Suporte a cenario baseline (anti_pattern.class: none) — sem injecao de hot key, sem sentinela.
"""
import sys
import json
import yaml
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apex import apexlib

SENTINEL = "# APEX::ANTIPATTERN"
GENERATOR_VERSION = "4"


def build_job_source(config):
    sid = config["scenario_id"]
    cfg = config["code_generator"]
    data = cfg["data"]
    conf = cfg.get("spark_config", {})
    conf_lines = "".join(f'    .config("{k}", "{v}")\n' for k, v in conf.items())

    baseline = config.get("anti_pattern", {}).get("class", "none") == "none"
    # [G1] baseline (class: none): sem injecao de hot key e sem sentinela — job saudavel
    skew_injection = "" if baseline else f'''orders = orders.withColumn('customer_id',
    when(rand(13) < {data['orders']['hot_share']}, {data['orders']['hot_key']}).otherwise(col('customer_id')))
'''
    join_suffix = "" if baseline else f"  {SENTINEL}"

    header = f'''# Auto-gerado por code_generator v4 — scenario: {sid}
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, rand, when

spark = (SparkSession.builder.appName("{sid}")
{conf_lines}    .getOrCreate())

orders = spark.range({data['orders']['rows']}).select(
    (rand(42) * {data['orders']['distinct_keys']}).cast('int').alias('customer_id'),
    col('id').alias('order_id'))
{skew_injection}customers = spark.range({data['customers']['rows']}).select(
    col('id').alias('customer_id'), col('id').alias('customer_name'))
'''
    body = f'''result = orders.join(customers.hint("shuffle_merge"), "customer_id", "inner"){join_suffix}
result.write.mode("overwrite").parquet("/tmp/apex_output")
spark.stop()
'''
    source = header + body
    line = None if baseline else next(i for i, l in enumerate(source.splitlines(), 1) if SENTINEL in l)
    return source, line


def generate_job(scenario_path, output_path):
    config = yaml.safe_load(open(scenario_path))
    source, actual_line = build_job_source(config)

    with open(output_path, "w") as f:
        f.write(source)

    manifest = {
        "scenario_id": config["scenario_id"],
        "scenario_hash": apexlib.compute_scenario_hash(scenario_path),
        "generator_version": GENERATOR_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "job_file": output_path,
        "anti_pattern_line": actual_line,
        "anti_pattern_class": config["anti_pattern"]["class"],
    }
    meta_path = output_path.rsplit(".", 1)[0] + ".meta.json"
    with open(meta_path, "w") as f:
        json.dump(manifest, f, indent=2)

    if actual_line is None:
        print(f"✅ {output_path} gerado (baseline, sem anti-pattern). Manifesto: {meta_path}")
        return

    declared = config["code_generator"].get("anti_pattern_line")
    if declared is not None and declared != actual_line:
        print(
            f"⚠️  scenario declara anti_pattern_line={declared}, mas caiu na {actual_line}. "
            f"Manifesto registra a linha real ({actual_line}).",
            file=sys.stderr,
        )
    print(f"✅ {output_path} gerado. Anti-pattern na linha {actual_line}. "
          f"Manifesto: {meta_path} (hash {manifest['scenario_hash']})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: code_generator.py <scenario.yaml> <output_job.py>")
        sys.exit(1)
    generate_job(sys.argv[1], sys.argv[2])
