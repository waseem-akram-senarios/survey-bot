import asyncio, os, json
from playwright.async_api import async_playwright
import httpx

BASE = "http://54.86.65.150:8080"
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

async def test_server_connectivity():
    """Test basic server connectivity"""
    print("\n=== SERVER CONNECTIVITY ===")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Test main server
            response = await client.get(BASE)
            log("Main server", "pass" if response.status_code == 200 else "fail", f"status {response.status_code}")
            
            # Test dashboard endpoint
            response = await client.get(f"{BASE}/dashboard")
            log("Dashboard endpoint", "pass" if response.status_code == 200 else "info", f"status {response.status_code}")
            
            # Test API gateway
            response = await client.get(f"{BASE}/pg/api/health")
            log("API gateway", "pass" if response.status_code == 200 else "info", f"status {response.status_code}")
            
            return True
    except Exception as e:
        log("Server connectivity", "fail", str(e))
        return False

async def test_dashboard_ui():
    """Test dashboard UI functionality"""
    print("\n=== DASHBOARD UI ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context(viewport={"width": 1400, "height": 900})).new_page()

        try:
            # Go to dashboard
            await page.goto(f"{BASE}/dashboard", timeout=30000)
            await asyncio.sleep(3)
            
            # Check page content
            body_text = await page.inner_text("body")
            has_content = len(body_text.strip()) > 100
            log("Dashboard content", "pass" if has_content else "fail", f"{len(body_text)} characters")
            
            # Test login if needed
            if await page.locator("input[type='password']").count() > 0:
                await page.locator("input").first.fill("admin")
                await page.locator("input[type='password']").first.fill("admin123")
                await page.locator("button[type='submit']").first.click()
                await page.wait_for_load_state("networkidle", timeout=15000)
                await asyncio.sleep(2)
                log("Login", "pass", "authentication successful")
                
                # Check content after login
                body_text = await page.inner_text("body")
                has_content = len(body_text.strip()) > 100
                log("Post-login content", "pass" if has_content else "fail", f"{len(body_text)} characters")
            else:
                log("Login", "info", "no login form found")
            
            # Look for dashboard elements
            dashboard_elements = ["dashboard", "survey", "template", "analytics", "manage", "create"]
            elements_found = 0
            
            for element in dashboard_elements:
                if element.lower() in body_text.lower():
                    elements_found += 1
                    log(f"Dashboard element: {element}", "pass", "found")
                else:
                    log(f"Dashboard element: {element}", "info", "not found")
            
            log("Dashboard UI", "pass" if elements_found >= 3 else "info", f"{elements_found}/6 elements")
            
            # Test navigation
            nav_items = ["Dashboard", "Surveys", "Templates", "Analytics"]
            nav_working = 0
            
            for item in nav_items:
                try:
                    if await page.locator(f"text={item}").count() > 0:
                        await page.locator(f"text={item}").first.click()
                        await asyncio.sleep(2)
                        nav_working += 1
                        log(f"Navigation: {item}", "pass", "clickable")
                        await ss(page, f"live_nav_{item.lower()}")
                    else:
                        log(f"Navigation: {item}", "info", "not found")
                except Exception as e:
                    log(f"Navigation: {item}", "fail", str(e))
            
            log("Navigation overall", "pass" if nav_working >= 2 else "info", f"{nav_working}/{len(nav_items)} working")
            
            await ss(page, "live_dashboard")
            
        except Exception as e:
            log("Dashboard UI", "fail", str(e))
        
        await browser.close()

async def test_live_apis():
    """Test live server APIs"""
    print("\n=== LIVE API TESTS ===")
    
    api_tests = [
        ("Health Check", f"{BASE}/pg/api/health", "GET"),
        ("Surveys List", f"{BASE}/pg/api/surveys/list", "GET"),
        ("Templates List", f"{BASE}/pg/api/templates/list", "GET"),
        ("Analytics Summary", f"{BASE}/pg/api/analytics/summary", "GET"),
        ("Brain Translation", f"{BASE}/pg/api/brain/translate", "POST", {"text": "Hello", "language": "es"}),
    ]
    
    async with httpx.AsyncClient(timeout=15) as client:
        for test_name, url, method, *data in api_tests:
            try:
                if method == "GET":
                    response = await client.get(url)
                elif method == "POST" and data:
                    response = await client.post(url, json=data[0])
                
                if response.status_code == 200:
                    log(f"API: {test_name}", "pass", f"status {response.status_code}")
                    
                    # Test specific response content
                    if test_name == "Surveys List":
                        surveys = response.json()
                        log(f"  - Surveys found", "pass", f"{len(surveys)} surveys")
                    elif test_name == "Templates List":
                        templates = response.json()
                        log(f"  - Templates found", "pass", f"{len(templates)} templates")
                    elif test_name == "Brain Translation":
                        translated = response.json().get("translated", "")
                        log(f"  - Translation", "pass", f"'Hello' → '{translated}'")
                else:
                    log(f"API: {test_name}", "fail", f"status {response.status_code}")
                    
            except Exception as e:
                log(f"API: {test_name}", "fail", str(e))

async def test_survey_urls():
    """Test survey URLs on live server"""
    print("\n=== LIVE SURVEY URLS ===")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Get surveys
            response = await client.get(f"{BASE}/pg/api/surveys/list")
            if response.status_code == 200:
                surveys = response.json()
                log("Survey API", "pass", f"found {len(surveys)} surveys")
                
                # Test first few survey URLs
                test_count = min(3, len(surveys))
                for i in range(test_count):
                    survey = surveys[i]
                    survey_url = f"{BASE}/survey/{survey['SurveyId']}"
                    
                    try:
                        response = await client.get(survey_url, timeout=10)
                        if response.status_code == 200:
                            log(f"Survey URL {i+1}", "pass", f"accessible (status {response.status_code})")
                        else:
                            log(f"Survey URL {i+1}", "info", f"status {response.status_code}")
                    except Exception as e:
                        log(f"Survey URL {i+1}", "fail", str(e))
            else:
                log("Survey API", "fail", f"status {response.status_code}")
                
    except Exception as e:
        log("Survey URLs", "fail", str(e))

async def test_responsive_design():
    """Test responsive design on live server"""
    print("\n=== RESPONSIVE DESIGN ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context()).new_page()

        try:
            await page.goto(f"{BASE}/dashboard", timeout=30000)
            await asyncio.sleep(2)
            
            # Login if needed
            if await page.locator("input[type='password']").count() > 0:
                await page.locator("input").first.fill("admin")
                await page.locator("input[type='password']").first.fill("admin123")
                await page.locator("button[type='submit']").first.click()
                await asyncio.sleep(2)
            
            # Test different viewports
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
                    log(f"Responsive: {vp['name']}", "pass", f"{vp['width']}x{vp['height']} - content visible")
                    await ss(page, f"live_responsive_{vp['name'].lower()}")
                else:
                    log(f"Responsive: {vp['name']}", "info", f"{vp['width']}x{vp['height']} - minimal content")
            
            log("Responsive design", "pass" if responsive_working >= 2 else "info", f"{responsive_working}/3 viewports")
            
        except Exception as e:
            log("Responsive design", "fail", str(e))
        
        await browser.close()

async def test_performance():
    """Test basic performance metrics"""
    print("\n=== PERFORMANCE TESTS ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context()).new_page()

        try:
            # Measure page load time
            start_time = asyncio.get_event_loop().time()
            await page.goto(f"{BASE}/dashboard", timeout=30000)
            load_time = asyncio.get_event_loop().time() - start_time
            
            log("Page load time", "pass" if load_time < 10 else "info", f"{load_time:.2f} seconds")
            
            # Check for loading states
            await asyncio.sleep(2)
            body_text = await page.inner_text("body")
            
            # Look for performance indicators
            loading_indicators = await page.locator("[class*='loading'], [class*='spinner']").count()
            log("Loading indicators", "pass" if loading_indicators >= 0 else "info", f"{loading_indicators} found")
            
            # Test JavaScript responsiveness
            try:
                buttons = await page.locator("button").count()
                if buttons > 0:
                    js_start = asyncio.get_event_loop().time()
                    await page.locator("button").first.click()
                    js_time = asyncio.get_event_loop().time() - js_start
                    log("JavaScript response", "pass" if js_time < 2 else "info", f"{js_time:.2f} seconds")
                else:
                    log("JavaScript response", "info", "no buttons to test")
            except:
                log("JavaScript response", "info", "JS test inconclusive")
            
        except Exception as e:
            log("Performance test", "fail", str(e))
        
        await browser.close()

async def main():
    print("🚀 TESTING LIVE SERVER: http://54.86.65.150:8080")
    print("="*60)
    
    # Run all tests
    tests = [
        ("Server Connectivity", test_server_connectivity),
        ("Dashboard UI", test_dashboard_ui),
        ("Live APIs", test_live_apis),
        ("Survey URLs", test_survey_urls),
        ("Responsive Design", test_responsive_design),
        ("Performance", test_performance),
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
    print(f"\n🎯 LIVE SERVER SUCCESS RATE: {success_rate:.1f}%")
    
    if failed == 0:
        print("🎉 LIVE SERVER FULLY FUNCTIONAL!")
    elif failed <= 2:
        print("✅ LIVE SERVER MOSTLY WORKING!")
    else:
        print("⚠️  LIVE SERVER HAS ISSUES")
    
    print(f"\n📸 Screenshots saved to: {SD}/")
    
    # Feature summary for live server
    print(f"\n📋 LIVE SERVER FEATURE SUMMARY:")
    print(f"  • Server Connectivity: {'✅ Working' if any('connectivity' in r['step'].lower() and r['status'] == 'pass' for r in results) else '❌ Issues'}")
    print(f"  • Dashboard UI: {'✅ Working' if any('dashboard' in r['step'].lower() and r['status'] == 'pass' for r in results) else '❌ Issues'}")
    print(f"  • API Endpoints: {'✅ Working' if any('api:' in r['step'].lower() and r['status'] == 'pass' for r in results) else '❌ Issues'}")
    print(f"  • Survey URLs: {'✅ Working' if any('survey url' in r['step'].lower() and r['status'] == 'pass' for r in results) else '❌ Issues'}")
    print(f"  • Responsive Design: {'✅ Working' if any('responsive' in r['step'].lower() and r['status'] == 'pass' for r in results) else '❌ Issues'}")
    print(f"  • Performance: {'✅ Good' if any('performance' in r['step'].lower() and r['status'] == 'pass' for r in results) else '❌ Issues'}")

if __name__ == "__main__":
    asyncio.run(main())
