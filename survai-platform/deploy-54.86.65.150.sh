#!/bin/bash
# Deploy SurvAI to server at http://54.86.65.150:8080
# Run this script ON the server (after: ssh user@54.86.65.150)

set -e
DEPLOY_HOST="54.86.65.150"
BASE_URL="http://${DEPLOY_HOST}:8080"

echo "🚀 Deploying SurvAI to $BASE_URL ..."

if [ -f "docker-compose.microservices.yml" ]; then
  PLATFORM_DIR="$(pwd)"
elif [ -f "survai-platform/docker-compose.microservices.yml" ]; then
  cd "$(dirname "$0")/.."
  PLATFORM_DIR="$(pwd)/survai-platform"
else
  echo "❌ Run from repo root or survai-platform (where docker-compose.microservices.yml is)"
  exit 1
fi

cd "$PLATFORM_DIR"

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

echo "⏳ Waiting 25s for services to start..."
sleep 25

echo "🔍 Health check (from this server)..."
if curl -sf -m 5 "http://127.0.0.1:8080/health" >/dev/null; then
  echo "   ✅ Gateway (localhost:8080)"
else
  echo "   ⚠️ Gateway not responding yet (may need more time)"
fi
if curl -sf -m 5 "http://127.0.0.1:8080/pg/api/health" >/dev/null; then
  echo "   ✅ API"
else
  echo "   ⚠️ API not responding yet"
fi

echo ""
echo "🔍 Running verify-server.sh..."
if [ -f "./verify-server.sh" ]; then
  ./verify-server.sh 127.0.0.1 || true
fi

echo ""
echo "🎉 Deploy done."
echo "   Dashboard: $BASE_URL"
echo "   From your browser open: $BASE_URL"
echo "   If you cannot connect, open port 8080 in the cloud firewall (see OPEN_PORT_8080.md)."
