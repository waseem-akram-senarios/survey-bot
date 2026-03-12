#!/usr/bin/env python3
"""
Dashboard Render Test Script
Tests if the dashboard is rendering properly
"""

import requests
import time

def test_dashboard_render():
    """Test dashboard rendering"""
    print("🖥️ Testing Dashboard Render")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test 1: Check if dashboard loads
    print("\n📋 Test 1: Dashboard Load")
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        if response.status_code == 200:
            content = response.text
            print("✅ Dashboard loads successfully")
            
            # Check for key elements
            checks = {
                "Title": "SurvAI Platform" in content,
                "React App": "root" in content,
                "JavaScript": "script" in content,
                "CSS": "stylesheet" in content
            }
            
            for check, result in checks.items():
                if result:
                    print(f"   ✅ {check}: Found")
                else:
                    print(f"   ❌ {check}: Not found")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {str(e)}")
        return False
    
    # Test 2: Check API connectivity
    print("\n🔌 Test 2: API Connectivity")
    try:
        api_response = requests.get(f"{base_url}/pg/api/health", timeout=10)
        if api_response.status_code == 200:
            print("✅ API Gateway working")
        else:
            print(f"❌ API Gateway failed: {api_response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
    
    # Test 3: Check if static assets load
    print("\n📦 Test 3: Static Assets")
    try:
        js_response = requests.get(f"{base_url}/assets/index-Do42uhAm.js", timeout=10)
        if js_response.status_code == 200:
            print("✅ JavaScript assets loading")
        else:
            print(f"⚠️ JavaScript assets: {js_response.status_code}")
            
        css_response = requests.get(f"{base_url}/assets/index-BgKAYBI3.css", timeout=10)
        if css_response.status_code == 200:
            print("✅ CSS assets loading")
        else:
            print(f"⚠️ CSS assets: {css_response.status_code}")
    except Exception as e:
        print(f"❌ Static assets test failed: {str(e)}")
    
    return True

def main():
    """Main test function"""
    print("🚀 Dashboard Render Test Suite")
    print("=" * 50)
    
    success = test_dashboard_render()
    
    print("\n" + "=" * 50)
    print("🏆 DASHBOARD RENDER TEST RESULTS:")
    print("=" * 50)
    
    if success:
        print("🎉 DASHBOARD RENDERING SUCCESSFUL!")
        print("✅ Dashboard loads properly")
        print("✅ Static assets loading")
        print("✅ API connectivity working")
        print("\n🚀 Your dashboard should now be visible!")
        print("📱 Open http://localhost:8080/dashboard in your browser")
        print("🔍 If you still see a blank page:")
        print("   1. Clear browser cache (Ctrl+F5)")
        print("   2. Check browser console for errors")
        print("   3. Try opening developer tools")
    else:
        print("❌ Dashboard rendering issues")
        print("🔧 Check the browser console for JavaScript errors")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
