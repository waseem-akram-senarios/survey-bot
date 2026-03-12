# Make http://54.86.65.150:8080/ Work

Follow these steps to fix and run the app on the server.

---

## Step 1: Run the fix script ON the server

SSH into the server and run the fix script (it starts the stack and checks health):

```bash
ssh ubuntu@54.86.65.150
cd survey-bot/survai-platform
# or: cd /path/where/you/have/survai-platform
chmod +x fix-54-server.sh
./fix-54-server.sh
```

If your repo is elsewhere, e.g. under your home:

```bash
cd ~/survey-bot/survai-platform
./fix-54-server.sh
```

The script will:

- Check Docker is installed and running  
- Use `.env` (warn if missing)  
- Set the public URL to `http://54.86.65.150:8080`  
- Run `docker compose up -d --build`  
- Wait and verify gateway + API on localhost  

If you see **✅ Gateway OK** and **✅ API OK**, the app is running on the server. If the browser still can’t open the URL, do Step 2.

---

## Step 2: Open port 8080 in the cloud firewall

The server must allow inbound **TCP 8080**. Otherwise the browser gets “Connection refused” or “Can’t reach this page”.

### AWS EC2

1. AWS Console → **EC2** → **Security Groups**.  
2. Select the security group attached to the instance **54.86.65.150**.  
3. **Edit inbound rules** → **Add rule**:
   - **Type:** Custom TCP  
   - **Port:** 8080  
   - **Source:** 0.0.0.0/0 (or your IP for restriction)  
4. Save.

### UFW on the server (if you use it)

```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

More options (GCP, Azure): see **OPEN_PORT_8080.md**.

---

## Step 3: Open in browser

From your PC/laptop open:

**http://54.86.65.150:8080/**

You should see the SurvAI dashboard.

---

## Quick checklist

| Step | Action | Done |
|------|--------|------|
| 1 | SSH to server, run `./fix-54-server.sh` in `survai-platform` | ☐ |
| 2 | Open port 8080 in cloud firewall (and UFW if used) | ☐ |
| 3 | Open http://54.86.65.150:8080/ in browser | ☐ |

---

## If it still doesn’t work

- **Connection refused:** Port 8080 is still blocked, or the app isn’t running. Re-run Step 1 on the server and double-check Step 2.  
- **502 Bad Gateway:** App is running but a backend is down; check `docker compose -f docker-compose.microservices.yml ps` and logs.  
- **.env missing:** Copy `.env.example` to `.env` on the server and set at least `DB_USER`, `DB_PASSWORD`, `OPENAI_API_KEY`, and `LIVEKIT_*` (see `.env.example`).
