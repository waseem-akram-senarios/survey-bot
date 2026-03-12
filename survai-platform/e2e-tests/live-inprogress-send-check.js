const { chromium } = require('@playwright/test');

const BASE = 'http://54.86.65.150:8080';

async function settle(page, ms = 2500) {
  await page.waitForLoadState('domcontentloaded');
  try {
    await page.waitForLoadState('networkidle', { timeout: 12000 });
  } catch (_) {}
  await page.waitForTimeout(ms);
}

async function auth(page) {
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
}

async function inspectSend(page, url, sendLocatorFactory) {
  const consoleErrors = [];
  const pageErrors = [];
  const onConsole = (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  };
  const onPageError = (err) => pageErrors.push(String(err));
  page.on('console', onConsole);
  page.on('pageerror', onPageError);

  await page.goto(url);
  await settle(page, 4000);
  const beforeUrl = page.url();
  const sendLocator = sendLocatorFactory();
  const sendCount = await sendLocator.count();
  let clicked = false;
  let dialogVisible = false;
  let dialogText = '';

  if (sendCount > 0) {
    await sendLocator.first().click();
    clicked = true;
    await settle(page, 2500);
    const dialog = page.locator('[role="dialog"]');
    dialogVisible = await dialog.count().then(async (c) => c > 0 && await dialog.first().isVisible()).catch(() => false);
    if (dialogVisible) dialogText = ((await dialog.first().textContent()) || '').trim();
  }

  const bodyText = ((await page.textContent('body')) || '').trim();
  const result = {
    url,
    beforeUrl,
    afterUrl: page.url(),
    sendCount,
    clicked,
    dialogVisible,
    dialogText,
    blankScreen: bodyText.length === 0,
    visibleError: /error|something went wrong|failed/i.test(bodyText),
    consoleErrors,
    pageErrors,
  };

  page.off('console', onConsole);
  page.off('pageerror', onPageError);
  return result;
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
  const page = await context.newPage();

  try {
    await auth(page);

    const dashboard = await inspectSend(
      page,
      `${BASE}/dashboard`,
      () => page.locator('img[alt="Send Survey"]')
    );

    const manage = await inspectSend(
      page,
      `${BASE}/surveys/manage`,
      () => page.locator('img[alt="Send Survey"]')
    );

    await page.goto(`${BASE}/surveys/manage`);
    await settle(page, 4000);
    const rows = page.locator('table tbody tr');
    const rowCount = await rows.count();
    let detail = {
      url: '',
      beforeUrl: '',
      afterUrl: '',
      sendCount: 0,
      clicked: false,
      dialogVisible: false,
      dialogText: '',
      blankScreen: false,
      visibleError: false,
      consoleErrors: [],
      pageErrors: [],
    };

    for (let i = 0; i < rowCount; i++) {
      const row = rows.nth(i);
      const rowText = ((await row.textContent()) || '');
      if (/In-Progress/i.test(rowText)) {
        await row.locator('td').first().click();
        await page.waitForURL(/\/surveys\/status\//, { timeout: 10000 });
        await settle(page, 4000);
        detail = await inspectSend(
          page,
          page.url(),
          () => page.getByRole('button', { name: 'Send Survey' })
        );
        break;
      }
    }

    console.log(JSON.stringify({ dashboard, manage, detail }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
