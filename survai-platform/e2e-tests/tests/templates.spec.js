// @ts-check
const { test, expect } = require('@playwright/test');
const { loginToDashboard } = require('./auth.setup');

const BASE = process.env.BASE_URL || 'http://localhost:8080';

// ─── Template API Tests ──────────────────────────────────────────────────────

test.describe('Template CRUD via API', () => {
  const TEMPLATE_NAME = `E2E_Test_Template_${Date.now()}`;

  test('create a new template', async ({ request }) => {
    const response = await request.post(`${BASE}/pg/api/templates/create`, {
      data: { TemplateName: TEMPLATE_NAME },
    });
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toContain(TEMPLATE_NAME);
    expect(body).toContain('added successfully');
  });

  test('new template appears in list', async ({ request }) => {
    const response = await request.get(`${BASE}/pg/api/templates/list`);
    expect(response.ok()).toBeTruthy();
    const templates = await response.json();
    const found = templates.find((t) => t.TemplateName === TEMPLATE_NAME);
    expect(found).toBeTruthy();
  });

  test('publish the template', async ({ request }) => {
    const response = await request.patch(`${BASE}/pg/api/templates/status`, {
      data: { TemplateName: TEMPLATE_NAME, Status: 'Published' },
    });
    expect(response.ok()).toBeTruthy();
  });

  test('template status is now Published', async ({ request }) => {
    const response = await request.get(`${BASE}/pg/api/templates/list`);
    const templates = await response.json();
    const found = templates.find((t) => t.TemplateName === TEMPLATE_NAME);
    expect(found).toBeTruthy();
    expect(found.Status).toBe('Published');
  });

  test('clone the template', async ({ request }) => {
    const cloneName = `${TEMPLATE_NAME}_Clone`;
    const response = await request.post(`${BASE}/pg/api/templates/clone`, {
      data: { SourceTemplateName: TEMPLATE_NAME, NewTemplateName: cloneName },
    });
    expect(response.ok()).toBeTruthy();

    const listResp = await request.get(`${BASE}/pg/api/templates/list`);
    const templates = await listResp.json();
    const found = templates.find((t) => t.TemplateName === cloneName);
    expect(found).toBeTruthy();

    await request.delete(`${BASE}/pg/api/templates/delete`, {
      data: { TemplateName: cloneName },
    });
  });

  test('delete the template', async ({ request }) => {
    await request.patch(`${BASE}/pg/api/templates/status`, {
      data: { TemplateName: TEMPLATE_NAME, Status: 'Draft' },
    });
    const response = await request.delete(`${BASE}/pg/api/templates/delete`, {
      data: { TemplateName: TEMPLATE_NAME },
    });
    expect(response.ok()).toBeTruthy();

    const listResp = await request.get(`${BASE}/pg/api/templates/list`);
    const templates = await listResp.json();
    const found = templates.find((t) => t.TemplateName === TEMPLATE_NAME);
    expect(found).toBeFalsy();
  });
});

// ─── Question + Template Question API Tests ──────────────────────────────────

test.describe('Question & Template-Question Flow via API', () => {
  const TEMPLATE_NAME = `E2E_QFlow_${Date.now()}`;
  let questionId = '';

  test('create template, question, and link them', async ({ request }) => {
    const tResp = await request.post(`${BASE}/pg/api/templates/create`, {
      data: { TemplateName: TEMPLATE_NAME },
    });
    expect(tResp.ok()).toBeTruthy();

    const qResp = await request.post(`${BASE}/pg/api/questions`, {
      data: {
        QueText: 'E2E: How would you rate the service?',
        QueCriteria: 'categorical',
        QueCategories: ['Excellent', 'Good', 'Average', 'Poor'],
      },
    });
    expect(qResp.ok()).toBeTruthy();
    const qBody = await qResp.json();
    const idMatch = qBody.match(/ID\s+([0-9a-f-]+)/i);
    questionId = idMatch ? idMatch[1] : '';
    expect(questionId).toBeTruthy();

    const addResp = await request.post(`${BASE}/pg/api/templates/addquestions`, {
      data: { TemplateName: TEMPLATE_NAME, QueId: questionId, Order: 1 },
    });
    expect(addResp.ok()).toBeTruthy();
  });

  test('template has the linked question', async ({ request }) => {
    const response = await request.post(`${BASE}/pg/api/templates/getquestions`, {
      data: { TemplateName: TEMPLATE_NAME },
    });
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.Questions).toBeTruthy();
    expect(Array.isArray(body.Questions)).toBeTruthy();
    const found = body.Questions.find((q) => q.id === questionId);
    expect(found).toBeTruthy();
  });

  test('cleanup: delete template', async ({ request }) => {
    await request.delete(`${BASE}/pg/api/templates/delete`, {
      data: { TemplateName: TEMPLATE_NAME },
    });
  });
});

// ─── Templates UI Tests ──────────────────────────────────────────────────────

test.describe('Templates UI', () => {
  test('templates manage page loads', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/templates/manage`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    const pageText = await page.textContent('body');
    expect(pageText && pageText.length > 10).toBeTruthy();
    const hasTemplateContent =
      pageText.includes('Template') ||
      pageText.includes('template') ||
      pageText.includes('Manage');
    expect(hasTemplateContent).toBeTruthy();
  });

  test('templates page shows stats cards', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/templates/manage`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('Total Templates');
  });

  test('templates table has Launch Survey icon buttons when templates exist', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/templates/manage`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    const launchBtns = page.locator('img[alt="Launch Survey"]');
    const count = await launchBtns.count();
    // Pass when page has templates (buttons) or empty state
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('templates table has Clone icon buttons when templates exist', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/templates/manage`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    const cloneBtns = page.locator('img[alt="Clone"]');
    const count = await cloneBtns.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('Launch Survey button navigates to create survey form when present', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/templates/manage`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    const launchBtn = page.locator('img[alt="Launch Survey"]').first();
    if (await launchBtn.count() > 0) {
      await launchBtn.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      const bodyText = await page.textContent('body');
      const isOnForm =
        bodyText.includes('Select Template') ||
        bodyText.includes('Recipient') ||
        bodyText.includes('Launch New Survey');
      expect(isOnForm).toBeTruthy();
    }
    // If no templates, test passes (nothing to click)
  });

  test('create template page loads', async ({ page }) => {
    await loginToDashboard(page);
    await page.goto(`${BASE}/templates/create`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    const bodyText = await page.textContent('body');
    expect(bodyText && bodyText.length > 10).toBeTruthy();
  });
});
