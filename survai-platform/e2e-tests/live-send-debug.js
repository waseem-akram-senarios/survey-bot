const { chromium } = require('@playwright/test');
const BASE = 'http://54.86.65.150:8080';

async function settle(page, ms = 3000) {
  await page.waitForLoadState('domcontentloaded');
  try { await page.waitForLoadState('networkidle', { timeout: 12000 }); } catch (_) {}
  await page.waitForTimeout(ms);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  await page.goto(BASE);
  await page.evaluate(() => {
    localStorage.setItem('survai_user', JSON.stringify({ username:'admin', role:'admin', tenantId:'itcurves', orgName:'IT Curves' }));
  });
  await page.goto(`${BASE}/surveys/manage`);
  await settle(page, 5000);
  const btn = page.locator('button:has(img[alt="Send Survey"])').first();
  await btn.click();
  await settle(page, 2000);
  await page.getByRole('button', { name: 'Send via Phone' }).click();
  await settle(page, 1500);
  const body = ((await page.textContent('body')) || '').trim();
  const buttons = await page.locator('button').evaluateAll((els) => els.map((e) => e.textContent.trim()));
  const inputs = await page.locator('input').evaluateAll((els) => els.map((e) => ({ type: e.type, placeholder: e.placeholder, value: e.value })));
  console.log(JSON.stringify({ url: page.url(), hasPhonePrompt: body.includes('Enter Phone Number'), body: body.slice(0, 1600), buttons, inputs }, null, 2));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
