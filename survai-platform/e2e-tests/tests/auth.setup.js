// @ts-check
const { test, expect } = require('@playwright/test');

const BASE = process.env.BASE_URL || 'http://localhost:8080';

/**
 * Logs into the dashboard by setting localStorage auth token,
 * then navigating so the SPA picks it up.
 */
async function loginToDashboard(page) {
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
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
}

module.exports = { loginToDashboard };
