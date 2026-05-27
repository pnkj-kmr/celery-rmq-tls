#!/usr/bin/env bash
# End-to-end smoke test: certs -> broker up -> worker -> client -> assert files -> teardown
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY=".venv/bin/python"
CELERY=".venv/bin/celery"
COMPOSE="docker compose -f docker/docker-compose.yml"

cleanup() {
  echo "--- cleanup ---"
  if [[ -n "${WORKER_PID:-}" ]] && kill -0 "$WORKER_PID" 2>/dev/null; then
    kill "$WORKER_PID" 2>/dev/null || true
    wait "$WORKER_PID" 2>/dev/null || true
  fi
  $COMPOSE down -v >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "--- 1/5 generating certs ---"
./docker/gen-certs.sh

echo "--- 2/5 starting broker ---"
$COMPOSE up -d
for i in $(seq 1 30); do
  status=$(docker inspect -f '{{.State.Health.Status}}' celery-rmq-tls 2>/dev/null || echo "starting")
  if [[ "$status" == "healthy" ]]; then break; fi
  sleep 2
done
if [[ "$status" != "healthy" ]]; then
  echo "Broker did not become healthy." >&2
  exit 1
fi

echo "--- 3/5 clearing previous results and starting worker ---"
rm -f result/notification/*.json 2>/dev/null || true
mkdir -p result/notification
$CELERY -A celery_app.app worker -Q notification -l INFO >/tmp/celery-smoke-worker.log 2>&1 &
WORKER_PID=$!
sleep 3
if ! kill -0 "$WORKER_PID" 2>/dev/null; then
  echo "Worker failed to start. Log:" >&2
  cat /tmp/celery-smoke-worker.log >&2
  exit 1
fi

echo "--- 4/5 publishing 3 tasks ---"
$PY client.py --count 3 --message "smoke"

echo "--- 5/5 asserting 3 result files appear (timeout 15s) ---"
for i in $(seq 1 15); do
  count=$(ls result/notification/message_*.json 2>/dev/null | wc -l | tr -d ' ')
  echo "  [$i] files=$count"
  if [[ "$count" -ge 3 ]]; then
    echo "SMOKE PASS: $count files written"
    exit 0
  fi
  sleep 1
done

echo "SMOKE FAIL: expected 3 files, found $count" >&2
echo "--- worker log ---" >&2
tail -50 /tmp/celery-smoke-worker.log >&2
exit 1
