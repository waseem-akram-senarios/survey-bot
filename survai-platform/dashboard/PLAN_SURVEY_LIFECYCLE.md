# Plan: Full Survey Lifecycle + Playwright Automation

## Goals
1. **Treat templates and surveys the same** – one "Surveys" section (Survey library + Launched surveys).
2. **No separate "Templates" in nav** – single "Surveys" with tabs: Launched | Library.
3. **Full survey lifecycle** – Create (builder) → Save → Launch/Send → Manage → Status/Complete.
4. **Playwright automation** – one survey-lifecycle E2E; remove template-only tests; fix all bugs.

## Implementation

### 1. Fix routes (current bugs)
- `surveys/builder` → use **CreateSurveyBuilder** (not SurveyBuilderAdvanced).
- `contacts` → use **Contacts** (not RouteDebug).
- Remove **RouteDebug** from catch-all; use **NotFound**.
- Remove debug `console.log` imports.

### 2. Unified Surveys page
- New route: **/surveys** (or keep /surveys/manage as main).
- Page with two tabs: **Launched** (ManageSurveys) | **Library** (Templates = survey definitions).
- Builder "Save" redirects to **/surveys** (tab=Library).
- TopBar: one **Surveys** link → /surveys.

### 3. Playwright
- Install browsers: `npx playwright install chromium`.
- One **survey-lifecycle.spec.js**: login → dashboard → create survey (builder) → add question → save → surveys (library) → launch → surveys (launched).
- Remove or merge **templates.spec.js** into survey flow (no standalone template tests).
- Run tests; fix any failures.

### 4. Fix bugs found during testing
- Fix route/import errors, missing elements, API assumptions.

---

## Done

- **Routes:** CreateSurveyBuilder for builder; Contacts for contacts; NotFound for *; SurveysUnified for /surveys and /surveys/manage; /templates/manage redirects to /surveys?tab=library.
- **SurveysUnified.jsx:** Tabs "Launched" (ManageSurveys) and "Survey library" (Templates). URL ?tab=library for library.
- **TopBar:** Single "Surveys" link to /surveys. Builder save → /surveys?tab=library.
- **Playwright:** survey-flow.spec.js has full lifecycle test; dashboard expects "Surveys"; templates.spec runs under project "surveys" (no separate templates project).
- **Run E2E:** `cd e2e-tests && npx playwright install chromium && BASE_URL=http://localhost:5173 npx playwright test --project=dashboard`
