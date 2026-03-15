#!/bin/bash
# Deploy latest code on server (run ON server as waseem@54.86.65.150)
# After pushing to git from your machine, SSH and run:
#   ssh waseem@54.86.65.150
#   cd survey-bot/survai-platform && chmod +x deploy-waseem-54.sh && ./deploy-waseem-54.sh

set -e
BASE_URL="http://54.86.65.150:8080"

# Find repo root (parent of survai-platform)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "=========================================="
echo "  Pull latest (prod) and deploy to $BASE_URL"
echo "=========================================="

echo "[1/4] Pulling latest from origin prod..."
git fetch origin prod
git checkout prod
git pull origin prod

echo ""
echo "[2/4] Deploying from survai-platform..."
cd "$SCRIPT_DIR"
export VITE_SERVER_URL="${BASE_URL}/pg"
export VITE_RECIPIENT_URL="${BASE_URL}"
export NEXT_PUBLIC_API_BASE_URL="${BASE_URL}"
export PUBLIC_URL="${BASE_URL}"
export GATEWAY_PORT="${GATEWAY_PORT:-8080}"

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

echo ""
echo "=========================================="
echo "  Done. Dashboard: $BASE_URL/"
echo "=========================================="
