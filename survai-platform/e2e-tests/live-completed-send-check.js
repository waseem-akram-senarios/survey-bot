const { chromium } = require('@playwright/test');

const BASE = 'http://54.86.65.150:8080';

async function waitForApp(page, ms = 3000) {
  await page.waitForLoadState('domcontentloaded');
  try {
    await page.waitForLoadState('networkidle', { timeout: 15000 });
  } catch (_) {
    // Some dashboard requests may keep polling; the timeout is non-fatal here.
  }
  await page.waitForTimeout(ms);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
  const page = await context.newPage();

  const report = {
    mainPageText: '',
    completedPageText: '',
    completedSendButtons: 0,
    completedRows: 0,
    resultUrl: '',
    resultPageText: '',
    resultHasSendButton: false,
    blockingIssue: '',
    screenshots: {},
  };

  try {
    await page.goto(BASE);
    await page.evaluate(() => {
      localStorage.setItem(
        'survai_user',
        JSON.stringify({
          username: 'admin',
          role: 'admin',
          tenantId: 'itcurves',
          orgName: 'IT Curves',
        })
      );
    });

    await page.goto(`${BASE}/dashboard`);
    await waitForApp(page);
    report.screenshots.dashboard = '/home/senarios/Desktop/survey-bot/survai-platform/e2e-tests/test-results/live-dashboard.png';
    await page.screenshot({ path: report.screenshots.dashboard, fullPage: true });
    report.mainPageText = (await page.textContent('body')) || '';

    await page.goto(`${BASE}/surveys/completed`);
    await waitForApp(page, 5000);
    report.screenshots.completed = '/home/senarios/Desktop/survey-bot/survai-platform/e2e-tests/test-results/live-completed.png';
    await page.screenshot({ path: report.screenshots.completed, fullPage: true });
    report.completedPageText = (await page.textContent('body')) || '';
    report.completedRows = await page.locator('table tbody tr').count();
    report.completedSendButtons = await page.locator('img[alt="Send Survey"]').count();

    if (report.completedRows === 0) {
      report.blockingIssue = 'No completed survey rows were rendered on /surveys/completed.';
    } else {
      await page.locator('table tbody tr').first().locator('td').first().click();
      try {
        await page.waitForURL(/\/surveys\/status\//, { timeout: 10000 });
      } catch (_) {
        report.blockingIssue = 'Could not navigate from completed list row to survey result page.';
      }
    }

    if (page.url().includes('/surveys/status/')) {
      await waitForApp(page, 4000);
      report.resultUrl = page.url();
      report.screenshots.result = '/home/senarios/Desktop/survey-bot/survai-platform/e2e-tests/test-results/live-result.png';
      await page.screenshot({ path: report.screenshots.result, fullPage: true });
      report.resultPageText = (await page.textContent('body')) || '';
      report.resultHasSendButton = await page.getByRole('button', { name: 'Send Survey' }).count() > 0;
    }

    console.log(JSON.stringify(report, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
