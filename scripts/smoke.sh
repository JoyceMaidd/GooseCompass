#!/usr/bin/env bash
# Smoke test for GooseCompass — launches backend + frontend if needed,
# hits the health endpoint, sends a real RAG query, and takes a screenshot.
# Run from the repo root: bash .claude/skills/run-goosecompass/smoke.sh

set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
SCREENSHOT="${1:-/tmp/goosecompass-screenshot.png}"
BACKEND_URL="http://127.0.0.1:8000"
FRONTEND_URL="http://localhost:5174"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# ── 1. Load .env ──────────────────────────────────────────────────────────────
if [[ -f "$REPO/.env" ]]; then
  set -a; source "$REPO/.env"; set +a
else
  echo "ERROR: .env not found at $REPO/.env" >&2
  exit 1
fi

# ── 2. Start backend if not already running ───────────────────────────────────
if ! curl -sf "$BACKEND_URL/health" > /dev/null 2>&1; then
  echo "Starting backend..."
  cd "$REPO"
  uvicorn backend.api.app:app --host 127.0.0.1 --port 8000 &
  BACKEND_PID=$!
  for i in $(seq 1 15); do
    sleep 1
    curl -sf "$BACKEND_URL/health" > /dev/null 2>&1 && break
    if [[ $i -eq 15 ]]; then echo "ERROR: backend failed to start" >&2; exit 1; fi
  done
  echo "Backend started (PID $BACKEND_PID)"
else
  echo "Backend already running"
  BACKEND_PID=""
fi

# ── 3. Start frontend if not already running ──────────────────────────────────
if ! curl -sf "$FRONTEND_URL" > /dev/null 2>&1; then
  echo "Starting frontend..."
  cd "$REPO/frontend"
  npm run dev -- --host 127.0.0.1 &
  FRONTEND_PID=$!
  for i in $(seq 1 20); do
    sleep 1
    curl -sf "$FRONTEND_URL" > /dev/null 2>&1 && break
    if [[ $i -eq 20 ]]; then echo "ERROR: frontend failed to start" >&2; exit 1; fi
  done
  echo "Frontend started (PID $FRONTEND_PID)"
  cd "$REPO"
else
  echo "Frontend already running"
  FRONTEND_PID=""
fi

# ── 4. Health check ───────────────────────────────────────────────────────────
echo ""
echo "=== Health check ==="
HEALTH=$(curl -sf "$BACKEND_URL/health")
echo "$HEALTH"
[[ "$HEALTH" == '{"status":"ok"}' ]] || { echo "ERROR: unexpected health response" >&2; exit 1; }

# ── 5. RAG query (real pipeline: rewrite → embed → retrieve → generate) ───────
echo ""
echo "=== RAG query ==="
QUERY="What exchange programs are available at University of Waterloo?"
RESPONSE=$(curl -sf -X POST "$BACKEND_URL/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\"}")
echo "$RESPONSE" | python3 -m json.tool
# Verify response has the expected shape
echo "$RESPONSE" | python3 -c "
import json, sys
r = json.load(sys.stdin)
assert 'paragraphs' in r, 'missing paragraphs'
assert 'insufficient_context' in r, 'missing insufficient_context'
print(f'paragraphs: {len(r[\"paragraphs\"])}, insufficient_context: {r[\"insufficient_context\"]}')
"

# ── 6. Streaming endpoint smoke check ─────────────────────────────────────────
echo ""
echo "=== Streaming query (first 3 events) ==="
curl -sN -X POST "$BACKEND_URL/query/stream" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\"}" | head -3

# ── 7. Screenshot ─────────────────────────────────────────────────────────────
echo ""
echo "=== Screenshot → $SCREENSHOT ==="
"$CHROME" \
  --headless=new \
  --disable-gpu \
  --screenshot="$SCREENSHOT" \
  --window-size=1280,800 \
  "$FRONTEND_URL" 2>/dev/null
echo "Screenshot written to $SCREENSHOT"
[[ -s "$SCREENSHOT" ]] || { echo "ERROR: screenshot is empty" >&2; exit 1; }

echo ""
echo "All checks passed."
