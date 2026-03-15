# Deploy your latest changes to the server (54.86.65.150:8080)

## Option A: From your computer (with SSH to the server)

1. **Commit your changes** (so the server can get them):
   ```bash
   cd /path/to/survey-bot
   git add -A
   git commit -m "Latest: survey builder fixes, frontend-backend integration"
   git push origin main
   ```

2. **Run the deploy script** (syncs code to server and rebuilds):
   ```bash
   cd survai-platform
   chmod +x deploy-and-verify-54.sh
   ./deploy-and-verify-54.sh
   ```
   This will:
   - rsync your local repo to `ubuntu@54.86.65.150:~/survey-bot` (or your `SURVEY_SERVER_PATH`)
   - SSH to the server and run `docker compose -f docker-compose.microservices.yml up -d --build`
   - Run a quick health check

   **If you don’t use SSH from this machine**, run Option B on the server instead.

---

## Option B: On the server (after SSH)

1. **SSH in:**
   ```bash
   ssh ubuntu@54.86.65.150
   ```

2. **Go to the repo and pull latest** (if you pushed from your computer):
   ```bash
   cd survey-bot
   git pull origin main
   cd survai-platform
   ```

3. **Deploy (build and start containers):**
   ```bash
   chmod +x deploy-54.86.65.150.sh
   ./deploy-54.86.65.150.sh
   ```
   Or:
   ```bash
   ./deploy-latest-on-server.sh
   ```

---

## After deploy

- **Dashboard:** http://54.86.65.150:8080/
- **Survey builder:** http://54.86.65.150:8080/surveys/builder

Do a hard refresh (Ctrl+Shift+R) so the browser loads the new bundle.
