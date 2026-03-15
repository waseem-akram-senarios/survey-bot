# Survey flow: creation to sending (E2E)

## Frontend–backend integration

The dashboard talks to the API at `/api/*`. For this to work end-to-end:

### Local development (recommended)

1. **Start the backend** so the gateway listens on **port 8080**:
   - From repo root: `cd survai-platform && docker compose -f docker-compose.microservices.yml up --build`
   - Or run the gateway + required services (template-service, question-service, survey-service, postgres) however you normally do.
2. **Start the dashboard**: `cd survai-platform/dashboard && npm run dev` → http://localhost:5173
3. The Vite dev server **proxies** all requests from `http://localhost:5173/api/*` to `http://localhost:8080/api/*`. The gateway then rewrites `/api/` to `/pg/api/` and routes to the right service.
4. **Do not set** `VITE_SERVER_URL` in `.env` for this setup (leave it unset so the app uses relative `/api` and the proxy is used).

### Server deployment (e.g. http://54.86.65.150:8080)

When the dashboard is served from the **same host** as the gateway (e.g. at `http://54.86.65.150:8080`):

1. **Build** without setting `VITE_SERVER_URL` (or set it to `http://54.86.65.150:8080`). The app uses the **current origin** at runtime, so opening `http://54.86.65.150:8080/surveys/builder` will send API requests to `http://54.86.65.150:8080/api/*` and survey links will use the same host.
2. Ensure the **gateway and backend services** (template-service, question-service, survey-service, postgres) are running on that server so `/api/*` is handled.
3. **Test create survey:** Open `http://54.86.65.150:8080/surveys/builder` → add title and questions → **Save Survey**. If you see “Survey saved successfully”, the flow works on the server.
4. **Test launch survey:** Open `http://54.86.65.150:8080/surveys/launch` → select template, recipient, phone → **Create Survey**.

### Production or API on another host

- Set `VITE_SERVER_URL` to the gateway URL (e.g. `http://your-server:8080`) in `.env` and rebuild. All API calls (axios and fetch) will then use that base URL.
- See `dashboard/.env.example` for the exact variable names.

### Quick check that the backend is reachable

- Open the dashboard, go to **Surveys** → **Survey library** (or **Templates**). If the list loads, the API is reachable.
- Create a survey from **+ Create Survey** → add questions → **Save Survey**. If you see “Survey saved successfully” and redirect to the library, the full create flow (template + questions + link) is working.

---

## Test: Can you launch a survey from the new UI?

Yes. You can launch in two ways:

### Option A – From Dashboard
1. Open **Dashboard** (after login).
2. Click the **Launch survey** button (outlined, next to Refresh).
3. You should land on **Create Survey** at `/surveys/launch`.
4. Select a **template** (dropdown), enter **Recipient name**, then click **Create Survey** (needs backend to complete).

### Option B – From Survey library (unified Surveys page)
1. Click **Surveys** in the top bar → opens the unified Surveys page with tabs **Launched** | **Survey library**.
2. Click the **Survey library** tab.
3. In the table, click the **Launch Survey** button on a row (survey definition).
4. You should land on `/surveys/launch` with that template **pre-selected**.
5. Enter **Recipient name** and click **Create Survey** (needs backend).

Both paths use the same launch page; the only difference is that from the library, the template is already chosen.

---

## Quick verification (manual)

1. **Start app:** `cd survai-platform/dashboard && npm run dev` → http://localhost:5173/ (or :5174 if 5173 is in use).
2. **Login:** e.g. `admin` / `admin123`.
3. **Dashboard:** You should see "Rider Voice", "+ Create Survey", "Launch survey", and in the top bar: **Surveys** (no separate Templates).
4. **Launch from Dashboard:** Click **Launch survey** → you should see the launch page (template dropdown, Recipient name, Create Survey).
5. **Launch from Survey library:** Click **Surveys** → **Survey library** tab → click **Launch Survey** on a row (if any) → same launch page, template pre-selected.
6. **Create:** "+ Create Survey" → builder → add question → Save → redirects to **Surveys** (Survey library tab). Needs API for save.

**E2E (Playwright):**  
`cd e2e-tests && npx playwright install chromium && BASE_URL=http://localhost:5173 npx playwright test --project=dashboard`  
Tests include: "Can launch a survey from new UI" and "Can launch from Survey library".

---

## 1. Create a survey (builder)

- **Where:** Dashboard → **+ Create Survey**.
- **Route:** `/surveys/builder`
- **Steps:** Enter title, add questions, **Save Survey**.
- **Result:** Redirects to **Surveys** (Survey library tab). Needs API.

## 2. Launch a survey

- **Where:** Dashboard → **Launch survey**, or **Surveys** → **Survey library** → **Launch Survey** on a row.
- **Route:** `/surveys/launch`
- **Steps:** Select template (or use pre-selected), Recipient name, **Create Survey**.
- **Result:** Survey created and launched; redirect to status page. Needs API.

## 3. Send existing survey (email/phone)

- **Where:** **Surveys** → **Launched** tab → Send on a row.
- **Result:** Send by email or start call. Needs API.

## Navigation (TopBar)

- **Dashboard** – Home, Create Survey, Launch survey.
- **Surveys** – Launched + Survey library (tabs).
- **Analytics**, **Contacts**.
