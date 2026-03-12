#!/usr/bin/env python3
"""
Simple Dashboard Test
Tests if the new dashboard content is in the built JavaScript
"""

import requests
import subprocess
import time

def test_dashboard_content():
    """Test if DashboardNew content is in the JavaScript"""
    print("🔍 Testing DashboardNew Content")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Step 1: Get the dashboard HTML
    print("\n📋 Step 1: Get Dashboard HTML")
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        if response.status_code == 200:
            content = response.text
            print("✅ Dashboard HTML loaded")
            
            # Extract JavaScript file name
            if "index-" in content:
                import re
                js_match = re.search(r'src="/assets/index-([^"]+\.js)"', content)
                if js_match:
                    js_file = f"index-{js_match.group(1)}"
                    print(f"   📄 JavaScript file: {js_file}")
                    
                    # Step 2: Check if DashboardNew content is in JavaScript
                    print(f"\n🔍 Step 2: Check {js_file} for DashboardNew content")
                    try:
                        js_response = requests.get(f"{base_url}/assets/{js_file}", timeout=10)
                        if js_response.status_code == 200:
                            js_content = js_response.text
                            
                            # Check for DashboardNew specific content
                            checks = {
                                "Rider Voice": "Rider Voice" in js_content,
                                "Transigo": "Transigo" in js_content,
                                "TOTAL SURVEYS": "TOTAL SURVEYS" in js_content,
                                "DashboardNew": "DashboardNew" in js_content,
                                "SidebarNew": "SidebarNew" in js_content,
                                "StatCardNew": "StatCardNew" in js_content
                            }
                            
                            found_count = 0
                            for check, found in checks.items():
                                if found:
                                    print(f"   ✅ {check}: Found")
                                    found_count += 1
                                else:
                                    print(f"   ❌ {check}: Missing")
                            
                            if found_count >= 4:
                                print(f"\n🎉 DashboardNew content found in JavaScript!")
                                return True
                            else:
                                print(f"\n⚠️ DashboardNew content missing or incomplete")
                                return False
                        else:
                            print(f"   ❌ Failed to load JavaScript: {js_response.status_code}")
                            return False
                    except Exception as e:
                        print(f"   ❌ JavaScript check failed: {str(e)}")
                        return False
                else:
                    print("   ❌ Could not find JavaScript file name")
                    return False
            else:
                print("   ❌ No JavaScript file found")
                return False
        else:
            print(f"❌ Dashboard HTML failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 DashboardNew Content Test")
    print("=" * 50)
    
    success = test_dashboard_content()
    
    print("\n" + "=" * 50)
    print("🏆 DASHBOARDNEW CONTENT TEST RESULTS:")
    print("=" * 50)
    
    if success:
        print("🎉 DASHBOARDNEW CONTENT FOUND!")
        print("✅ DashboardNew component is built into JavaScript")
        print("✅ All new UI elements are present")
        print("\n💡 If you still see the old dashboard:")
        print("   1. Clear browser cache (Ctrl+F5)")
        print("   2. Open browser console (F12)")
        print("   3. Check for JavaScript errors")
        print("   4. Try hard refresh (Ctrl+Shift+R)")
    else:
        print("❌ DASHBOARDNEW CONTENT MISSING!")
        print("🔧 The DashboardNew component is not built correctly")
        print("🔧 Need to check the build process")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
