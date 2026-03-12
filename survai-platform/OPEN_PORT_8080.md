# Cannot Access Dashboard? Open Port 8080

**Works at http://localhost:8080 but not on the server?**

- On your **own machine**, `http://localhost:8080` works because the browser and the app are on the same host.
- On a **server**, open the app from your browser using the **server’s IP and port**: `http://SERVER_IP:8080/` (e.g. `http://54.86.65.150:8080/`). Do **not** use `localhost` in the browser when the app runs on a remote server.
- Ensure the server accepts connections on port **8080** (see below: cloud firewall and/or UFW).

**Getting "This site can't be reached" or "Connection refused" (ERR_CONNECTION_REFUSED)?**

Do **both** of these:

| Step | What to do |
|------|------------|
| **A** | **On the server:** SSH in and run `cd survey-bot/survai-platform && ./check-why-8080-refused.sh` — it tells you if the app is running or the firewall is the problem. If the app is not running, run `./fix-54-server.sh`. |
| **B** | **In the cloud:** Open **port 8080** in the firewall (AWS Security Group → Inbound → Add rule: Custom TCP, port **8080**, source **0.0.0.0/0**). See below for details. |

Also:
1. **Use the URL with port 8080** — **http://54.86.65.150:8080/** (not http://54.86.65.150/).
2. If the app is not running on the server, the browser will get connection refused even if the firewall is open — so do step A first, then B.

The app runs on **port 8080**. If you still cannot open:

- http://54.86.65.150:8080/
- http://100.48.92.139:8080/

the reason is usually **port 8080 is not allowed** from the internet (or from your network).

---

## 1. Server 54.86.65.150 (public IP)

This is likely a **cloud VM** (AWS, GCP, Azure, DigitalOcean, etc.). You must open port **8080** in the **cloud firewall** (security group / firewall rules).

### AWS EC2
1. EC2 → **Security Groups** → select the group attached to your instance.
2. **Edit inbound rules** → **Add rule**:
   - Type: **Custom TCP**
   - Port: **8080**
   - Source: **0.0.0.0/0** (or your IP for more security)
3. Save. Try again: http://54.86.65.150:8080/

### Google Cloud (GCP)
1. **VPC network** → **Firewall** → **Create firewall rule**:
   - Targets: your instance / tag
   - Source: **0.0.0.0/0**
   - Protocols and ports: **tcp:8080**
2. Save. Try: http://54.86.65.150:8080/

### Azure
1. **Virtual machine** → **Networking** → **Add inbound port rule**:
   - Port: **8080**, Protocol: TCP, Source: Any (or your IP)
2. Save. Try: http://54.86.65.150:8080/

### If you use UFW on the server
```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

---

## 2. Server 100.48.92.139 (Tailscale / VPN IP)

**100.48.92.139** is in the **100.64.0.0/10** range (Tailscale or similar VPN). It is **not** reachable from the normal internet.

- You **must** use a device that is on the **same Tailscale network** (same account).
- On that device: install Tailscale, log in, then open: **http://100.48.92.139:8080/**
- From any other network (e.g. home Wi‑Fi without Tailscale), this URL will never work.

---

## Quick check from the server

SSH into the server and run:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/
```

If you see **200**, the app is fine; the problem is network/firewall between your browser and the server. Open port **8080** (and, for 100.48.92.139, use Tailscale).
