# Debug: Connection Refused at http://54.86.65.150:8080/

"Connection refused" means the TCP connection to port 8080 is being rejected. There are **two possible causes**; the debug script tells you which.

---

## Step 1: Run the debug script on the server

SSH in and run (from the repo that contains `survai-platform`):

```bash
ssh ubuntu@54.86.65.150
cd survey-bot/survai-platform
chmod +x debug-connection-refused.sh
./debug-connection-refused.sh
```

Or from repo root: `cd survey-bot && survai-platform/debug-connection-refused.sh`

**Read the output:**

| What you see | Cause | Fix |
|--------------|--------|-----|
| **Section 1:** Nothing listening on 8080 | App is not running | Run `./fix-54-server.sh` in `survai-platform` |
| **Section 4:** "HTTP fail" or not 200 | App is not running or not ready | Run `./fix-54-server.sh`; if already run, check `docker logs gateway` |
| **Section 4:** "200 OK — app is running HERE" | App runs; firewall is blocking | Open port **8080** in AWS Security Group (or UFW). See OPEN_PORT_8080.md |

---

## Cause A: App not running on the server

**Symptoms:** Section 1 shows no process on port 8080; section 4 shows curl failed or non-200.

**Fix:**

```bash
cd survey-bot/survai-platform
./fix-54-server.sh
```

If that fails:

- Ensure `.env` exists (copy from `.env.example` and set DB_*, OPENAI_API_KEY, LIVEKIT_*, etc.).
- Check Docker: `docker ps -a` and `docker logs gateway`.

---

## Cause B: Firewall blocking port 8080

**Symptoms:** Section 4 says "200 OK — app is running HERE" but your browser still gets connection refused.

**Fix:** Open **TCP port 8080** in the **cloud firewall**:

- **AWS EC2:** EC2 → Security Groups → your instance’s group → Edit inbound rules → Add: Custom TCP, port **8080**, source **0.0.0.0/0**.
- **UFW on server:** `sudo ufw allow 8080/tcp && sudo ufw reload`

Then try again: **http://54.86.65.150:8080/**

---

## Codebase checks (already verified)

- **docker-compose.microservices.yml:** Gateway maps `0.0.0.0:8080:8081` so the host listens on all interfaces.
- **gateway/nginx.conf:** Nginx listens on **8081** inside the container (correct).
- **Gateway Dockerfile:** Uses nginx:alpine (includes curl for healthcheck).

So the config is correct; the issue is either **app not running** (A) or **firewall** (B). Use the debug script output to choose the fix above.
