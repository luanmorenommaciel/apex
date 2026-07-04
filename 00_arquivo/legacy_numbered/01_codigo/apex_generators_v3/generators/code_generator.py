#!/usr/bin/env python3
"""
Gerador de codigo (v3) — sentinela em vez de linha absoluta no contrato.

Mudanca vs v2: a linha do anti-pattern deixou de ser um INPUT fragil no scenario (que
quebrava o guard a cada mudanca de config). Agora e um OUTPUT derivado:
- o template marca o anti-pattern com um comentario-sentinela `# APEX::ANTIPATTERN`;
- o gerador acha a linha do sentinela apos renderizar (sempre correta por construcao);
- grava num manifesto `<job>.meta.json` (a coordenada que o CodeGrounder usa na Lane 2);
- se o scenario declarar uma linha esperada, AVISA na divergencia (nao derruba o build).
"""
import sys
import json
import yaml

SENTINEL = "# APEX::ANTIPATTERN"


def build_job_source(config):
    sid = config["scenario_id"]
    cfg = config["code_generator"]
    data = cfg["data"]
    conf = cfg.get("spark_config", {})
    conf_lines = "".join(f'    .config("{k}", "{v}")\n' for k, v in conf.items())

    header = f'''# Auto-gerado por code_generator v3 — scenario: {sid}
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, rand, when

spark = (SparkSession.builder.appName("{sid}")
{conf_lines}    .getOrCreate())

orders = spark.range({data['orders']['rows']}).select(
    (rand(42) * {data['orders']['distinct_keys']}).cast('int').alias('customer_id'),
    col('id').alias('order_id'))
orders = orders.withColumn('customer_id',
    when(rand(13) < {data['orders']['hot_share']}, {data['orders']['hot_key']}).otherwise(col('customer_id')))
customers = spark.range({data['customers']['rows']}).select(
    col('id').alias('customer_id'), col('id').alias('customer_name'))
'''
    body = f'''result = orders.join(customers.hint("shuffle_merge"), "customer_id", "inner")  {SENTINEL}
result.write.mode("overwrite").parquet("/tmp/apex_output")
spark.stop()
'''
    source = header + body
    line = next(i for i, l in enumerate(source.splitlines(), 1) if SENTINEL in l)
    return source, line


def generate_job(scenario_path, output_path):
    config = yaml.safe_load(open(scenario_path))
    source, actual_line = build_job_source(config)

    with open(output_path, "w") as f:
        f.write(source)

    # A linha e um OUTPUT derivado -> manifesto (usado na correlacao codigo<->log, Lane 2).
    manifest = {
        "scenario_id": config["scenario_id"],
        "job_file": output_path,
        "anti_pattern_line": actual_line,
        "anti_pattern_class": config["anti_pattern"]["class"],
    }
    meta_path = output_path.rsplit(".", 1)[0] + ".meta.json"
    with open(meta_path, "w") as f:
        json.dump(manifest, f, indent=2)

    declared = config["code_generator"].get("anti_pattern_line")
    if declared is not None and declared != actual_line:
        print(
            f"⚠️  scenario declara anti_pattern_line={declared}, mas caiu na {actual_line}. "
            f"Manifesto registra a linha real ({actual_line}); atualize o scenario se quiser.",
            file=sys.stderr,
        )
    print(f"✅ {output_path} gerado. Anti-pattern na linha {actual_line}. Manifesto: {meta_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: code_generator.py <scenario.yaml> <output_job.py>")
        sys.exit(1)
    generate_job(sys.argv[1], sys.argv[2])
