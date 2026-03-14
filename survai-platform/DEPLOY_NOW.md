# Deploy latest code to server (54.86.65.150)

Latest code is **already pushed** to `main`. Deploy on the server as follows.

## Option A: SSH and run deploy script (recommended)

1. SSH into the server (use your SSH user, e.g. `waseem` or `ubuntu`):
   ```bash
   ssh waseem@54.86.65.150
   ```
   (Replace `waseem` with your server username if different.)

2. Go to the project and run the deploy script:
   ```bash
   cd ~/survey-bot/survai-platform
   chmod +x deploy-latest-on-server.sh
   ./deploy-latest-on-server.sh
   ```
   If your repo is elsewhere (e.g. `/home/waseem/survey-bot`):
   ```bash
   cd /home/waseem/survey-bot/survai-platform
   ./deploy-latest-on-server.sh
   ```

3. The script will:
   - Pull latest from `origin main`
   - Build and start all services with Docker
   - Run a short health check

4. Open in browser: **http://54.86.65.150:8080/**

---

## Option B: Manual steps on the server

```bash
ssh your-user@54.86.65.150
cd ~/survey-bot   # or your repo path
git pull origin main
cd survai-platform
export VITE_SERVER_URL="http://54.86.65.150:8080/pg"
export VITE_RECIPIENT_URL="http://54.86.65.150:8080"
export GATEWAY_PORT=8080
docker compose -f docker-compose.microservices.yml up -d --build
```

---

## From your machine (if SSH works)

If you have SSH key access to the server, you can use:

```bash
cd survai-platform
SSH_USER=waseem ./deploy-and-verify-54.sh
```
(Replace `waseem` with your server username.)
