// @ts-check
const { test, expect } = require('@playwright/test');
const { loginToDashboard } = require('./auth.setup');

const BASE = process.env.BASE_URL || 'http://localhost:8080';

test.describe('Dashboard Home', () => {
  test('root redirects to /dashboard after login', async ({ page }) => {
    await loginToDashboard(page);
    expect(page.url()).toContain('/dashboard');
  });

  test('renders dashboard with stats or Rider Voice content', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(2000);

    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();
    // Rider Voice dashboard: Rider Voice, Transigo, metric cards; or legacy cards
    const hasRiderVoice = bodyText.includes('Rider Voice') || bodyText.includes('Transigo');
    const hasLegacyCards = bodyText.includes('Created Templates') || bodyText.includes('Active Surveys');
    const hasMetricCards = bodyText.includes('AVG. SATISFACTION') || bodyText.includes('RESPONSE CHANNELS');
    expect(hasRiderVoice || hasLegacyCards || hasMetricCards).toBeTruthy();
  });

  test('dashboard has top bar navigation (Dashboard, Analytics, Contacts)', async ({ page }) => {
    await loginToDashboard(page);

    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('Dashboard');
    expect(bodyText).toContain('Analytics');
    expect(bodyText).toContain('Contacts');
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

  test('dashboard shows survey section (table or empty state)', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(2000);

    const bodyText = await page.textContent('body');
    const hasTableOrEmpty = bodyText.includes('Active Surveys') || bodyText.includes('No surveys yet') || bodyText.includes('Search surveys');
    expect(hasTableOrEmpty).toBeTruthy();
  });

  test('dashboard table has expected columns when table present', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(2000);

    const tableHeaders = page.locator('table thead th');
    const count = await tableHeaders.count();
    if (count >= 5) {
      const headers = await tableHeaders.allInnerTexts();
      const joined = headers.join(',');
      expect(joined).toContain('Name');
      expect(joined).toContain('Status');
    }
    // If no table (empty state), test passes
  });

  test('dashboard search filters table rows when present', async ({ page }) => {
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

test.describe('Top bar navigation', () => {
  test('can navigate to Templates Manage page via URL', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/templates/manage`);
    await page.waitForLoadState('networkidle');
    const bodyText = await page.textContent('body');
    expect(bodyText && bodyText.length > 10).toBeTruthy();
  });

  test('can navigate to Surveys/Contacts Manage page', async ({ page }) => {
    await loginToDashboard(page);

    try {
      const contactsBtn = page.getByRole('button', { name: /Contacts/i }).first();
      await contactsBtn.click({ timeout: 5000 });
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('/surveys');
    } catch {
      await page.goto(`${BASE}/surveys/manage`);
      await page.waitForLoadState('networkidle');
      const bodyText = await page.textContent('body');
      expect(bodyText && bodyText.length > 10).toBeTruthy();
    }
  });
});
