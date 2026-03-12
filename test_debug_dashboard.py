#!/usr/bin/env python3
"""
Debug Dashboard Test Script
Tests step-by-step to find the rendering issue
"""

import requests
import time

def test_dashboard_debug():
    """Debug dashboard rendering step by step"""
    print("🔍 Debugging Dashboard Step by Step")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Step 1: Check HTML structure
    print("\n📋 Step 1: HTML Structure")
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            checks = {
                "DOCTYPE": "<!doctype html" in content.lower(),
                "HTML Tag": "<html" in content.lower(),
                "Head Tag": "<head>" in content.lower(),
                "Body Tag": "<body>" in content.lower(),
                "Root Div": '<div id="root">' in content,
                "Script Tag": "<script" in content.lower(),
                "CSS Link": "<link" in content.lower()
            }
            
            for check, result in checks.items():
                if result:
                    print(f"   ✅ {check}: Found")
                else:
                    print(f"   ❌ {check}: Missing")
                    
            print(f"   📄 Content length: {len(content)} characters")
        else:
            print(f"❌ HTML failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HTML test failed: {str(e)}")
        return False
    
    # Step 2: Check static assets
    print("\n📦 Step 2: Static Assets")
    try:
        js_response = requests.get(f"{base_url}/assets/index-DVVC57pj.js", timeout=10)
        css_response = requests.get(f"{base_url}/assets/index-7DyOx3AN.css", timeout=10)
        
        print(f"   📄 JS: {js_response.status_code} ({len(js_response.content)} bytes)")
        print(f"   📄 CSS: {css_response.status_code} ({len(css_response.content)} bytes)")
        
        # Check if dashboard text is in JS
        js_content = js_response.text
        if "🎉 Survey Bot Dashboard" in js_content:
            print("   ✅ Dashboard text found in JS")
        else:
            print("   ❌ Dashboard text not found in JS")
            
    except Exception as e:
        print(f"❌ Assets test failed: {str(e)}")
    
    # Step 3: Check API connectivity
    print("\n🔌 Step 3: API Connectivity")
    try:
        api_response = requests.get(f"{base_url}/pg/api/health", timeout=10)
        if api_response.status_code == 200:
            print("   ✅ API Gateway: Working")
        else:
            print(f"   ❌ API Gateway: {api_response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
    
    # Step 4: Test root page (to see if React is working at all)
    print("\n🏠 Step 4: Root Page Test")
    try:
        root_response = requests.get(f"{base_url}/", timeout=10)
        if root_response.status_code == 200:
            root_content = root_response.text
            if root_content == content:
                print("   ⚠️ Root and Dashboard return same content")
            else:
                print("   ✅ Root and Dashboard have different content")
                print(f"   📄 Root length: {len(root_content)} characters")
        else:
            print(f"   ❌ Root failed: {root_response.status_code}")
    except Exception as e:
        print(f"❌ Root test failed: {str(e)}")
    
    # Step 5: Check for potential JavaScript errors
    print("\n⚠️ Step 5: Potential Issues")
    print("   🔍 Common causes of blank page:")
    print("      1. JavaScript errors in browser console")
    print("      2. React component mounting issues")
    print("      3. CSS not loading properly")
    print("      4. API calls failing and causing errors")
    print("      5. ProtectedRoute blocking access")
    
    # Step 6: Suggest debugging steps
    print("\n🛠️ Step 6: Debugging Suggestions")
    print("   📱 Open browser and go to: http://localhost:8080/dashboard")
    print("   🔧 Press F12 to open Developer Tools")
    print("   📋 Check Console tab for JavaScript errors")
    print("   📋 Check Network tab for failed requests")
    print("   📋 Check Elements tab if #root div is empty")
    
    return True

def main():
    """Main debug function"""
    print("🚀 Dashboard Debug Tool")
    print("=" * 50)
    
    success = test_dashboard_debug()
    
    print("\n" + "=" * 50)
    print("🔍 DEBUG RESULTS:")
    print("=" * 50)
    
    if success:
        print("✅ Basic structure is correct")
        print("🔧 Issue is likely in JavaScript execution")
        print("📱 Check browser console for specific errors")
        print("\n💡 Next steps:")
        print("   1. Open http://localhost:8080/dashboard in browser")
        print("   2. Press F12 for Developer Tools")
        print("   3. Check Console tab for errors")
        print("   4. Look for 'DashboardSimple' component errors")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
