#!/bin/bash
# Run this ON the server (54.86.65.150) to find why http://54.86.65.150:8080/ refuses connection.
# Copy the output and use it to fix the issue (or share with support).

echo "=============================================="
echo "  DEBUG: Connection refused on :8080"
echo "  Run on server: $(hostname -f 2>/dev/null || hostname) at $(date)"
echo "=============================================="

# Find platform dir
if [ -f "docker-compose.microservices.yml" ]; then
  PD="$(pwd)"
elif [ -f "survai-platform/docker-compose.microservices.yml" ]; then
  cd "$(dirname "$0")/.."
  PD="$(pwd)/survai-platform"
else
  PD=""
fi

echo ""
echo "--- 1. Is anything listening on port 8080? ---"
if command -v ss >/dev/null 2>&1; then
  ss -tlnp 2>/dev/null | grep -E ':8080 |LISTEN' || true
  ss -tlnp 2>/dev/null | grep -q ':8080 ' && echo "  => Something is listening on 8080" || echo "  => NOTHING on 8080 (app not running or wrong port)"
else
  netstat -tlnp 2>/dev/null | grep -E '8080|LISTEN' || true
fi

echo ""
echo "--- 2. Docker: gateway container ---"
docker ps -a --filter name=gateway --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo "  Docker not running or no gateway container"

echo ""
echo "--- 3. All containers (survey-bot stack) ---"
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null | head -20 || true

echo ""
echo "--- 4. Curl from this server to localhost:8080 ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' -m 2 http://127.0.0.1:8080/health 2>/dev/null || echo "fail")
if [ "$CODE" = "200" ]; then
  echo "  => 200 OK — app is running HERE. Problem is FIREWALL (open port 8080 in AWS Security Group / UFW)."
else
  echo "  => HTTP $CODE or failed — app is NOT responding on this server. Start it: cd $PD && ./fix-54-server.sh"
fi

echo ""
echo "--- 5. UFW status (if used) ---"
sudo ufw status 2>/dev/null | head -10 || echo "  (ufw not available or no sudo)"

echo ""
echo "--- 6. Gateway container port mapping ---"
docker port gateway 2>/dev/null || echo "  (gateway container not found)"

echo ""
echo "--- 7. If platform dir found: .env and compose ---"
if [ -n "$PD" ] && [ -d "$PD" ]; then
  [ -f "$PD/.env" ] && echo "  .env: exists" || echo "  .env: MISSING (copy .env.example)"
  grep -E 'GATEWAY_PORT|8080:8081' "$PD/docker-compose.microservices.yml" 2>/dev/null | head -3 || true
fi

echo ""
echo "=============================================="
echo "  SUMMARY"
echo "  • If section 1 shows nothing on 8080  → run: ./fix-54-server.sh"
echo "  • If section 4 says 200 OK           → open port 8080 in cloud firewall (AWS Security Group)"
echo "  • If gateway container is Exit/Restart → check: docker logs gateway"
echo "=============================================="
