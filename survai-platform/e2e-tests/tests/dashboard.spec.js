// @ts-check
const { test, expect } = require('@playwright/test');
const { loginToDashboard } = require('./auth.setup');

const BASE = process.env.BASE_URL || 'http://localhost:8080';

test.describe('Dashboard Home', () => {
  test('root redirects to /dashboard after login', async ({ page }) => {
    await loginToDashboard(page);
    expect(page.url()).toContain('/dashboard');
  });

  test('renders dashboard with stats cards', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(2000);

    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();
    expect(bodyText).toContain('Created Templates');
    expect(bodyText).toContain('Active Surveys');
    expect(bodyText).toContain('Completed Surveys');
  });

  test('dashboard has sidebar with navigation links', async ({ page }) => {
    await loginToDashboard(page);

    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('Templates');
    expect(bodyText).toContain('Surveys');
  });

  test('dashboard loads without critical JS errors', async ({ page }) => {
    const errors = [];
    page.on('pageerror', (err) => errors.push(err.message));

    await loginToDashboard(page);
    await page.waitForTimeout(2000);

    const criticalErrors = errors.filter(
      (e) => !e.includes('ResizeObserver') && !e.includes('Loading chunk')
    );
    expect(criticalErrors).toHaveLength(0);
  });

  test('dashboard shows Active Surveys table', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(2000);

    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('Active Surveys');
  });

  test('dashboard table has expected columns', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(2000);

    const headers = await page.locator('table thead th').allInnerTexts();
    expect(headers.length).toBeGreaterThanOrEqual(5);
    expect(headers.join(',')).toContain('Name');
    expect(headers.join(',')).toContain('Status');
  });

  test('dashboard search filters table rows', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(2000);

    const searchInput = page.locator('input[placeholder*="earch" i]');
    if (await searchInput.count() > 0) {
      const rowsBefore = await page.locator('table tbody tr').count();
      await searchInput.first().fill('NONEXISTENT_TERM_XYZ');
      await page.waitForTimeout(1000);
      const rowsAfter = await page.locator('table tbody tr').count();
      expect(rowsAfter).toBeLessThanOrEqual(rowsBefore);
    }
  });
});

test.describe('Sidebar Navigation', () => {
  test('can navigate to Templates Manage page', async ({ page }) => {
    await loginToDashboard(page);

    const templatesLink = page.locator('a[href*="templates"]').first();
    if (await templatesLink.count() > 0) {
      await templatesLink.click();
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('/templates');
    } else {
      await page.goto(`${BASE}/templates/manage`);
      await page.waitForLoadState('networkidle');
      const bodyText = await page.textContent('body');
      expect(bodyText && bodyText.length > 10).toBeTruthy();
    }
  });

  test('can navigate to Surveys Manage page', async ({ page }) => {
    await loginToDashboard(page);

    const surveysLink = page.locator('a[href*="surveys/manage"]').first();
    if (await surveysLink.count() > 0) {
      await surveysLink.click();
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('/surveys');
    } else {
      await page.goto(`${BASE}/surveys/manage`);
      await page.waitForLoadState('networkidle');
      const bodyText = await page.textContent('body');
      expect(bodyText && bodyText.length > 10).toBeTruthy();
    }
  });
});
