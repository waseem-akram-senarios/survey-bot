#!/bin/bash
# Run this ON the server to verify docker compose and nginx are working.
# After this shows OK, you can check from the web (browser).
# Usage: ssh user@54.86.65.150, then: cd survey-bot/survai-platform && ./check-server-inside.sh

set -e
FAIL=0

echo "=============================================="
echo "  Server check: Docker Compose & Nginx"
echo "  (Run on server; then check from web)"
echo "=============================================="

# Find platform dir
if [ -f "docker-compose.microservices.yml" ]; then
  PD="$(pwd)"
elif [ -f "survai-platform/docker-compose.microservices.yml" ]; then
  cd "$(dirname "$0")/.."
  PD="$(pwd)/survai-platform"
else
  echo "❌ Run from survey-bot or survai-platform."
  exit 1
fi
cd "$PD"

echo ""
echo "--- 1. Docker Compose file ---"
if docker compose -f docker-compose.microservices.yml config --quiet 2>/dev/null; then
  echo "   ✅ docker-compose.microservices.yml is valid"
else
  echo "   ❌ docker-compose config invalid"
  FAIL=1
fi

echo ""
echo "--- 2. Gateway container ---"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx gateway; then
  echo "   ✅ gateway container is running"
else
  echo "   ❌ gateway not running (run: ./fix-54-server.sh)"
  FAIL=1
fi

echo ""
echo "--- 3. Nginx config (inside gateway container) ---"
if docker exec gateway nginx -t 2>/dev/null; then
  echo "   ✅ nginx config OK"
else
  echo "   ❌ nginx config error (check gateway/nginx.conf)"
  FAIL=1
fi

echo ""
echo "--- 4. Port 8080 listening on this server ---"
if command -v ss >/dev/null 2>&1; then
  if ss -tlnp 2>/dev/null | grep -q ':8080 '; then
    echo "   ✅ something is listening on 8080"
  else
    echo "   ❌ nothing on 8080 (gateway may not have started correctly)"
    FAIL=1
  fi
else
  echo "   (skipped: ss not available)"
fi

echo ""
echo "--- 5. http://127.0.0.1:8080/health ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/health 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
  echo "   ✅ HTTP 200"
else
  echo "   ❌ HTTP $CODE (expected 200)"
  FAIL=1
fi

echo ""
echo "--- 6. http://127.0.0.1:8080/pg/api/health ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' -m 3 http://127.0.0.1:8080/pg/api/health 2>/dev/null || echo "000")
if [ "$CODE" = "200" ]; then
  echo "   ✅ HTTP 200"
else
  echo "   ❌ HTTP $CODE (expected 200)"
  FAIL=1
fi

echo ""
echo "--- 7. All stack containers (quick list) ---"
docker ps -a --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null | head -16 || true

echo ""
echo "=============================================="
if [ $FAIL -eq 0 ]; then
  echo "  ✅ All checks passed. Docker Compose and Nginx are working."
  echo "  You can now check from the web: http://54.86.65.150:8080/"
  echo "  (If browser still fails, open port 8080 in cloud firewall.)"
else
  echo "  ❌ Some checks failed. Fix the issues above, then run this script again."
  echo "  To start/restart stack: ./fix-54-server.sh"
  exit 1
fi
echo "=============================================="
