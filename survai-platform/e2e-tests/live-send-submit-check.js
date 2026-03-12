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

async function openSendModalOnManage(page) {
  await page.goto(`${BASE}/surveys/manage`);
  await settle(page, 5000);
  const rows = page.locator('table tbody tr');
  const rowCount = await rows.count();
  for (let i = 0; i < rowCount; i++) {
    const row = rows.nth(i);
    const text = (await row.textContent()) || '';
    if (/In-Progress/i.test(text)) {
      const btn = row.locator('button:has(img[alt="Send Survey"])').first();
      if (await btn.count()) {
        await btn.click();
        try {
          await page.getByText('Copy link', { exact: true }).waitFor({ timeout: 10000 });
        } catch (_) {}
        await settle(page, 1000);
        return true;
      }
    }
  }
  return false;
}

async function captureVisibleMessage(page, timeout = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    const alert = page.locator('[role="alert"]');
    if (await alert.count()) {
      const text = ((await alert.first().textContent()) || '').trim();
      if (text) return text;
    }
    const dialog = page.locator('[role="dialog"]');
    if (await dialog.count()) {
      const text = ((await dialog.first().textContent()) || '').trim();
      if (/Sending\.\.\.|Email is required|Phone number is required|Please enter a valid email|Phone number must/.test(text)) {
        return text;
      }
    }
    await page.waitForTimeout(500);
  }
  const bodyText = ((await page.textContent('body')) || '').trim();
  return bodyText.slice(0, 400);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
  const page = await context.newPage();

  const result = {
    email: { url: '', message: '', blankScreen: false },
    phone: { url: '', message: '', blankScreen: false },
  };

  try {
    await auth(page);

    const emailOpened = await openSendModalOnManage(page);
    if (!emailOpened) throw new Error('Could not open Send Survey modal for an in-progress survey.');
    result.email.url = page.url();
    await page.getByRole('button', { name: 'Send via Email' }).click();
    await page.getByText('Recipient Email', { exact: true }).waitFor({ timeout: 10000 });
    await settle(page, 500);
    const emailInput = page.locator('input[type="email"]').last();
    await emailInput.fill('waseem@aidevlab.com');
    await page.getByRole('button', { name: /^Send$/ }).click();
    result.email.message = await captureVisibleMessage(page, 20000);
    result.email.blankScreen = (((await page.textContent('body')) || '').trim().length === 0);

    // Re-open modal for phone test.
    const phoneOpened = await openSendModalOnManage(page);
    if (!phoneOpened) throw new Error('Could not reopen Send Survey modal for phone test.');
    result.phone.url = page.url();
    await page.getByRole('button', { name: 'Send via Phone' }).click();
    await page.getByText('Enter Phone Number', { exact: true }).waitFor({ timeout: 10000 });
    await settle(page, 500);
    const phoneInput = page.locator('input[type="tel"]').last();
    await phoneInput.fill('+13854036617');
    await page.getByRole('button', { name: /^Send$/ }).click();
    result.phone.message = await captureVisibleMessage(page, 20000);
    result.phone.blankScreen = (((await page.textContent('body')) || '').trim().length === 0);

    console.log(JSON.stringify(result, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
