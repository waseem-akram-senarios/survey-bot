#!/bin/bash
# Run ON the server to verify the app is listening and healthy.
# Usage: ./verify-server.sh [host]   (default: 127.0.0.1)

HOST="${1:-127.0.0.1}"
BASE="http://${HOST}:8080"

echo "Checking $BASE ..."
echo ""

code_gateway=$(curl -s -o /dev/null -w "%{http_code}" -m 5 "$BASE/health" 2>/dev/null || echo "000")
code_api=$(curl -s -o /dev/null -w "%{http_code}" -m 5 "$BASE/pg/api/health" 2>/dev/null || echo "000")

if [ "$code_gateway" = "200" ]; then
  echo "  Gateway /health: $code_gateway ✅"
else
  echo "  Gateway /health: $code_gateway ❌"
fi
if [ "$code_api" = "200" ]; then
  echo "  API /pg/api/health: $code_api ✅"
else
  echo "  API /pg/api/health: $code_api ❌"
fi

echo ""
if [ "$code_gateway" = "200" ] && [ "$code_api" = "200" ]; then
  echo "✅ Server is working. Open in browser: $BASE"
  exit 0
else
  echo "❌ One or more checks failed. Ensure containers are up: docker compose -f docker-compose.microservices.yml ps"
  exit 1
fi
