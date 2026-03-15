# Survey flow: creation to sending (E2E)

## Quick verification (run with backend on :8080 or dashboard dev on :5173)

1. **Start app:** `cd survai-platform/dashboard && npm run dev` → http://localhost:5173/
2. **Login:** e.g. `admin` / `admin123`
3. **Dashboard:** You should see "Rider Voice", "+ Create Survey", "Launch survey", "Templates", "Surveys" in the top bar.
4. **Create:** Click "+ Create Survey" → enter title, add a question (e.g. Open Ended) → "Save Survey" → redirects to Templates (needs API for save).
5. **Launch:** Click "Launch survey" or go to Templates → Launch on a row → select template, Recipient name → "Create Survey" (needs API).
6. **Send:** Go to Surveys → use Send on a survey row (needs API).

**E2E tests:** `cd e2e-tests && npx playwright install && BASE_URL=http://localhost:5173 npx playwright test --project=dashboard`

---

## 1. Create a survey (builder)

- **Where:** Dashboard → **+ Create Survey** (or **Templates** → then create from builder).
- **Route:** `/surveys/builder`
- **Steps:**
  1. Enter Survey title, Client/Agency name, Description (optional).
  2. Click **Add a question** and add one or more question types (Multiple Choice, Open Ended, Yes/No, Rating, NPS, Route/Stop, Date/Time).
  3. Click **Save Survey**.
- **Result:** A template is created (name = survey title or "Survey YYYY-MM-DD") and you are redirected to **Templates** (`/templates/manage`).

## 2. Launch a survey (create + send to recipient)

- **Where:** **Templates** → click **Launch** on a template, or Dashboard → **Launch survey**.
- **Route:** `/surveys/launch`
- **Steps:**
  1. Select a **template** (pre-filled if you came from the Templates table).
  2. Enter **Recipient name** (required); optionally Rider name, Ride ID, Phone, Biodata.
  3. Choose **language** (e.g. English).
  4. Click **Create Survey** (generate + launch).
- **Result:** Survey is generated and launched; you are redirected to **Survey status** (`/surveys/status/{surveyId}`).

## 3. Send an existing survey (email / phone)

- **Where:** **Surveys** (Manage Surveys) in the top nav.
- **Route:** `/surveys/manage`
- **Steps:**
  1. Find the survey in the table.
  2. Click the **Send** (email/phone) action for that row.
  3. Enter email or phone and confirm.
- **Result:** Survey is sent by email or a call is initiated to the given phone.

## Navigation (TopBar)

- **Dashboard** – Home, stats, Create Survey, Launch survey, Manage Surveys.
- **Templates** – Manage templates, Launch from table.
- **Surveys** – Manage and send existing surveys.
- **Analytics** – Analytics.
- **Contacts** – Contacts.

All of the above flows are wired end-to-end in the app.
