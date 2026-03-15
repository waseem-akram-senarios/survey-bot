# Frontend–backend integration

Your **frontend is integrated** with the microservices backend at **http://54.86.65.150:8080**.

## How it works

- When you open the app at **http://54.86.65.150:8080**, all API calls use that same origin (e.g. `http://54.86.65.150:8080/api/...`). No localhost or extra config needed.
- **Survey builder** (`/surveys/builder`): Save Survey → `POST /api/templates/create`, `POST /api/questions`, `POST /api/templates/addquestions`.
- **Launch survey** (`/surveys/launch`): Create Survey → `POST /api/surveys/generate`.
- Templates list, survey list, analytics, export, etc. all use `/api/*` on the same host.

## Deploy steps (so frontend talks to your backend)

1. **Build** the dashboard (no need to set `VITE_SERVER_URL` if the app is served from the same server as the API):
   ```bash
   cd survai-platform/dashboard
   npm run build
   ```
2. **Serve** the `dist/` folder from your server at the same host as the gateway (e.g. gateway and dashboard both on 54.86.65.150:8080). For example, the gateway can serve the dashboard static files from `dist/`.
3. Open **http://54.86.65.150:8080/surveys/builder** (or your login page first). Create a survey and click **Save Survey** — it should hit the backend and succeed.

## If the app is on a different host than the API

Set `VITE_SERVER_URL=http://54.86.65.150:8080` (and optionally `VITE_RECIPIENT_URL` for survey links) in `.env`, then run `npm run build` again. See `.env.example`.

## Quick backend check

```bash
cd survai-platform
python3 scripts/test_backend_create_survey.py http://54.86.65.150:8080
```

If all three steps return OK, the backend is ready; the frontend uses the same APIs.
