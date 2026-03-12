const { chromium } = require('@playwright/test');

const BASE = 'http://54.86.65.150:8080';

async function settle(page, ms = 3000) {
  await page.waitForLoadState('domcontentloaded');
  try {
    await page.waitForLoadState('networkidle', { timeout: 12000 });
  } catch (_) {
    // Non-fatal if the app keeps background requests open.
  }
  await page.waitForTimeout(ms);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
  const page = await context.newPage();

  const consoleErrors = [];
  const pageErrors = [];

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  page.on('pageerror', (err) => {
    pageErrors.push(String(err));
  });

  const result = {
    startUrl: '',
    clickedFromUrl: '',
    afterClickUrl: '',
    sendButtonCount: 0,
    dialogVisible: false,
    dialogText: '',
    bodyTextSnippet: '',
    blankScreen: false,
    consoleErrors,
    pageErrors,
    screenshot: '',
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

    await page.goto(`${BASE}/surveys/completed`);
    await settle(page, 5000);
    result.startUrl = page.url();
    result.clickedFromUrl = page.url();

    const sendButtons = page.locator('img[alt="Send Survey"]');
    result.sendButtonCount = await sendButtons.count();

    if (result.sendButtonCount === 0) {
      throw new Error('No Send Survey action found on completed surveys page.');
    }

    await sendButtons.first().click();
    await settle(page, 2500);
    result.afterClickUrl = page.url();

    const dialog = page.locator('[role="dialog"]');
    result.dialogVisible = await dialog.count().then(async (count) => count > 0 && await dialog.first().isVisible()).catch(() => false);
    if (result.dialogVisible) {
      result.dialogText = ((await dialog.first().textContent()) || '').trim();
    }

    const bodyText = ((await page.textContent('body')) || '').trim();
    result.bodyTextSnippet = bodyText.slice(0, 800);
    result.blankScreen = bodyText.length === 0;

    result.screenshot = '/home/senarios/Desktop/survey-bot/survai-platform/e2e-tests/test-results/live-send-action.png';
    await page.screenshot({ path: result.screenshot, fullPage: true });

    console.log(JSON.stringify(result, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
