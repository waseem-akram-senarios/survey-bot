#!/bin/bash
# Deploy a specific git commit to http://54.86.65.150:8080
# Usage (on server):
#   ./deploy-commit-54.sh                    # deploy commit a2f0f6f51b7d115cfafe4266835f3e4ec0d1ec6b
#   ./deploy-commit-54.sh a2f0f6f51b7d115cfafe4266835f3e4ec0d1ec6b
#   DEPLOY_COMMIT=abc123 ./deploy-commit-54.sh

set -e
COMMIT="${DEPLOY_COMMIT:-${1:-a2f0f6f51b7d115cfafe4266835f3e4ec0d1ec6b}}"
DEPLOY_HOST="54.86.65.150"
BASE_URL="http://${DEPLOY_HOST}:8080"

echo "=============================================="
echo "  Deploying commit $COMMIT to $BASE_URL"
echo "=============================================="

if [ -f "docker-compose.microservices.yml" ]; then
  PLATFORM_DIR="$(pwd)"
else
  cd "$(dirname "$0")/.."
  [ -f "survai-platform/docker-compose.microservices.yml" ] || { echo "❌ Run from survey-bot or survai-platform."; exit 1; }
  PLATFORM_DIR="$(pwd)/survai-platform"
fi
# Git root is survey-bot (parent of survai-platform or cwd if we're in survey-bot)
GIT_ROOT="$(cd "$PLATFORM_DIR/.." && pwd)"
[ -d "$GIT_ROOT/.git" ] || GIT_ROOT="$(cd "$PLATFORM_DIR" && pwd)"

cd "$GIT_ROOT"
if [ ! -d ".git" ]; then
  echo "❌ Not a git repo. Clone the repo first, then run this script."
  exit 1
fi

echo ""
echo "[1/4] Fetching and checking out $COMMIT..."
git fetch origin 2>/dev/null || true
git checkout "$COMMIT" --detach 2>/dev/null || git checkout "$COMMIT" 2>/dev/null || {
  echo "❌ Cannot checkout $COMMIT. Try: git fetch origin && git checkout $COMMIT"
  exit 1
}
echo "   ✅ At commit $(git rev-parse --short HEAD)"

cd "$PLATFORM_DIR"
export VITE_SERVER_URL="${BASE_URL}/pg"
export VITE_RECIPIENT_URL="${BASE_URL}"
export NEXT_PUBLIC_API_BASE_URL="${BASE_URL}"
export PUBLIC_URL="${BASE_URL}"
export GATEWAY_PORT=8080

echo ""
echo "[2/4] Building and starting services..."
docker compose -f docker-compose.microservices.yml up -d --build

echo ""
echo "[3/4] Waiting 25s..."
sleep 25

echo ""
echo "[4/4] Health check..."
if curl -sf -m 5 "http://127.0.0.1:8080/health" >/dev/null; then
  echo "   ✅ Gateway OK"
else
  echo "   ⚠️ Gateway not ready yet"
fi
if curl -sf -m 5 "http://127.0.0.1:8080/pg/api/health" >/dev/null; then
  echo "   ✅ API OK"
else
  echo "   ⚠️ API not ready yet"
fi

[ -f "./verify-server.sh" ] && ./verify-server.sh 127.0.0.1 || true

echo ""
echo "🎉 Deploy done. Dashboard: $BASE_URL/"
echo "   Deployed commit: $(cd "$GIT_ROOT" && git rev-parse --short HEAD)"
