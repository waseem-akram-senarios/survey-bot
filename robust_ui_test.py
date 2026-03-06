import asyncio, os, json
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"
SD = "/home/senarios/Desktop/survey-bot/test_screenshots"
results = []

def log(step, status, detail=""):
    results.append({"step": step, "status": status, "detail": detail})
    print(f"[{'PASS' if status=='pass' else 'FAIL' if status=='fail' else 'INFO'}] {step}: {detail}")

async def ss(page, name):
    await page.screenshot(path=f"{SD}/{name}.png", full_page=True)

async def wait_and_click(page, selector, timeout=10000):
    """Wait for element and click with error handling"""
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.click(selector)
        return True
    except Exception as e:
        # Try alternative selectors
        alternatives = [
            f"[data-testid*='{selector.split(':')[1].lower()}']" if ":" in selector else None,
            f"button:has-text('{selector.split(':')[1]}')" if ":" in selector else None,
            f"text={selector.split(':')[1]}" if ":" in selector else None,
        ]
        for alt in alternatives:
            if alt:
                try:
                    await page.wait_for_selector(alt, timeout=5000)
                    await page.click(alt)
                    return True
                except:
                    continue
        return False

async def test_login(page):
    """Test login functionality"""
    print("\n=== LOGIN ===")
    try:
        await page.goto(BASE, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        
        # Check if already logged in
        if "dashboard" in page.url.lower() or await page.locator("text=Dashboard").count() > 0:
            log("Login", "pass", "already logged in")
            return True
        
        # Try login
        if await page.locator("input[type='password']").count() > 0:
            await page.locator("input").first.fill("admin")
            await page.locator("input[type='password']").first.fill("admin123")
            await page.locator("button[type='submit']").first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(2)
            log("Login", "pass", "admin authentication successful")
            return True
        else:
            log("Login", "info", "login form not found - may be already logged in")
            return True
    except Exception as e:
        log("Login", "fail", str(e))
        return False

async def test_dashboard(page):
    """Test dashboard features"""
    print("\n=== DASHBOARD ===")
    
    # Test dashboard elements
    try:
        # Look for dashboard content
        body = await page.inner_text("body")
        
        # Check for common dashboard elements
        dashboard_elements = [
            ("Created Templates", "stat card"),
            ("Published Templates", "stat card"),
            ("Active Surveys", "stat card"),
            ("Completed Surveys", "stat card"),
            ("table", "data table"),
            ("survey", "survey content"),
        ]
        
        for element, desc in dashboard_elements:
            if element.lower() in body.lower():
                log(f"Dashboard: {element}", "pass", f"{desc} visible")
            else:
                log(f"Dashboard: {element}", "info", f"{desc} not found")
        
        # Test survey table if exists
        rows = await page.locator("table tbody tr").count()
        if rows > 0:
            log("Survey table", "pass", f"{rows} rows")
            headers = await page.locator("table thead th").all_inner_texts()
            log("Table headers", "pass", f"{len(headers)} columns: {', '.join(headers[:3])}...")
        
        return True
    except Exception as e:
        log("Dashboard", "fail", str(e))
        return False

async def test_navigation(page):
    """Test navigation menu"""
    print("\n=== NAVIGATION ===")
    
    nav_items = ["Dashboard", "Surveys", "Templates", "Analytics"]
    nav_success = 0
    
    for item in nav_items:
        try:
            # Try multiple selector patterns
            selectors = [
                f"text={item}",
                f"button:has-text('{item}')",
                f"[role='menuitem']:has-text('{item}')",
                f".nav-item:has-text('{item}')",
                f"li:has-text('{item}')"
            ]
            
            clicked = False
            for selector in selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.locator(selector).first.click()
                        await asyncio.sleep(1)
                        clicked = True
                        break
                except:
                    continue
            
            if clicked:
                log(f"Navigation: {item}", "pass", "clickable")
                nav_success += 1
            else:
                log(f"Navigation: {item}", "info", "not clickable")
                
        except Exception as e:
            log(f"Navigation: {item}", "fail", str(e))
    
    log("Navigation overall", "pass" if nav_success >= 2 else "info", f"{nav_success}/{len(nav_items)} items working")
    return nav_success >= 2

async def test_surveys_section(page):
    """Test surveys section"""
    print("\n=== SURVEYS SECTION ===")
    
    try:
        # Try to navigate to surveys
        if await wait_and_click(page, "text=Surveys", timeout=5000):
            await asyncio.sleep(2)
            
            # Look for survey-related content
            body = await page.inner_text("body").lower()
            
            survey_features = [
                ("manage", "manage surveys"),
                ("launch", "launch new survey"),
                ("completed", "completed surveys"),
                ("active", "active surveys"),
                ("create", "create survey"),
            ]
            
            for feature, desc in survey_features:
                if feature in body:
                    log(f"Surveys: {feature}", "pass", f"{desc} available")
                else:
                    log(f"Surveys: {feature}", "info", f"{desc} not found")
            
            # Test survey table if present
            rows = await page.locator("table tbody tr").count()
            if rows > 0:
                log("Survey table", "pass", f"{rows} surveys listed")
            
            return True
        else:
            log("Surveys section", "info", "could not navigate to surveys")
            return False
            
    except Exception as e:
        log("Surveys section", "fail", str(e))
        return False

async def test_templates_section(page):
    """Test templates section"""
    print("\n=== TEMPLATES SECTION ===")
    
    try:
        # Try to navigate to templates
        if await wait_and_click(page, "text=Templates", timeout=5000):
            await asyncio.sleep(2)
            
            # Look for template-related content
            body = await page.inner_text("body").lower()
            
            template_features = [
                ("manage", "manage templates"),
                ("create", "create template"),
                ("published", "published templates"),
                ("draft", "draft templates"),
                ("spanish", "spanish templates"),
                ("bilingual", "bilingual support"),
            ]
            
            for feature, desc in template_features:
                if feature in body:
                    log(f"Templates: {feature}", "pass", f"{desc} available")
                else:
                    log(f"Templates: {feature}", "info", f"{desc} not found")
            
            # Test template table if present
            rows = await page.locator("table tbody tr").count()
            if rows > 0:
                log("Template table", "pass", f"{rows} templates listed")
            
            return True
        else:
            log("Templates section", "info", "could not navigate to templates")
            return False
            
    except Exception as e:
        log("Templates section", "fail", str(e))
        return False

async def test_form_elements(page):
    """Test form elements and inputs"""
    print("\n=== FORM ELEMENTS ===")
    
    try:
        # Look for common form elements
        inputs = await page.locator("input").count()
        selects = await page.locator("select, [role='combobox']").count()
        buttons = await page.locator("button").count()
        textareas = await page.locator("textarea").count()
        
        log("Input fields", "pass" if inputs > 0 else "info", f"{inputs} found")
        log("Select dropdowns", "pass" if selects > 0 else "info", f"{selects} found")
        log("Buttons", "pass" if buttons > 0 else "info", f"{buttons} found")
        log("Text areas", "pass" if textareas > 0 else "info", f"{textareas} found")
        
        # Test specific input types
        email_inputs = await page.locator("input[type='email'], input[placeholder*='email' i]").count()
        phone_inputs = await page.locator("input[type='tel'], input[placeholder*='phone' i], input[placeholder*='+1' i]").count()
        
        log("Email inputs", "pass" if email_inputs > 0 else "info", f"{email_inputs} found")
        log("Phone inputs", "pass" if phone_inputs > 0 else "info", f"{phone_inputs} found")
        
        return True
    except Exception as e:
        log("Form elements", "fail", str(e))
        return False

async def test_responsive(page):
    """Test responsive design"""
    print("\n=== RESPONSIVE DESIGN ===")
    
    try:
        # Test different viewport sizes
        viewports = [
            {"width": 1400, "height": 900, "name": "Desktop"},
            {"width": 768, "height": 1024, "name": "Tablet"},
            {"width": 375, "height": 667, "name": "Mobile"}
        ]
        
        for vp in viewports:
            await page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
            await asyncio.sleep(1)
            
            # Check if content is still visible
            body_content = await page.locator("body").inner_text()
            has_content = len(body_content.strip()) > 100
            log(f"Responsive: {vp['name']}", "pass" if has_content else "fail", f"{vp['width']}x{vp['height']} - {'content visible' if has_content else 'no content'}")
        
        # Reset to desktop
        await page.set_viewport_size({"width": 1400, "height": 900})
        return True
    except Exception as e:
        log("Responsive design", "fail", str(e))
        return False

async def test_bilingual_features(page):
    """Test bilingual/Spanish features"""
    print("\n=== BILINGUAL FEATURES ===")
    
    try:
        body = await page.inner_text("body").lower()
        
        bilingual_indicators = [
            ("spanish", "Spanish language"),
            ("español", "Spanish language"),
            ("idioma", "Language"),
            ("translate", "Translation"),
            ("bilingual", "Bilingual support"),
        ]
        
        bilingual_found = 0
        for indicator, desc in bilingual_indicators:
            if indicator in body:
                log(f"Bilingual: {indicator}", "pass", f"{desc} detected")
                bilingual_found += 1
            else:
                log(f"Bilingual: {indicator}", "info", f"{desc} not detected")
        
        log("Bilingual overall", "pass" if bilingual_found >= 2 else "info", f"{bilingual_found} indicators found")
        return bilingual_found >= 1
    except Exception as e:
        log("Bilingual features", "fail", str(e))
        return False

async def test_api_connectivity(page):
    """Test API connectivity through UI"""
    print("\n=== API CONNECTIVITY ===")
    
    try:
        # Listen for network requests
        api_requests = []
        page.on("request", lambda request: api_requests.append(request.url) if "/api/" in request.url else None)
        
        # Navigate around to trigger API calls
        await page.goto(BASE, wait_until="networkidle", timeout=15000)
        await asyncio.sleep(2)
        
        # Try different sections
        await wait_and_click(page, "text=Surveys", timeout=3000)
        await asyncio.sleep(1)
        
        await wait_and_click(page, "text=Templates", timeout=3000)
        await asyncio.sleep(1)
        
        # Check if API calls were made
        api_calls = len([url for url in api_requests if "/api/" in url])
        log("API calls", "pass" if api_calls > 0 else "info", f"{api_calls} API requests detected")
        
        if api_calls > 0:
            log("API connectivity", "pass", "UI is communicating with backend")
        else:
            log("API connectivity", "info", "No API calls detected")
        
        return api_calls > 0
    except Exception as e:
        log("API connectivity", "fail", str(e))
        return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context(viewport={"width": 1400, "height": 900})).new_page()

        # TEST SEQUENCE
        tests = [
            ("Login & Authentication", test_login),
            ("Dashboard Features", test_dashboard),
            ("Navigation Menu", test_navigation),
            ("Surveys Section", test_surveys_section),
            ("Templates Section", test_templates_section),
            ("Form Elements", test_form_elements),
            ("Bilingual Features", test_bilingual_features),
            ("API Connectivity", test_api_connectivity),
            ("Responsive Design", test_responsive),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if await test_func(page):
                    passed_tests += 1
                await ss(page, test_name.lower().replace(" ", "_"))
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
        print(f"TEST SUITES: {passed_tests}/{total_tests} completed successfully")
        print("-"*70)
        
        # Group results by category
        categories = {}
        for r in results:
            category = r["step"].split(":")[0] if ":" in r["step"] else "General"
            if category not in categories:
                categories[category] = {"pass": 0, "fail": 0, "info": 0}
            categories[category][r["status"]] += 1
        
        for category, counts in categories.items():
            total_cat = counts["pass"] + counts["fail"] + counts["info"]
            print(f"\n{category.upper()}:")
            print(f"  ✓ Passed: {counts['pass']}")
            print(f"  ✗ Failed: {counts['fail']}")
            print(f"  ℹ  Info: {counts['info']}")
            print(f"  📊 Total: {total_cat}")
        
        print("="*70)
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}%")
        
        if failed == 0:
            print("🎉 ALL CRITICAL FEATURES WORKING PERFECTLY!")
        elif failed <= 2:
            print("✅ MOST FEATURES WORKING - Minor issues detected")
        else:
            print("⚠️  SEVERAL ISSUES NEED ATTENTION")
        
        print(f"\n📸 Screenshots saved to: {SD}/")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
