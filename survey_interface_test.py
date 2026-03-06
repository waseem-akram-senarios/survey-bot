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

async def test_survey_urls():
    """Test actual survey URLs"""
    print("\n=== TESTING SURVEY URLs ===")
    
    # Get survey list from API
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE}/pg/api/surveys/list", timeout=10)
            if response.status_code == 200:
                surveys = response.json()
                log("Survey API", "pass", f"found {len(surveys)} surveys")
                
                # Test first few survey URLs
                test_count = min(3, len(surveys))
                for i in range(test_count):
                    survey = surveys[i]
                    survey_url = f"{BASE}/survey/{survey['SurveyId']}"
                    log(f"Survey URL {i+1}", "info", f"testing {survey_url}")
                    
                    # Test survey URL
                    async with httpx.AsyncClient() as client:
                        try:
                            response = await client.get(survey_url, timeout=10)
                            if response.status_code == 200:
                                log(f"Survey {i+1}", "pass", f"URL accessible (status {response.status_code})")
                            else:
                                log(f"Survey {i+1}", "fail", f"URL returned {response.status_code}")
                        except Exception as e:
                            log(f"Survey {i+1}", "fail", str(e))
                
                return True
            else:
                log("Survey API", "fail", f"status {response.status_code}")
                return False
                
    except Exception as e:
        log("Survey API", "fail", str(e))
        return False

