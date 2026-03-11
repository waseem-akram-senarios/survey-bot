#!/bin/bash
# Connect to the survey server (54.86.65.150) via SSH.
# Usage: ./connect-to-survey-server.sh
#        ./connect-to-survey-server.sh "command to run on server"
#
# Requires: your SSH public key must be in ubuntu@54.86.65.150 ~/.ssh/authorized_keys
# If you get "Permission denied (publickey)", add this key on the server:
#   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC24qSXO1n87m6ACx7rOiNo53oEkEK9pxaCZRRMy/n8a waseem@aidevlab.com

set -e
SERVER="survey-server"   # from ~/.ssh/config: 54.86.65.150, user ubuntu

if [ -n "$1" ]; then
  echo "Running on server: $*"
  ssh -o ConnectTimeout=10 "$SERVER" "$@"
else
  echo "Connecting to $SERVER (54.86.65.150)..."
  echo "  (To run a command: ./connect-to-survey-server.sh 'your command')"
  ssh -o ConnectTimeout=10 "$SERVER"
fi
