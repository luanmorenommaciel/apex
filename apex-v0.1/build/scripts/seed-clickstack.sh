#!/usr/bin/env bash
# Seeds ClickStack (HyperDX) so `make compose` comes up ready:
#   1. Ensures the local account/team exists (registration also triggers the
#      DEFAULT_CONNECTIONS / DEFAULT_SOURCES auto-provisioning).
#   2. Ensures every source in build/config/clickstack/sources.json exists.
#   3. Ensures every dashboard in build/config/clickstack/dashboards/*.json
#      exists (matched by name; source names resolved to ids).
#   4. Ensures the local webhook channel and the alerts in
#      build/config/clickstack/alerts.json exist (attached to dashboard tiles).
# Idempotent by design; safe to run on every `make compose`.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
set -a
source .env.example
[[ -f .env ]] && source .env
set +a

BASE_URL="http://localhost:${HYPERDX_UI_PORT}"
EMAIL="${HYPERDX_SEED_EMAIL}"
PASSWORD="${HYPERDX_SEED_PASSWORD}"
JAR="$(mktemp)"
trap 'rm -f "${JAR}"' EXIT

# Wait until the API layer answers (not just the static frontend): right after
# `compose up` the app returns 504 from /api/* while it warms up.
for _ in $(seq 1 45); do
  probe=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 \
    -H 'Content-Type: application/json' -d '{}' "${BASE_URL}/api/login/password" || echo "000")
  case "${probe}" in
    000|502|503|504) sleep 2 ;;
    *) break ;;
  esac
done

register_status=$(curl -s -o /dev/null -w '%{http_code}' \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\",\"confirmPassword\":\"${PASSWORD}\"}" \
  "${BASE_URL}/api/register/password" || echo "000")
case "${register_status}" in
  200|302) echo "ClickStack: seed account created (${EMAIL})." ;;
  *)       echo "ClickStack: seed account present (register HTTP ${register_status})." ;;
esac

login_status=$(curl -s -c "${JAR}" -o /dev/null -w '%{http_code}' \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}" \
  "${BASE_URL}/api/login/password" || echo "000")
if [[ "${login_status}" != "302" && "${login_status}" != "200" ]]; then
  echo "ClickStack: WARN login failed (HTTP ${login_status}); seeding skipped. See docs/logs-info/clickstack-dashboards.md."
  exit 0
fi

HDX_BASE_URL="${BASE_URL}" HDX_JAR="${JAR}" python3 - <<'PYEOF'
import glob
import json
import os
import subprocess

BASE = os.environ["HDX_BASE_URL"]
JAR = os.environ["HDX_JAR"]


def api(path, payload=None, method=None):
    cmd = ["curl", "-s", "-b", JAR, "-H", "Content-Type: application/json"]
    if payload is not None:
        cmd += ["-d", json.dumps(payload)]
    if method:
        cmd += ["-X", method]
    out = subprocess.run(cmd + [BASE + path], capture_output=True, text=True).stdout
    try:
        parsed = json.loads(out or "{}")
    except json.JSONDecodeError:
        return {"_raw": out}
    return parsed


def items(resp):
    return resp.get("data", resp) if isinstance(resp, dict) else resp


def oid(doc):
    return doc.get("id") or doc.get("_id")


connections = items(api("/api/connections"))
if not connections:
    print("ClickStack: WARN no connection found; sources cannot be created.")
    raise SystemExit(0)
conn_id = oid(connections[0])

existing_sources = {s["name"]: oid(s) for s in items(api("/api/sources"))}
for spec in json.load(open("build/config/clickstack/sources.json")):
    if spec["name"] in existing_sources:
        continue
    spec = dict(spec, connection=conn_id)
    resp = api("/api/sources", spec)
    created = resp.get("data", resp)
    if isinstance(created, dict) and oid(created):
        existing_sources[spec["name"]] = oid(created)
        print(f"ClickStack: source '{spec['name']}' created.")
    else:
        print(f"ClickStack: WARN source '{spec['name']}' failed: {json.dumps(resp)[:160]}")

dashboards = {d["name"]: d for d in items(api("/api/dashboards"))}
cost_per_core_hour = os.environ.get("COST_PER_CORE_HOUR", "0.05")
for path in sorted(glob.glob("build/config/clickstack/dashboards/*.json")):
    dash = json.loads(open(path).read().replace("{{COST_PER_CORE_HOUR}}", cost_per_core_hour))
    ok = True
    for tile in dash["tiles"]:
        src = tile["config"]["source"]
        if src not in existing_sources:
            print(f"ClickStack: WARN dashboard '{dash['name']}' skipped (missing source '{src}').")
            ok = False
            break
        tile["config"]["source"] = existing_sources[src]
    if not ok:
        continue
    payload = {"name": dash["name"], "tiles": dash["tiles"], "tags": dash.get("tags", [])}
    existing = dashboards.get(dash["name"])
    if existing:
        if existing.get("tiles") == dash["tiles"]:
            continue
        resp = api(f"/api/dashboards/{oid(existing)}", payload, method="PATCH")
        action = "updated"
    else:
        resp = api("/api/dashboards", payload)
        action = "seeded"
    result = resp.get("data", resp)
    if isinstance(result, dict) and oid(result):
        dashboards[dash["name"]] = result
        print(f"ClickStack: dashboard '{dash['name']}' {action}.")
    else:
        print(f"ClickStack: WARN dashboard '{dash['name']}' {action} failed: {json.dumps(resp)[:200]}")

alert_specs = json.load(open("build/config/clickstack/alerts.json"))
webhooks = {w["name"]: oid(w) for w in items(api("/api/webhooks?service=slack")) if isinstance(w, dict) and "name" in w}
for name in {a["webhook"] for a in alert_specs}:
    if name not in webhooks:
        resp = api("/api/webhooks", {"name": name, "service": "slack", "url": "http://localhost:8000/local-alert-sink"})
        created = resp.get("data", resp)
        if isinstance(created, dict) and oid(created):
            webhooks[name] = oid(created)
            print(f"ClickStack: webhook '{name}' created (aponte para o seu Slack depois).")

existing_alerts = items(api("/api/alerts"))
alerted_tiles = set()
for alert in existing_alerts:
    dash_ref = alert.get("dashboard") or alert.get("dashboardId")
    if isinstance(dash_ref, dict):
        dash_ref = oid(dash_ref)
    alerted_tiles.add((dash_ref, alert.get("tileId") or alert.get("tile_id")))

for spec in alert_specs:
    dash = dashboards.get(spec["dashboard"])
    if not dash:
        print(f"ClickStack: WARN alert '{spec['name']}' skipped (dashboard missing).")
        continue
    key = (oid(dash), spec["tile"])
    if key in alerted_tiles:
        continue
    payload = {
        "source": "tile",
        "dashboardId": oid(dash),
        "tileId": spec["tile"],
        "threshold": spec["threshold"],
        "thresholdType": spec["threshold_type"],
        "interval": spec["interval"],
        "channel": {"type": "webhook", "webhookId": webhooks[spec["webhook"]]},
    }
    resp = api("/api/alerts", payload)
    created = resp.get("data", resp)
    if isinstance(created, dict) and oid(created):
        print(f"ClickStack: alert '{spec['name']}' seeded.")
    else:
        print(f"ClickStack: WARN alert '{spec['name']}' failed: {json.dumps(resp)[:300]}")
PYEOF
