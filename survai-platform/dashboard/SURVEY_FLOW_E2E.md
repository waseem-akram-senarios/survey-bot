# Survey flow: creation to sending (E2E)

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
