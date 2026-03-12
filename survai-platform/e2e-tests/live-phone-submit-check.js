const { chromium } = require('@playwright/test');
const BASE = 'http://54.86.65.150:8080';

async function settle(page, ms = 2000) {
  await page.waitForLoadState('domcontentloaded');
  try { await page.waitForLoadState('networkidle', { timeout: 12000 }); } catch (_) {}
  await page.waitForTimeout(ms);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  const pageErrors = [];
  page.on('pageerror', (err) => pageErrors.push(String(err)));

  await page.goto(BASE);
  await page.evaluate(() => {
    localStorage.setItem('survai_user', JSON.stringify({ username:'admin', role:'admin', tenantId:'itcurves', orgName:'IT Curves' }));
  });
  await page.goto(`${BASE}/surveys/manage`);
  await settle(page, 5000);
  await page.locator('button:has(img[alt="Send Survey"])').first().click();
  await settle(page, 1500);
  await page.getByRole('button', { name: 'Send via Phone' }).click();
  await settle(page, 1500);
  await page.locator('input[type="tel"]').last().fill('+13854036617');
  await page.getByRole('button', { name: 'Send Survey' }).click();

  let message = '';
  const started = Date.now();
  while (Date.now() - started < 20000) {
    const alert = page.locator('[role="alert"]');
    if (await alert.count()) {
      message = ((await alert.first().textContent()) || '').trim();
      if (message) break;
    }
    const body = ((await page.textContent('body')) || '').trim();
    if (/Failed to send survey via phone|sent successfully|Call initiated successfully|Network error|Request timed out|Not found/i.test(body)) {
      message = body.match(/Failed to send survey via phone\. Please try again\.|Survey ".+?" sent successfully to \+?\d+|Call initiated successfully|Network error\. Check that the server is running and the dashboard URL is correct\.|Request timed out\. Try again\.|Not found\. Check template name and try again\./)?.[0] || body.slice(0, 500);
      break;
    }
    await page.waitForTimeout(500);
  }

  const body = ((await page.textContent('body')) || '').trim();
  console.log(JSON.stringify({
    url: page.url(),
    message,
    bodySnippet: body.slice(0, 800),
    blankScreen: body.length === 0,
    pageErrors,
  }, null, 2));

  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
