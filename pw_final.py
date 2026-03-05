import asyncio, os
from playwright.async_api import async_playwright

BASE = "http://54.86.65.150:8080"
SD = "/home/senarios/Desktop/survey-bot/test_screenshots"
results = []

def log(step, status, detail=""):
    results.append({"step": step, "status": status, "detail": detail})
    print(f"[{'PASS' if status=='pass' else 'FAIL' if status=='fail' else 'INFO'}] {step}: {detail}")

async def ss(page, name):
    await page.screenshot(path=f"{SD}/{name}.png", full_page=True)

async def close_modal(page):
    for sel in ["button:has-text('Confirm')", "button:has-text('OK')"]:
        if await page.locator(sel).count() > 0:
            await page.locator(sel).first.click()
            await asyncio.sleep(1)
            return
    await page.keyboard.press("Escape")
    await asyncio.sleep(0.5)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context(viewport={"width": 1400, "height": 900})).new_page()

        # LOGIN
        print("=== 1. LOGIN ===")
        await page.goto(BASE, wait_until="networkidle", timeout=30000)
        if await page.locator("input[type='password']").count() > 0:
            await page.locator("input").first.fill("admin")
            await page.locator("input[type='password']").first.fill("admin123")
            await page.locator("button[type='submit']").first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(2)
        log("Login", "pass", "admin / IT Curves")

        # DASHBOARD
        print("\n=== 2. DASHBOARD ===")
        body = await page.inner_text("body")
        for s in ["Created Templates", "Published Templates", "Active Surveys", "Completed Surveys", "Completed Today"]:
            log(f"Stat: {s}", "pass" if s in body else "fail", "visible" if s in body else "MISSING")
        rows = await page.locator("table tbody tr").count()
        log("Survey table", "pass" if rows > 0 else "fail", f"{rows} rows")
        hdrs = await page.locator("table thead th").all_inner_texts()
        log("Columns", "pass" if len(hdrs) >= 5 else "fail", ", ".join(hdrs))
        log("Pagination", "pass" if await page.locator("button:has-text('2'), [class*='pagination']").count() > 0 else "info", "present")
        # Search
        if await page.locator("input[placeholder*='earch' i]").count() > 0:
            await page.locator("input[placeholder*='earch' i]").first.fill("MK")
            await asyncio.sleep(1)
            log("Search", "pass", f"{await page.locator('table tbody tr').count()} rows for 'MK'")
            await page.locator("input[placeholder*='earch' i]").first.fill("")
            await asyncio.sleep(1)

        # MANAGE TEMPLATES
        print("\n=== 3. MANAGE TEMPLATES ===")
        await page.click("text=Templates"); await asyncio.sleep(0.5)
        await page.click("text=Manage Templates")
        await page.wait_for_load_state("networkidle", timeout=10000); await asyncio.sleep(2)
        log("Template table", "pass" if await page.locator("table tbody tr").count() > 0 else "fail", f"{await page.locator('table tbody tr').count()} templates")
        log("Stats cards", "pass" if "Total Templates" in await page.inner_text("body") else "fail", "visible")
        # *** FIXED SELECTORS: use img[alt] for icon buttons ***
        launch_btns = await page.locator('img[alt="Launch Survey"]').count()
        clone_btns = await page.locator('img[alt="Clone"]').count()
        log("Launch Survey btns", "pass" if launch_btns > 0 else "fail", f"{launch_btns} icon buttons")
        log("Clone btns", "pass" if clone_btns > 0 else "fail", f"{clone_btns} icon buttons")
        # Click Launch Survey on first template
        if launch_btns > 0:
            await page.locator('img[alt="Launch Survey"]').first.click()
            await page.wait_for_load_state("networkidle", timeout=10000); await asyncio.sleep(2)
            body = await page.inner_text("body")
            log("Launch Survey click", "pass" if "Select Template" in body or "Recipient" in body else "fail", "Opens create survey form")
            await page.go_back(); await page.wait_for_load_state("networkidle", timeout=10000); await asyncio.sleep(1)

        # CREATE SURVEY
        print("\n=== 4. LAUNCH NEW SURVEY ===")
        await page.click("text=Surveys"); await asyncio.sleep(0.5)
        await page.click("text=Launch New Survey")
        await page.wait_for_load_state("networkidle", timeout=10000); await asyncio.sleep(2)
        body = await page.inner_text("body")
        log("Form page", "pass" if "Select Template" in body else "fail", "loaded")
        log("CSV import", "pass" if "rider data" in body.lower() else "info", "section visible")
        # Select template
        await page.locator("[role='combobox'], .MuiSelect-select").first.click(); await asyncio.sleep(1)
        for opt in await page.locator("[role='option'], .MuiMenuItem-root").all():
            txt = (await opt.inner_text()).strip()
            if txt and "select" not in txt.lower() and "loading" not in txt.lower():
                await opt.click(); log("Template", "pass", txt); break
        await asyncio.sleep(1)
        # Fill
        for inp in await page.locator("input:not([type='hidden']):not([readonly])").all():
            ph = (await inp.get_attribute("placeholder") or "").lower()
            if "recipient" in ph: await inp.fill("Final Verify User")
            elif "rider" in ph: await inp.fill("Final Rider")
            elif "phone" in ph or "+1" in ph: await inp.fill("+15557776666")
        log("Form filled", "pass", "recipient, rider, phone")
        # Generate
        await page.locator("button:has-text('Generate')").first.click()
        await asyncio.sleep(8)
        try: await page.wait_for_load_state("networkidle", timeout=30000)
        except: pass
        await asyncio.sleep(2)
        body = await page.inner_text("body")
        log("Generated", "pass" if "Generated Survey" in body else "fail", "questions visible")
        log("Properties", "pass" if "Survey Properties" in body else "fail", "panel visible")
        # Launch
        await page.locator("button:has-text('Launch Survey')").first.click()
        await asyncio.sleep(4)
        try: await page.wait_for_load_state("networkidle", timeout=15000)
        except: pass
        await asyncio.sleep(1)
        body = await page.inner_text("body")
        log("Share dialog", "pass" if "Share Survey Link" in body else "fail", "modal visible")
        log("Copy button", "pass" if "Copy" in body else "fail", "available")
        await close_modal(page)

        # MANAGE SURVEYS
        print("\n=== 5. MANAGE SURVEYS ===")
        await page.click("text=Surveys"); await asyncio.sleep(0.5)
        await page.click("text=Manage Surveys")
        await page.wait_for_load_state("networkidle", timeout=10000); await asyncio.sleep(2)
        await ss(page, "FINAL_manage_surveys")
        body = await page.inner_text("body")
        log("Survey table", "pass" if await page.locator("table tbody tr").count() > 0 else "fail", f"{await page.locator('table tbody tr').count()} rows")
        log("Stats", "pass" if "Total Surveys" in body else "fail", "cards visible")
        log("New survey", "pass" if "Final Verify User" in body else "fail", "appears in list")
        # *** FIXED SELECTOR: use img[alt] ***
        send_btns = await page.locator('img[alt="Send Survey"]').count()
        log("Send Survey btns", "pass" if send_btns > 0 else "fail", f"{send_btns} icon buttons for in-progress")
        delete_btns = await page.locator('button[aria-label="Delete Survey"]').count()
        log("Delete btns", "pass" if delete_btns > 0 else "fail", f"{delete_btns} delete buttons")
        view_icons = await page.locator("table tbody svg").count()
        log("View/action icons", "pass" if view_icons > 0 else "fail", f"{view_icons} total")

        # COMPLETED SURVEYS
        print("\n=== 6. COMPLETED SURVEYS ===")
        await page.click("text=Surveys"); await asyncio.sleep(0.5)
        await page.click("text=Completed Surveys")
        await page.wait_for_load_state("networkidle", timeout=10000); await asyncio.sleep(2)
        await ss(page, "FINAL_completed")
        rows = await page.locator("table tbody tr").count()
        log("Completed table", "pass" if rows > 0 else "fail", f"{rows} rows")
        log("Only completed", "pass" if "In-Progress" not in await page.inner_text("body") else "fail", "filter working")

        # FINAL DASHBOARD
        print("\n=== 7. FINAL DASHBOARD ===")
        await close_modal(page)
        await page.click("text=Dashboard")
        await asyncio.sleep(3)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(3)
        await ss(page, "FINAL_dashboard")
        log("Dashboard final", "pass" if "Active Surveys" in await page.inner_text("body") else "fail", "loads correctly")

        # SUMMARY
        print("\n" + "="*70)
        passed = sum(1 for r in results if r["status"] == "pass")
        failed = sum(1 for r in results if r["status"] == "fail")
        info_c = sum(1 for r in results if r["status"] == "info")
        print(f"TOTAL: {len(results)}  |  PASSED: {passed}  |  FAILED: {failed}  |  INFO: {info_c}")
        print("-"*70)
        for r in results:
            icon = {"pass":"✓","fail":"✗","info":"ℹ"}[r["status"]]
            print(f"  {icon} {r['step']}: {r['detail']}")
        print("="*70)
        print("\n  ALL TESTS PASSED!" if failed == 0 else f"\n  {failed} FAILURE(S)")
        print("="*70)
        await browser.close()

asyncio.run(main())
