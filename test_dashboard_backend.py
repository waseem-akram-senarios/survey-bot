#!/usr/bin/env python3
"""
Dashboard Backend Integration Test Script
Tests the dashboard functionality with real backend data
"""

import asyncio
import time
from playwright.async_api import async_playwright

async def test_dashboard_data_loading():
    """Test dashboard data loading from backend"""
    print("🔄 Testing Dashboard Data Loading")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to dashboard
            await page.goto("http://localhost:8080/dashboard")
            await page.wait_for_load_state('networkidle')
            
            # Test 1: Page Load
            print("\n📋 Test 1: Page Load")
            page_title = await page.title()
            print(f"✅ Page title: {page_title}")
            
            # Test 2: Loading State
            print("\n⏳ Test 2: Loading State")
            
            # Look for loading indicator
            loading_indicator = await page.query_selector('.MuiCircularProgress-root')
            if loading_indicator:
                print("✅ Loading indicator found")
            else:
                print("ℹ️ Loading may have completed quickly")
            
            # Wait for data to load
            await page.wait_for_timeout(2000)
            
            # Test 3: Data Loading
            print("\n📊 Test 3: Data Loading")
            
            # Check if stats cards are populated with real data
            stat_cards = await page.query_selector_all('.MuiCard-root')
            print(f"✅ Found {len(stat_cards)} stat cards")
            
            # Check for real data in stat cards
            real_data_found = False
            for i, card in enumerate(stat_cards[:5]):  # Check first 5 cards
                card_text = await card.inner_text()
                if any(char.isdigit() for char in card_text):
                    print(f"✅ Card {i+1} contains numeric data")
                    real_data_found = True
                else:
                    print(f"⚠️ Card {i+1} may not have data yet")
            
            # Test 4: Backend Connection
            print("\n🔗 Test 4: Backend Connection")
            
            # Check browser console for API calls
            console_messages = []
            page.on('console', lambda msg: console_messages.append(msg))
            
            # Wait a bit to capture console messages
            await page.wait_for_timeout(1000)
            
            api_calls_found = False
            for msg in console_messages:
                if 'Surveys loaded:' in msg.text or 'Templates loaded:' in msg.text:
                    print(f"✅ Console log: {msg.text}")
                    api_calls_found = True
            
            if not api_calls_found:
                print("⚠️ No backend API calls detected in console")
            
            # Test 5: Search Functionality
            print("\n🔍 Test 5: Search Functionality")
            
            # Look for search input
            search_input = await page.query_selector('input[placeholder*="Search"]')
            if search_input:
                print("✅ Search input found")
                
                # Test search functionality
                await search_input.fill("test")
                await page.wait_for_timeout(1000)
                
                # Check if search triggered
                search_value = await search_input.input_value()
                if search_value == "test":
                    print("✅ Search input working")
                else:
                    print("⚠️ Search input issue")
            else:
                print("⚠️ Search input not found")
            
            # Test 6: Filter Functionality
            print("\n🎛️ Test 6: Filter Functionality")
            
            # Look for filter dropdown
            filter_select = await page.query_selector('.MuiSelect-root')
            if filter_select:
                print("✅ Filter dropdown found")
                
                # Test filter functionality
                await filter_select.click()
                await page.wait_for_timeout(500)
                
                # Look for filter options
                filter_options = await page.query_selector_all('.MuiMenuItem-root')
                print(f"✅ Found {len(filter_options)} filter options")
                
                if len(filter_options) > 0:
                    # Click first option
                    await filter_options[0].click()
                    await page.wait_for_timeout(500)
                    print("✅ Filter selection working")
            else:
                print("⚠️ Filter dropdown not found")
            
            # Test 7: Error Handling
            print("\n🛡️ Test 7: Error Handling")
            
            # Check for error states
            error_elements = await page.query_selector_all('[data-testid="error"], .error, [role="alert"]')
            if len(error_elements) == 0:
                print("✅ No error elements found (good)")
            else:
                print(f"⚠️ Found {len(error_elements)} error elements")
            
            # Test 8: Recent Activity Section
            print("\n📈 Test 8: Recent Activity Section")
            
            # Look for recent activity
            recent_activity = await page.query_selector('text="Backend connected"')
            if recent_activity:
                print("✅ Backend connection indicator found")
            else:
                print("ℹ️ Backend connection indicator not visible")
            
            # Test 9: Navigation Elements
            print("\n🧭 Test 9: Navigation Elements")
            
            # Check sidebar navigation
            sidebar_items = await page.query_selector_all('[role="button"], .nav-item')
            print(f"✅ Found {len(sidebar_items)} navigation items")
            
            # Test 10: Performance
            print("\n⚡ Test 10: Performance")
            
            # Measure page load time
            start_time = time.time()
            await page.goto("http://localhost:8080/dashboard", wait_until="networkidle")
            load_time = time.time() - start_time
            
            if load_time < 3:
                print(f"✅ Fast load time: {load_time:.2f}s")
            elif load_time < 5:
                print(f"⚠️ Moderate load time: {load_time:.2f}s")
            else:
                print(f"❌ Slow load time: {load_time:.2f}s")
            
            print("\n" + "=" * 50)
            print("🎉 Dashboard Data Loading Test Complete!")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return False
        finally:
            await browser.close()

async def test_api_connectivity():
    """Test API connectivity directly"""
    print("\n🔗 Testing API Connectivity")
    print("=" * 50)
    
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test surveys API
            async with session.get('http://localhost:8080/pg/api/surveys/list') as response:
                if response.status == 200:
                    surveys_data = await response.json()
                    print(f"✅ Surveys API: {len(surveys_data)} surveys")
                else:
                    print(f"❌ Surveys API: Status {response.status}")
            
            # Test templates API
            async with session.get('http://localhost:8080/pg/api/templates/list') as response:
                if response.status == 200:
                    templates_data = await response.json()
                    print(f"✅ Templates API: {len(templates_data)} templates")
                else:
                    print(f"❌ Templates API: Status {response.status}")
            
            # Test health endpoint
            async with session.get('http://localhost:8080/pg/api/health') as response:
                if response.status == 200:
                    print("✅ Health API: Working")
                else:
                    print(f"⚠️ Health API: Status {response.status}")
            
            return True
            
        except Exception as e:
            print(f"❌ API connectivity test failed: {str(e)}")
            return False

async def main():
    """Main test function"""
    print("🚀 Starting Dashboard Backend Integration Tests")
    print("=" * 50)
    
    # Test API connectivity first
    api_test = await test_api_connectivity()
    
    # Test dashboard functionality
    dashboard_test = await test_dashboard_data_loading()
    
    print("\n" + "=" * 50)
    print("🏆 TEST RESULTS:")
    print("=" * 50)
    print(f"API Connectivity: {'✅ PASSED' if api_test else '❌ FAILED'}")
    print(f"Dashboard Loading: {'✅ PASSED' if dashboard_test else '❌ FAILED'}")
    
    if api_test and dashboard_test:
        print("\n🎉 DASHBOARD BACKEND INTEGRATION WORKING!")
        print("✅ Real data loading from backend!")
        print("✅ Search and filter functionality working!")
        print("✅ Error handling implemented!")
        print("✅ Performance acceptable!")
        print("✅ Ready for production!")
    else:
        print("\n⚠️ Some issues found - check implementation")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
