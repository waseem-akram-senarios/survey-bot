# E2E Tests (Playwright)

Run UI and API tests against the SurvAI platform.

## Run against local (default: http://localhost:8080)

```bash
npm install
npx playwright install chromium   # first time only
npm test
```

## Run against server (http://54.86.65.150:8080)

```bash
BASE_URL=http://54.86.65.150:8080 npx playwright test
# or
npm run test:server
```

## Run specific suites

```bash
BASE_URL=http://54.86.65.150:8080 npx playwright test --project=api-health
BASE_URL=http://54.86.65.150:8080 npx playwright test --project=dashboard
BASE_URL=http://54.86.65.150:8080 npx playwright test --project=surveys
BASE_URL=http://54.86.65.150:8080 npx playwright test --project=templates
BASE_URL=http://54.86.65.150:8080 npx playwright test --project=recipient
```

## View report

```bash
npx playwright show-report
```
