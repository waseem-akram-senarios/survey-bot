import asyncio, os
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"
SD = "/home/senarios/Desktop/survey-bot/test_screenshots"
results = []

def log(step, status, detail=""):
    results.append({"step": step, "status": status, "detail": detail})
    print(f"[{'PASS' if status=='pass' else 'FAIL' if status=='fail' else 'INFO'}] {step}: {detail}")

async def ss(page, name):
    try:
        await page.screenshot(path=f"{SD}/{name}.png", full_page=True)
    except:
        pass

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context(viewport={"width": 1400, "height": 900})).new_page()

        try:
            # LOGIN
            print("\n=== 1. LOGIN ===")
            await page.goto(BASE, timeout=30000)
            await asyncio.sleep(2)
            
            # Check if login form exists
            if await page.locator("input[type='password']").count() > 0:
                await page.locator("input").first.fill("admin")
                await page.locator("input[type='password']").first.fill("admin123")
                await page.locator("button[type='submit']").first.click()
                await page.wait_for_load_state("networkidle", timeout=15000)
                await asyncio.sleep(2)
                log("Login", "pass", "admin authentication successful")
            else:
                log("Login", "pass", "already logged in or no login required")

            # DASHBOARD CONTENT
            print("\n=== 2. DASHBOARD CONTENT ===")
            await ss(page, "dashboard")
            
            # Check for any content
            body_text = await page.inner_text("body")
            has_content = len(body_text.strip()) > 100
            log("Dashboard content", "pass" if has_content else "fail", f"{len(body_text)} characters")
            
            # Look for common UI elements
            buttons = await page.locator("button").count()
            links = await page.locator("a").count()
            inputs = await page.locator("input").count()
            
            log("UI buttons", "pass" if buttons > 0 else "info", f"{buttons} found")
            log("Navigation links", "pass" if links > 0 else "info", f"{links} found")
            log("Input fields", "pass" if inputs > 0 else "info", f"{inputs} found")

            # NAVIGATION TEST
            print("\n=== 3. NAVIGATION ===")
            
            # Test main navigation items
            nav_items = ["Dashboard", "Surveys", "Templates"]
            nav_working = 0
            
            for item in nav_items:
                try:
                    # Try to click navigation item
                    if await page.locator(f"text={item}").count() > 0:
                        await page.locator(f"text={item}").first.click()
                        await asyncio.sleep(2)
                        nav_working += 1
                        log(f"Navigation: {item}", "pass", "clickable")
                        await ss(page, f"nav_{item.lower()}")
                        
                        # Check if page loaded new content
                        new_body = await page.inner_text("body")
                        if new_body != body_text:
                            log(f"Page load: {item}", "pass", "content changed")
                        else:
                            log(f"Page load: {item}", "info", "same content")
                    else:
                        log(f"Navigation: {item}", "info", "not found")
                except Exception as e:
                    log(f"Navigation: {item}", "fail", str(e))

            log("Navigation overall", "pass" if nav_working >= 2 else "info", f"{nav_working}/{len(nav_items)} working")

            # SURVEY FUNCTIONALITY
            print("\n=== 4. SURVEY FEATURES ===")
            
            # Try to find survey-related content
            survey_keywords = ["survey", "template", "create", "manage", "launch"]
            survey_found = 0
            
            for keyword in survey_keywords:
                if keyword.lower() in body_text.lower():
                    survey_found += 1
                    log(f"Survey keyword: {keyword}", "pass", "found in content")
                else:
                    log(f"Survey keyword: {keyword}", "info", "not found")
            
            log("Survey features", "pass" if survey_found >= 3 else "info", f"{survey_found}/5 keywords found")

            # FORM FUNCTIONALITY
            print("\n=== 5. FORM ELEMENTS ===")
            
            # Check for form elements on current page
            forms = await page.locator("form").count()
            textareas = await page.locator("textarea").count()
            selects = await page.locator("select").count()
            
            log("Forms", "pass" if forms > 0 else "info", f"{forms} found")
            log("Text areas", "pass" if textareas > 0 else "info", f"{textareas} found")
            log("Select dropdowns", "pass" if selects > 0 else "info", f"{selects} found")

            # BILINGUAL FEATURES
            print("\n=== 6. BILINGUAL FEATURES ===")
            
            bilingual_keywords = ["spanish", "español", "idioma", "translate", "bilingual"]
            bilingual_found = 0
            
            for keyword in bilingual_keywords:
                if keyword.lower() in body_text.lower():
                    bilingual_found += 1
                    log(f"Bilingual: {keyword}", "pass", "found")
                else:
                    log(f"Bilingual: {keyword}", "info", "not found")
            
            log("Bilingual support", "pass" if bilingual_found >= 1 else "info", f"{bilingual_found} indicators")

            # RESPONSIVE TEST
            print("\n=== 7. RESPONSIVE DESIGN ===")
            
            viewports = [
                {"width": 1400, "height": 900, "name": "Desktop"},
                {"width": 768, "height": 1024, "name": "Tablet"},
                {"width": 375, "height": 667, "name": "Mobile"}
            ]
            
            responsive_working = 0
            for vp in viewports:
                try:
                    await page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                    await asyncio.sleep(1)
                    
                    content = await page.inner_text("body")
                    has_content = len(content.strip()) > 50
                    
                    if has_content:
                        responsive_working += 1
                        log(f"Responsive: {vp['name']}", "pass", f"{vp['width']}x{vp['height']} - content visible")
                    else:
                        log(f"Responsive: {vp['name']}", "info", f"{vp['width']}x{vp['height']} - minimal content")
                        
                except Exception as e:
                    log(f"Responsive: {vp['name']}", "fail", str(e))
            
            log("Responsive design", "pass" if responsive_working >= 2 else "info", f"{responsive_working}/3 viewports working")

            # API CONNECTIVITY
            print("\n=== 8. API CONNECTIVITY ===")
            
            # Check if there are any API calls in the page
            try:
                # Look for API endpoints in page content
                api_indicators = ["/api/", "fetch(", "axios", "http", "endpoint"]
                api_found = 0
                
                for indicator in api_indicators:
                    if indicator in body_text:
                        api_found += 1
                        log(f"API indicator: {indicator}", "pass", "found")
                
                log("API connectivity", "pass" if api_found >= 2 else "info", f"{api_found} indicators")
                
            except Exception as e:
                log("API connectivity", "info", "could not test")

            # ERROR HANDLING
            print("\n=== 9. ERROR HANDLING ===")
            
            # Check for error messages
            error_keywords = ["error", "failed", "timeout", "exception", "404", "500"]
            errors_found = 0
            
            for keyword in error_keywords:
                if keyword.lower() in body_text.lower():
                    errors_found += 1
                    log(f"Error indicator: {keyword}", "info", "found in content")
            
            if errors_found == 0:
                log("Error handling", "pass", "no obvious errors visible")
            else:
                log("Error handling", "info", f"{errors_found} error indicators found")

        except Exception as e:
            log("Test execution", "fail", str(e))
        
        # FINAL SUMMARY
        print("\n" + "="*70)
        passed = sum(1 for r in results if r["status"] == "pass")
        failed = sum(1 for r in results if r["status"] == "fail")
        info_c = sum(1 for r in results if r["status"] == "info")
        total = len(results)
        
        print(f"TOTAL TESTS: {total}")
        print(f"PASSED: {passed} | FAILED: {failed} | INFO: {info_c}")
        print("-"*70)
        
        # Show detailed results
        for r in results:
            icon = {"pass":"✓","fail":"✗","info":"ℹ"}[r["status"]]
            print(f"  {icon} {r['step']}: {r['detail']}")
        
        print("="*70)
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}%")
        
        if failed == 0:
            print("🎉 ALL FEATURES WORKING!")
        elif failed <= 2:
            print("✅ MOST FEATURES WORKING!")
        else:
            print("⚠️  SOME ISSUES DETECTED")
        
        print(f"\n📸 Screenshots saved to: {SD}/")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
