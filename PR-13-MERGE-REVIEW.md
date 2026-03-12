# PR #13 merge review – merge carefully

**PR:** [restore files to stable commit](https://github.com/waseem-akram-senarios/survey-bot/pull/13)  
**Source:** `staging` → **Target:** `main`  
**Author:** Muhammad Umer Usman (@umer-dilber)  
**Status:** Open, mergeable (clean)

---

## What the PR changes (1 commit: `67c697f`)

### 1. `survai-platform/docker-compose.microservices.yml`
- **Change:** Removes one comment line:  
  `# Host port 8080 (set GATEWAY_PORT to override, e.g. 80)`
- **Impact:** None. Port mapping stays `${GATEWAY_PORT:-8080}:8081`.

### 2. `survai-platform/gateway/nginx.conf`

| Change | Effect |
|--------|--------|
| **Remove** `resolver 127.0.0.11 valid=5s ipv6=off;` | Nginx will no longer re-resolve Docker’s embedded DNS every 5s. In some environments this was added to avoid 502s after container restarts. If you see 502s after restarting containers, you may need to bring the resolver back. |
| **favicon.ico** | `proxy_pass` changed from `dashboard_app` to `recipient_app`. Favicon is now served from the recipient (Next.js) app instead of the dashboard. |
| **Root `location /`** | Reverted from “variable upstream” pattern to direct `proxy_pass http://dashboard_app/;`. The variable was used to force nginx to re-resolve the upstream on each request. Simpler config; same “may 502 after restarts” trade-off as removing the resolver. |

---

## Risk summary

- **Low:** Comment removal and favicon source.
- **Low–medium:** Resolver and dashboard upstream change. Only matters if you see 502s after container restarts; if things are stable without them, merging is fine.

---

## How to merge carefully

1. **Optional:** Merge `main` into `staging` first so the PR is up to date (GitHub will show “This branch is up to date with main” if already the case).
2. On GitHub: open PR #13 → **Merge pull request** → confirm (create merge commit if you want a clear merge commit on `main`).
3. After merge: pull `main` locally and run a quick health check or e2e (e.g. gateway and one flow) to confirm.

---

## Commands (if you merge locally instead)

```bash
git fetch origin
git checkout main
git pull origin main
git merge origin/staging -m "Merge PR #13: restore files to stable commit"
git push origin main
```

Then close PR #13 on GitHub (or it will close automatically when you push to `main` if the PR was targeting `main` from `staging` and you merged `staging` into `main` elsewhere).
