#!/bin/bash
# Deploy latest code to http://54.86.65.150:8080 and verify.
# Run from your machine (with SSH access to the server):
#   chmod +x deploy-and-verify-54.sh && ./deploy-and-verify-54.sh
# Or run ON the server (from survai-platform dir):
#   ./deploy-54.86.65.150.sh && ./verify-server.sh

set -e
HOST="54.86.65.150"
BASE="http://${HOST}:8080"
# Override SSH user if needed: SSH_USER=ec2-user ./deploy-and-verify-54.sh
SSH_USER="${SSH_USER:-ubuntu}"
SURVEY_SERVER="${SSH_USER}@${HOST}"
REMOTE_PATH="${SURVEY_SERVER_PATH:-survey-bot}"
[[ "$REMOTE_PATH" == /* ]] && REMOTE_PLATFORM="$REMOTE_PATH/survai-platform" || REMOTE_PLATFORM='~/'"$REMOTE_PATH"'/survai-platform'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/docker-compose.microservices.yml" ]; then
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
else
  REPO_ROOT="$(cd "$SCRIPT_DIR" && pwd)"
fi

echo "=========================================="
echo "  Deploy latest to $BASE and verify"
echo "=========================================="

# If we have ssh, deploy from local; else assume we're on the server
if ssh -o BatchMode=yes -o ConnectTimeout=5 "$SURVEY_SERVER" "exit" 2>/dev/null; then
  echo ""
  echo "[1/4] Syncing code to server..."
  RSYNC_DEST="$SURVEY_SERVER:$REMOTE_PATH"
  [[ "$REMOTE_PATH" != /* ]] && RSYNC_DEST="$SURVEY_SERVER:~/$REMOTE_PATH"
  if rsync -az --delete \
    --exclude '.git' --exclude 'node_modules' --exclude '__pycache__' --exclude '.env' \
    "$REPO_ROOT/" "$RSYNC_DEST/" 2>/dev/null; then
    echo "   ✅ Code synced"
  else
    echo "   ⚠️ rsync failed (continuing; server must have repo)"
  fi

  echo ""
  echo "[2/4] Running deploy on server..."
  ssh "$SURVEY_SERVER" "cd $REMOTE_PLATFORM && \
    export VITE_SERVER_URL=\"$BASE/pg\" && \
    export VITE_RECIPIENT_URL=\"$BASE\" && \
    export NEXT_PUBLIC_API_BASE_URL=\"$BASE\" && \
    export PUBLIC_URL=\"$BASE\" && \
    export GATEWAY_PORT=8080 && \
    docker compose -f docker-compose.microservices.yml up -d --build && \
    echo '⏳ Waiting 25s...' && sleep 25"
else
  echo ""
  echo "[1/4] No SSH to $SURVEY_SERVER (or not from your machine)."
  echo "   Run this script ON the server instead:"
  echo "   ssh $SURVEY_SERVER"
  echo "   cd $REMOTE_PATH/survai-platform && ./deploy-54.86.65.150.sh && ./verify-server.sh"
  echo ""
  echo "   Or from your machine, ensure SSH works: ssh $SURVEY_SERVER"
  exit 1
fi

echo ""
echo "[3/4] Verify on server..."
ssh "$SURVEY_SERVER" "cd $REMOTE_PLATFORM && ./verify-server.sh 127.0.0.1" || true

echo ""
echo "[4/4] Verify from here (http://$HOST:8080)..."
if curl -sf -m 5 "$BASE/health" >/dev/null; then
  echo "   ✅ Gateway reachable"
else
  echo "   ⚠️ Gateway not reachable (open port 8080 in cloud firewall)"
fi
if curl -sf -m 5 "$BASE/pg/api/health" >/dev/null; then
  echo "   ✅ API reachable"
else
  echo "   ⚠️ API not reachable"
fi

echo ""
echo "=========================================="
echo "  Dashboard: $BASE/"
echo "  If you cannot connect, see OPEN_PORT_8080.md"
echo "=========================================="
