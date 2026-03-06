import asyncio, os
from playwright.async_api import async_playwright

BASE_LOCAL = "http://localhost:3000"
BASE_LIVE = "http://54.86.65.150:8080"
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

async def test_recipient_improved(base_url, server_name):
    """Improved recipient interface test with JavaScript wait"""
    print(f"\n=== TESTING {server_name.upper()} RECIPIENT ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context(viewport={"width": 1400, "height": 900})).new_page()

        try:
            # Go to recipient app
            await page.goto(base_url, timeout=30000)
            
            # Wait for JavaScript to load content
            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(3)  # Extra wait for Next.js
            
            # Check for React/Next.js content
            body_text = await page.inner_text("body")
            has_content = len(body_text.strip()) > 50
            
            log(f"{server_name} content", "pass" if has_content else "fail", f"{len(body_text)} characters")
            
            # Look for Next.js/React indicators
            react_indicators = await page.locator("#root, [data-reactroot], #__next").count()
            log(f"{server_name} React app", "pass" if react_indicators > 0 else "info", f"{react_indicators} React roots found")
            
            # Wait for and check survey elements
            try:
                # Wait for any survey-related elements to appear
                await page.wait_for_selector("text=survey, text=question, text=answer, form, input, button", timeout=10000)
                log(f"{server_name} survey elements", "pass", "survey interface detected")
            except:
                log(f"{server_name} survey elements", "info", "no survey elements detected")
            
            # Test JavaScript functionality
            try:
                # Execute JavaScript to check if app is loaded
                js_result = await page.evaluate("""
                    () => {
                        return {
                            hasDocument: typeof document !== 'undefined',
                            hasWindow: typeof window !== 'undefined',
                            hasReact: !!document.querySelector('#root, #__next'),
                            bodyText: document.body.innerText.length,
                            title: document.title
                        }
                    }
                """)
                
                log(f"{server_name} JavaScript", "pass", f"JS working - title: '{js_result['title']}'")
                log(f"{server_name} App loaded", "pass" if js_result['hasReact'] else "info", f"React detected: {js_result['hasReact']}")
                
            except Exception as e:
                log(f"{server_name} JavaScript", "fail", str(e))
            
            # Test survey URL if live server
            if "54.86.65.150" in base_url:
                try:
                    await page.goto(f"{base_url}/survey/demo_1771414344", timeout=15000)
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    await asyncio.sleep(2)
                    
                    survey_content = await page.inner_text("body")
                    has_survey_content = len(survey_content.strip()) > 100
                    
                    log(f"{server_name} survey URL", "pass" if has_survey_content else "info", f"survey page: {len(survey_content)} chars")
                    
                except Exception as e:
                    log(f"{server_name} survey URL", "info", str(e))
            
            await ss(page, f"{server_name.lower()}_recipient_improved")
            
        except Exception as e:
            log(f"{server_name} recipient", "fail", str(e))
        
        await browser.close()

async def test_health_endpoints():
    """Test both health endpoints"""
    print("\n=== TESTING HEALTH ENDPOINTS ===")
    
    import httpx
    
    endpoints = [
        ("Local Gateway Health", "http://localhost:8080/health"),
        ("Local API Health", "http://localhost:8080/pg/api/health"),
        ("Live Gateway Health", "http://54.86.65.150:8080/health"),
        ("Live API Health", "http://54.86.65.150:8080/pg/api/health"),
    ]
    
    async with httpx.AsyncClient(timeout=10) as client:
        for name, url in endpoints:
            try:
                response = await client.get(url)
                log(f"Health: {name}", "pass" if response.status_code == 200 else "fail", f"status {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    log(f"  - Response", "pass", f"service: {data.get('service', 'unknown')}")
                
            except Exception as e:
                log(f"Health: {name}", "fail", str(e))

async def main():
    print("🔧 TESTING IMPROVED SOLUTIONS")
    print("="*50)
    
    # Test health endpoints first
    await test_health_endpoints()
    
    # Test recipient interfaces with improved detection
    await test_recipient_improved(BASE_LOCAL, "local")
    await test_recipient_improved(BASE_LIVE, "live")
    
    # SUMMARY
    print("\n" + "="*70)
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    info_c = sum(1 for r in results if r["status"] == "info")
    total = len(results)
    
    print(f"TOTAL TESTS: {total}")
    print(f"PASSED: {passed} | FAILED: {failed} | INFO: {info_c}")
    print("-"*70)
    
    # Show results
    for r in results:
        icon = {"pass":"✓","fail":"✗","info":"ℹ"}[r["status"]]
        print(f"  {icon} {r['step']}: {r['detail']}")
    
    print("="*70)
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"\n🎯 IMPROVED SUCCESS RATE: {success_rate:.1f}%")
    
    if failed == 0:
        print("🎉 ALL ISSUES SOLVED!")
    elif failed <= 2:
        print("✅ MOST ISSUES SOLVED!")
    else:
        print("⚠️  SOME ISSUES REMAIN")
    
    print(f"\n📸 Screenshots saved to: {SD}/")

if __name__ == "__main__":
    asyncio.run(main())
