#!/usr/bin/env python3
"""Capture screenshots of the current UI (dashboard, surveys, templates) for preview."""
import asyncio
import os
from playwright.async_api import async_playwright

BASE = os.getenv("BASE_URL", "http://localhost:8080")
OUT_DIR = os.path.join(os.path.dirname(__file__), "ui_screenshots")

async def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print(f"Opening {BASE} ...")
        await page.goto(BASE, wait_until="domcontentloaded", timeout=30000)
        # Auth via localStorage (same as e2e) so dashboard loads
        await page.evaluate("""() => {
            localStorage.setItem('survai_user', JSON.stringify({
                username: 'admin', role: 'admin', tenantId: 'itcurves', orgName: 'IT Curves'
            }));
        }""")

        # 1. Dashboard
        await page.goto(f"{BASE}/dashboard", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        await page.screenshot(path=os.path.join(OUT_DIR, "01_dashboard.png"), full_page=True)
        print(f"  Saved {OUT_DIR}/01_dashboard.png")

        # 2. Surveys (manage)
        await page.goto(f"{BASE}/surveys/manage", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        await page.screenshot(path=os.path.join(OUT_DIR, "02_surveys_manage.png"), full_page=True)
        print(f"  Saved {OUT_DIR}/02_surveys_manage.png")

        # 3. Templates
        await page.goto(f"{BASE}/templates/manage", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        await page.screenshot(path=os.path.join(OUT_DIR, "03_templates_manage.png"), full_page=True)
        print(f"  Saved {OUT_DIR}/03_templates_manage.png")

        # 4. Analytics
        await page.goto(f"{BASE}/analytics", wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        await page.screenshot(path=os.path.join(OUT_DIR, "04_analytics.png"), full_page=True)
        print(f"  Saved {OUT_DIR}/04_analytics.png")

        await browser.close()

    print(f"\nDone. Open the images in: {OUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
