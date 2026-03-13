// @ts-check
const BASE = process.env.BASE_URL || 'http://localhost:8080';

/**
 * Logs into the dashboard by setting localStorage auth token,
 * then navigating. If login page is shown, submits credentials.
 * Waits for dashboard content to be visible.
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
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(2000);

  // If we're on login page (auth required), submit credentials
  const url = page.url();
  if (url.includes('/login') || (await page.locator('input[type="password"]').count()) > 0) {
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('admin123');
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL(/\/(dashboard)?(\?|$)/, { timeout: 10000 });
    await page.waitForTimeout(1500);
  }

  // Wait for dashboard content (Rider Voice, nav, or stats)
  await page.waitForFunction(
    () => {
      const body = document.body?.innerText || '';
      return (
        body.includes('Rider Voice') ||
        body.includes('Dashboard') ||
        body.includes('Analytics') ||
        body.includes('Contacts')
      );
    },
    { timeout: 15000 }
  );
  await page.waitForTimeout(500);
}

module.exports = { loginToDashboard };
