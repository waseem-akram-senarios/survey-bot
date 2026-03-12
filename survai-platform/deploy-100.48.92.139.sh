#!/bin/bash
# Deploy latest code to server at http://100.48.92.139/
# Run this script ON the server (e.g. after: ssh user@100.48.92.139)

set -e
DEPLOY_HOST="100.48.92.139"
BASE_URL="http://${DEPLOY_HOST}:8080"

echo "🚀 Deploying SurvAI to $BASE_URL ..."

# If run from repo root (survey-bot/survai-platform)
if [ -f "docker-compose.microservices.yml" ]; then
  PLATFORM_DIR="$(pwd)"
elif [ -f "survai-platform/docker-compose.microservices.yml" ]; then
  cd "$(dirname "$0")/.."
  PLATFORM_DIR="$(pwd)/survai-platform"
else
  echo "❌ Run from survey-bot or survey-bot/survai-platform"
  exit 1
fi

cd "$PLATFORM_DIR"

# Export env for this host (dashboard/recipient need public URL)
export VITE_SERVER_URL="${BASE_URL}/pg"
export VITE_RECIPIENT_URL="${BASE_URL}"
export NEXT_PUBLIC_API_BASE_URL="${BASE_URL}"
export PUBLIC_URL="${BASE_URL}"
export GATEWAY_PORT="${GATEWAY_PORT:-8080}"

echo "📥 Pulling latest code..."
if [ -d ".git" ]; then
  git pull origin main || true
else
  echo "⚠️  Not a git repo; using existing files"
fi

echo "🔨 Building and starting services..."
docker compose -f docker-compose.microservices.yml up -d --build

echo "⏳ Waiting 20s for services..."
sleep 20

echo "🔍 Health check..."
curl -sf -m 5 "${BASE_URL}/pg/api/health" && echo " ✅ API" || echo " ⚠️ API not ready yet"
curl -sf -m 5 "${BASE_URL}/health" && echo " ✅ Gateway" || echo " ⚠️ Gateway not ready yet"

echo ""
echo "🎉 Deploy done. Dashboard: $BASE_URL"
