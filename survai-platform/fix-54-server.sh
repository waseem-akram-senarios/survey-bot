#!/bin/bash
# Fix and start SurvAI on this server so http://54.86.65.150:8080/ works.
# Run ON the server: ssh user@54.86.65.150, then run this script.

set -e
HOST="54.86.65.150"
BASE="http://${HOST}:8080"

echo "=============================================="
echo "  Fix & start SurvAI at $BASE"
echo "=============================================="

# Find platform dir (run from survey-bot or survai-platform)
if [ -f "docker-compose.microservices.yml" ]; then
  PLATFORM_DIR="$(pwd)"
elif [ -f "survai-platform/docker-compose.microservices.yml" ]; then
  cd "$(dirname "$0")/.."
  PLATFORM_DIR="$(pwd)/survai-platform"
else
  echo "❌ Run from survey-bot or survai-platform (where docker-compose.microservices.yml is)."
  exit 1
fi
cd "$PLATFORM_DIR" || { echo "❌ Cannot cd to $PLATFORM_DIR"; exit 1; }

echo ""
echo "[1/5] Checking Docker..."
if ! command -v docker >/dev/null 2>&1; then
  echo "   ❌ Docker not installed. Install Docker and Docker Compose first."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "   ❌ Docker daemon not running. Start Docker (e.g. sudo systemctl start docker)."
  exit 1
fi
echo "   ✅ Docker OK"

echo ""
echo "[2/5] Checking .env..."
if [ ! -f ".env" ]; then
  echo "   ⚠️ No .env file. Copy .env.example to .env and set DB_*, OPENAI_API_KEY, LIVEKIT_*, etc."
  echo "   Continuing anyway (compose may fail without required vars)."
else
  echo "   ✅ .env exists"
fi

echo ""
echo "[3/5] Setting URL and starting stack..."
export VITE_SERVER_URL="${BASE}/pg"
export VITE_RECIPIENT_URL="${BASE}"
export NEXT_PUBLIC_API_BASE_URL="${BASE}"
export PUBLIC_URL="${BASE}"
export GATEWAY_PORT=8080

docker compose -f docker-compose.microservices.yml up -d --build

echo ""
echo "[4/5] Waiting for services (30s)..."
sleep 30

echo ""
echo "[5/5] Verifying on this server..."
if [ -f "./verify-server.sh" ]; then
  ./verify-server.sh 127.0.0.1 || true
else
  curl -sf -m 5 "http://127.0.0.1:8080/health" >/dev/null && echo "   ✅ Gateway OK" || echo "   ⚠️ Gateway not ready"
  curl -sf -m 5 "http://127.0.0.1:8080/pg/api/health" >/dev/null && echo "   ✅ API OK" || echo "   ⚠️ API not ready"
fi

echo ""
echo "=============================================="
echo "  If you see ✅ above, the app is running here."
echo "  To reach it from your browser:"
echo ""
echo "  1. Open port 8080 in the CLOUD FIREWALL:"
echo "     AWS: EC2 → Security Groups → Inbound → Add Custom TCP 8080, Source 0.0.0.0/0"
echo "     UFW on server: sudo ufw allow 8080/tcp && sudo ufw reload"
echo ""
echo "  2. Open in browser: $BASE/"
echo ""
echo "  Details: OPEN_PORT_8080.md"
echo "=============================================="