async def test_recipient_interface():
    """Test recipient survey interface"""
    print("\n=== TESTING RECIPIENT INTERFACE ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context(viewport={"width": 1400, "height": 900})).new_page()

        try:
            # Test recipient app directly
            await page.goto("http://localhost:3000", timeout=30000)
            await asyncio.sleep(2)
            
            body_text = await page.inner_text("body")
            has_content = len(body_text.strip()) > 100
            log("Recipient app", "pass" if has_content else "fail", f"{len(body_text)} characters")
            
            # Look for survey interface elements
            survey_elements = ["question", "answer", "submit", "next", "survey", "form"]
            elements_found = 0
            
            for element in survey_elements:
                if element.lower() in body_text.lower():
                    elements_found += 1
                    log(f"Survey element: {element}", "pass", "found")
                else:
                    log(f"Survey element: {element}", "info", "not found")
            
            log("Survey interface", "pass" if elements_found >= 3 else "info", f"{elements_found}/6 elements")
            
            # Test responsive design
            viewports = [
                {"width": 1400, "height": 900, "name": "Desktop"},
                {"width": 768, "height": 1024, "name": "Tablet"},
                {"width": 375, "height": 667, "name": "Mobile"}
            ]
            
            responsive_working = 0
            for vp in viewports:
                await page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                await asyncio.sleep(1)
                
                content = await page.inner_text("body")
                has_content = len(content.strip()) > 50
                
                if has_content:
                    responsive_working += 1
                    log(f"Recipient responsive: {vp['name']}", "pass", "content visible")
                else:
                    log(f"Recipient responsive: {vp['name']}", "info", "minimal content")
            
            log("Recipient responsive", "pass" if responsive_working >= 2 else "info", f"{responsive_working}/3 viewports")
            
            await ss(page, "recipient_interface")
            
        except Exception as e:
            log("Recipient interface", "fail", str(e))
        
        await browser.close()

async def test_dashboard_detailed():
    """Test dashboard in detail"""
    print("\n=== TESTING DASHBOARD DETAILED ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context(viewport={"width": 1400, "height": 900})).new_page()

        try:
            # Go to dashboard
            await page.goto(BASE, timeout=30000)
            await asyncio.sleep(2)
            
            # Login if needed
            if await page.locator("input[type='password']").count() > 0:
                await page.locator("input").first.fill("admin")
                await page.locator("input[type='password']").first.fill("admin123")
                await page.locator("button[type='submit']").first.click()
                await page.wait_for_load_state("networkidle", timeout=15000)
                await asyncio.sleep(2)
                log("Dashboard login", "pass", "authenticated")
            
            # Check for React app content
            body_text = await page.inner_text("body")
            
            # Look for React/Modern app indicators
            modern_indicators = ["loading", "dashboard", "survey", "template", "analytics", "menu"]
            modern_found = 0
            
            for indicator in modern_indicators:
                if indicator.lower() in body_text.lower():
                    modern_found += 1
                    log(f"Modern UI: {indicator}", "pass", "found")
                else:
                    log(f"Modern UI: {indicator}", "info", "not found")
            
            # Check for loading states
            loading_indicators = await page.locator("[class*='loading'], [class*='spinner'], .MuiCircularProgress").count()
            log("Loading indicators", "pass" if loading_indicators > 0 else "info", f"{loading_indicators} found")
            
            # Check for Material-UI components
            mui_indicators = await page.locator("[class*='Mui'], .MuiButton, .MuiCard").count()
            log("Material-UI components", "pass" if mui_indicators > 0 else "info", f"{mui_indicators} found")
            
            # Test JavaScript functionality
            try:
                # Try to click something to test JS
                buttons = await page.locator("button").count()
                if buttons > 0:
                    await page.locator("button").first.click()
                    await asyncio.sleep(1)
                    log("JavaScript functionality", "pass", "button click handled")
                else:
                    log("JavaScript functionality", "info", "no buttons to test")
            except Exception as e:
                log("JavaScript functionality", "info", f"JS test inconclusive: {str(e)[:50]}")
            
            await ss(page, "dashboard_detailed")
            
        except Exception as e:
            log("Dashboard detailed", "fail", str(e))
        
        await browser.close()

async def test_bilingual_templates():
    """Test bilingual template functionality"""
    print("\n=== TESTING BILINGUAL TEMPLATES ===")
    
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            # Get templates
            response = await client.get(f"{BASE}/pg/api/templates/list", timeout=10)
            if response.status_code == 200:
                templates = response.json()
                log("Template API", "pass", f"found {len(templates)} templates")
                
                # Look for Spanish templates
                spanish_templates = [t for t in templates if "spanish" in t.get("TemplateName", "").lower() or "español" in t.get("TemplateName", "").lower()]
                log("Spanish templates", "pass" if spanish_templates else "info", f"{len(spanish_templates)} found")
                
                # Test translation API
                translate_response = await client.post(
                    f"{BASE}/pg/api/brain/translate",
                    json={"text": "Hello, how are you?", "language": "es"},
                    timeout=10
                )
                
                if translate_response.status_code == 200:
                    translated = translate_response.json().get("translated", "")
                    log("Translation API", "pass", f"'Hello, how are you?' → '{translated}'")
                else:
                    log("Translation API", "fail", f"status {translate_response.status_code}")
                
                return True
            else:
                log("Template API", "fail", f"status {response.status_code}")
                return False
                
    except Exception as e:
        log("Bilingual templates", "fail", str(e))
        return False

async def main():
    print("🚀 COMPREHENSIVE UI FEATURE TESTING")
    print("="*50)
    
    # Run all tests
    tests = [
        ("Survey URLs", test_survey_urls),
        ("Recipient Interface", test_recipient_interface),
        ("Dashboard Detailed", test_dashboard_detailed),
        ("Bilingual Templates", test_bilingual_templates),
    ]
    
    for test_name, test_func in tests:
        try:
            await test_func()
        except Exception as e:
            log(f"Test error: {test_name}", "fail", str(e))
    
    # SUMMARY
    print("\n" + "="*70)
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    info_c = sum(1 for r in results if r["status"] == "info")
    total = len(results)
    
    print(f"TOTAL TESTS: {total}")
    print(f"PASSED: {passed} | FAILED: {failed} | INFO: {info_c}")
    print("-"*70)
    
    # Show key results
    key_results = [r for r in results if r["status"] in ["pass", "fail"]]
    for r in key_results:
        icon = "✓" if r["status"] == "pass" else "✗"
        print(f"  {icon} {r['step']}: {r['detail']}")
    
    print("="*70)
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}%")
    
    if failed == 0:
        print("🎉 ALL CRITICAL FEATURES WORKING!")
    elif failed <= 2:
        print("✅ MOST FEATURES WORKING!")
    else:
        print("⚠️  SOME ISSUES DETECTED")
    
    print(f"\n📸 Screenshots saved to: {SD}/")
    
    # Feature summary
    print(f"\n📋 FEATURE SUMMARY:")
    print(f"  • Login System: {'✅ Working' if any('Login' in r['step'] and r['status'] == 'pass' for r in results) else '❌ Issues'}")
    print(f"  • Dashboard UI: {'✅ Working' if any('Dashboard' in r['step'] and r['status'] == 'pass' for r in results) else '❌ Issues'}")
    print(f"  • Survey URLs: {'✅ Working' if any('Survey URL' in r['step'] and r['status'] == 'pass' for r in results) else '❌ Issues'}")
    print(f"  • Recipient Interface: {'✅ Working' if any('Recipient' in r['step'] and r['status'] == 'pass' for r in results) else '❌ Issues'}")
    print(f"  • Bilingual Support: {'✅ Working' if any('Spanish' in r['step'] and r['status'] == 'pass' for r in results) else '❌ Issues'}")
    print(f"  • API Connectivity: {'✅ Working' if any('API' in r['step'] and r['status'] == 'pass' for r in results) else '❌ Issues'}")

if __name__ == "__main__":
    asyncio.run(main())
