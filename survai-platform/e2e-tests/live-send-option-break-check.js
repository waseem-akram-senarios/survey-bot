const { chromium } = require('@playwright/test');
const BASE = 'http://54.86.65.150:8080';

async function settle(page, ms = 2000) {
  await page.waitForLoadState('domcontentloaded');
  try { await page.waitForLoadState('networkidle', { timeout: 12000 }); } catch (_) {}
  await page.waitForTimeout(ms);
}

async function auth(page) {
  await page.goto(BASE);
  await page.evaluate(() => {
    localStorage.setItem('survai_user', JSON.stringify({ username:'admin', role:'admin', tenantId:'itcurves', orgName:'IT Curves' }));
  });
}

async function run(optionName) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', (msg) => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', (err) => pageErrors.push(String(err)));
  await auth(page);
  await page.goto(`${BASE}/surveys/manage`);
  await settle(page, 5000);
  await page.locator('button:has(img[alt="Send Survey"])').first().click();
  await settle(page, 1500);
  await page.getByRole('button', { name: optionName }).click();
  await settle(page, 2000);
  const body = ((await page.textContent('body')) || '');
  const result = {
    optionName,
    url: page.url(),
    title: await page.title(),
    bodyLength: body.trim().length,
    bodySnippet: body.trim().slice(0, 500),
    consoleErrors,
    pageErrors,
  };
  await browser.close();
  return result;
}

(async () => {
  const email = await run('Send via Email');
  const phone = await run('Send via Phone');
  console.log(JSON.stringify({ email, phone }, null, 2));
})().catch((e) => { console.error(e); process.exit(1); });
