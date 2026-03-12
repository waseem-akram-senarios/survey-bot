# Deploy latest version on the server

`conn-survey-server.sh` is now executable (`chmod +x` done). Use it **locally** to check Docker and API health after deploy.

## Deploy from your machine (if SSH works)

```bash
# From repo root
./survai-platform/deploy-and-verify-54.sh
```

If that fails with "No SSH", deploy **on the server** as below.

---

## Deploy ON the server (54.86.65.150)

1. **SSH in**
   ```bash
   ssh ubuntu@54.86.65.150
   ```

2. **Go to the repo and pull latest**
   ```bash
   cd survey-bot
   git pull origin main
   ```

3. **Run deploy from platform dir**
   ```bash
   cd survai-platform
   chmod +x deploy-54.86.65.150.sh verify-server.sh
   ./deploy-54.86.65.150.sh
   ./verify-server.sh 127.0.0.1
   ```

4. **Check from browser**
   - Dashboard: http://54.86.65.150:8080

---

## One-liner (on server, from home dir)

```bash
cd ~/survey-bot && git pull origin main && cd survai-platform && ./deploy-54.86.65.150.sh && ./verify-server.sh 127.0.0.1
```

---

## After deploy: local health check

From your **local** machine (in the repo):

```bash
./conn-survey-server.sh
```

This checks Docker containers and API health (when run on the machine where Docker is running). To check the **remote** server from your laptop:

```bash
curl -s http://54.86.65.150:8080/health
curl -s http://54.86.65.150:8080/pg/api/health
```
