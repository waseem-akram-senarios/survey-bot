# Run SurvAI on the Server

Use this to run the app on **http://54.86.65.150:8080/** and verify it works.

## Deploy latest and verify (from your machine)

If you have SSH access to the server:

```bash
cd survai-platform
chmod +x deploy-and-verify-54.sh
./deploy-and-verify-54.sh
```

Or from repo root:

```bash
chmod +x conn-survey-server.sh
./conn-survey-server.sh
```

Use a different SSH user if needed: `SSH_USER=ec2-user ./deploy-and-verify-54.sh`

---

## 1. On the server

SSH into the server and go to the project:

```bash
ssh your-user@54.86.65.150
cd /path/to/survey-bot/survai-platform
# Or: cd /path/to/survai-platform
```

Ensure you have a `.env` file with required keys (copy from `.env.example` and fill in):

- `DB_USER`, `DB_PASSWORD`, `OPENAI_API_KEY`, `LIVEKIT_*`, etc.

## 2. Deploy

From the **server** (inside the repo):

```bash
./deploy-54.86.65.150.sh
```

Or from repo root:

```bash
./survai-platform/deploy-54.86.65.150.sh
```

This will pull latest code, set the public URL to `http://54.86.65.150:8080`, build and start all services, and run a quick health check.

## 3. Verify on the server

Still on the server:

```bash
./verify-server.sh
```

Or check manually:

```bash
curl -s http://127.0.0.1:8080/health
curl -s http://127.0.0.1:8080/pg/api/health
```

You should see `200` or JSON like `{"status":"OK"}`.

## 4. Open port 8080 (cloud firewall)

If the app works locally on the server but you cannot open **http://54.86.65.150:8080** from your browser:

- **AWS EC2:** Security Groups → Inbound rules → Add Custom TCP **8080**, Source **0.0.0.0/0**
- **UFW on server:** `sudo ufw allow 8080/tcp && sudo ufw reload`

See **OPEN_PORT_8080.md** for more detail.

## 5. Open in browser

From your laptop/PC open:

**http://54.86.65.150:8080/**

You should see the SurvAI dashboard.

---

### Other server (e.g. 100.48.92.139)

Use the script for that host:

```bash
./deploy-100.48.92.139.sh
```

Then open **http://100.48.92.139:8080/** (from a device on the same Tailscale network if it’s a Tailscale IP).
