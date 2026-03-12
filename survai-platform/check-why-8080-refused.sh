#!/bin/bash
# Run this ON the server (54.86.65.150) to see why http://54.86.65.150:8080/ refuses connection.
# Usage: ssh ubuntu@54.86.65.150, then: cd survey-bot/survai-platform && ./check-why-8080-refused.sh

echo "=============================================="
echo "  Why is 54.86.65.150:8080 refusing connection?"
echo "=============================================="
echo ""

# 1. Is anything listening on 8080?
echo "[1] Is anything listening on port 8080?"
if command -v ss >/dev/null 2>&1; then
  ss -tlnp 2>/dev/null | grep -q ':8080 ' && echo "    ✅ Yes (something is listening on 8080)" || echo "    ❌ No — the app is NOT running. Start it with: ./fix-54-server.sh"
elif command -v netstat >/dev/null 2>&1; then
  netstat -tlnp 2>/dev/null | grep -q ':8080 ' && echo "    ✅ Yes" || echo "    ❌ No — start the app: ./fix-54-server.sh"
else
  (curl -sf -m 2 http://127.0.0.1:8080/health >/dev/null && echo "    ✅ Yes (localhost:8080 responds)") || echo "    ❌ No — start the app: ./fix-54-server.sh"
fi

# 2. Docker and gateway container
echo ""
echo "[2] Is the gateway container running?"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^gateway$'; then
  echo "    ✅ Yes"
else
  echo "    ❌ No — start the stack: ./fix-54-server.sh"
fi

# 3. Localhost health
echo ""
echo "[3] Does http://127.0.0.1:8080 work on this server?"
if curl -sf -m 3 http://127.0.0.1:8080/health >/dev/null 2>&1; then
  echo "    ✅ Yes — app is running. The problem is the FIREWALL: open port 8080 in AWS Security Group (or UFW)."
else
  echo "    ❌ No — app is not running here. Run: ./fix-54-server.sh"
fi

echo ""
echo "=============================================="
echo "  What to do:"
echo "  • If [1] or [3] said ❌ → run: ./fix-54-server.sh"
echo "  • If [1] and [3] said ✅ but browser still refuses → open port 8080 in cloud firewall (see OPEN_PORT_8080.md)"
echo "=============================================="
