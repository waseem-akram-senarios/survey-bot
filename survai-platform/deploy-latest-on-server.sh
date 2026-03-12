#!/bin/bash
# Deploy latest code on this server (54.86.65.150:8080)
# Run this script ON the server after: ssh ubuntu@54.86.65.150
#
# Usage (on server):
#   cd survey-bot/survai-platform && chmod +x deploy-latest-on-server.sh && ./deploy-latest-on-server.sh

set -e
BASE_URL="http://54.86.65.150:8080"

# Find platform dir (script lives in survai-platform)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  Deploy latest to $BASE_URL"
echo "=========================================="

# If we're in a git repo, pull latest
if [ -d "../.git" ]; then
  echo "[1/4] Pulling latest code (main)..."
  git -C .. pull origin main
else
  echo "[1/4] No .git in parent; using current files"
fi

export VITE_SERVER_URL="${BASE_URL}/pg"
export VITE_RECIPIENT_URL="${BASE_URL}"
export NEXT_PUBLIC_API_BASE_URL="${BASE_URL}"
export PUBLIC_URL="${BASE_URL}"
export GATEWAY_PORT="${GATEWAY_PORT:-8080}"

echo ""
echo "[2/4] Building and starting services..."
docker compose -f docker-compose.microservices.yml up -d --build

echo ""
echo "[3/4] Waiting 30s for services..."
sleep 30

echo ""
echo "[4/4] Health check..."
if curl -sf -m 10 "http://127.0.0.1:8080/health" >/dev/null; then
  echo "  ✅ Gateway OK"
else
  echo "  ⚠️  Gateway not responding yet"
fi
if curl -sf -m 10 "http://127.0.0.1:8080/pg/api/health" >/dev/null; then
  echo "  ✅ API OK"
else
  echo "  ⚠️  API not responding yet"
fi

echo ""
echo "=========================================="
echo "  Done. Dashboard: $BASE_URL/"
echo "=========================================="
