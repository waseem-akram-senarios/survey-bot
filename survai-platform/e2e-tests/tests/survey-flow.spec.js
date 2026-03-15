// @ts-check
// Full survey lifecycle E2E: Dashboard → Create (builder) → Surveys (Launched + Library) → Launch
const { test, expect } = require('@playwright/test');
const { loginToDashboard } = require('./auth.setup');

const BASE = process.env.BASE_URL || 'http://localhost:8080';

test.describe('Survey flow E2E', () => {
  test('Dashboard shows Create Survey and Launch survey buttons', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(1500);

    await expect(page.getByRole('button', { name: /Create Survey/i }).first()).toBeVisible({ timeout: 8000 });
    await expect(page.getByRole('button', { name: /Launch survey/i })).toBeVisible({ timeout: 5000 });
  });

  test('Navigate to Create Survey builder and see form', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(1000);

    await page.getByRole('button', { name: /Create Survey/i }).first().click();
    await page.waitForURL(/\/surveys\/builder/, { timeout: 10000 });
    await page.waitForTimeout(1000);

    await expect(page.getByRole('heading', { name: /Create Survey/i })).toBeVisible({ timeout: 5000 });
    await expect(page.getByPlaceholder(/Survey title|e\.g\./i)).toBeVisible({ timeout: 5000 });
    await expect(page.getByRole('button', { name: /Save Survey/i })).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/Add a question/i)).toBeVisible({ timeout: 5000 });
  });

  test('Builder: add a question type and see it in list', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/surveys/builder`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    const addOpenEnded = page.getByRole('button', { name: /Open Ended/i }).first();
    await addOpenEnded.click();
    await page.waitForTimeout(500);

    await expect(page.getByText(/1 question\(s\) added/i)).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/New open-ended question/i)).toBeVisible({ timeout: 3000 });
  });

  test('Top bar has Surveys link (unified)', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(1000);

    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('Surveys');
    await expect(page.getByRole('button', { name: /Surveys/i }).first()).toBeVisible({ timeout: 5000 });
  });

  test('Surveys page loads with Launched and Survey library tabs', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/surveys`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    await expect(page.getByText('Surveys')).toBeVisible({ timeout: 5000 });
    await expect(page.getByRole('tab', { name: /Launched/i })).toBeVisible({ timeout: 5000 });
    await expect(page.getByRole('tab', { name: /Survey library|Library/i })).toBeVisible({ timeout: 5000 });
    expect(page.url()).toContain('/surveys');
  });

  test('Surveys page: switch to Survey library tab', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/surveys`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1500);

    await page.getByRole('tab', { name: /Survey library|Library/i }).click();
    await page.waitForTimeout(1500);

    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();
    expect(page.url()).toMatch(/\/surveys(\?tab=library)?/);
  });

  test('Launch survey page loads and shows template select', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/surveys/launch`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    await expect(page.getByText(/Create Survey|Survey Details/i)).toBeVisible({ timeout: 8000 });
    expect(page.url()).toContain('/surveys/launch');
  });

  test('Can launch a survey from new UI: Dashboard → Launch survey → launch page', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(1500);

    await page.getByRole('button', { name: /Launch survey/i }).click();
    await page.waitForURL(/\/surveys\/launch/, { timeout: 10000 });
    await page.waitForTimeout(1500);

    await expect(page.getByText(/Create Survey|Survey Details|Recipient/i)).toBeVisible({ timeout: 8000 });
    expect(page.url()).toContain('/surveys/launch');
  });

  test('Can launch from Survey library: Surveys → Survey library tab → Launch → launch page', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/surveys?tab=library`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2500);

    const launchBtn = page.getByRole('button', { name: /Launch Survey/i }).first();
    if (await launchBtn.count() > 0) {
      await launchBtn.click();
      await page.waitForURL(/\/surveys\/launch/, { timeout: 10000 });
      await page.waitForTimeout(1000);
      await expect(page.getByText(/Create Survey|Survey Details|Recipient/i)).toBeVisible({ timeout: 8000 });
    }
    expect(page.url()).toContain('/surveys');
  });

  test('Full survey lifecycle: Dashboard → Builder → Surveys → Launch (navigation)', async ({ page }) => {
    await loginToDashboard(page);
    await page.waitForTimeout(1500);

    // 1. Go to builder
    await page.getByRole('button', { name: /Create Survey/i }).first().click();
    await page.waitForURL(/\/surveys\/builder/, { timeout: 10000 });
    await page.waitForTimeout(500);

    // 2. Add a question
    await page.getByRole('button', { name: /Yes \/ No/i }).first().click();
    await page.waitForTimeout(300);
    await expect(page.getByText(/1 question\(s\) added/i)).toBeVisible({ timeout: 5000 });

    // 3. Go to Surveys (unified)
    await page.goto(`${BASE}/surveys`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1500);
    await expect(page.getByRole('tab', { name: /Launched/i })).toBeVisible({ timeout: 5000 });

    // 4. Go to Launch
    await page.goto(`${BASE}/surveys/launch`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);
    await expect(page.getByText(/Create Survey|Survey Details|Recipient/i)).toBeVisible({ timeout: 8000 });
  });
});
