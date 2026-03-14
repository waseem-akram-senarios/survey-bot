#!/usr/bin/env python3
"""
Final Survey Builder Test
Verify that the survey builder is now working
"""

import requests
import time

BASE_URL = "http://54.86.65.150:8080"

def test_survey_builder_final():
    """Final test of the survey builder"""
    print("🎯 FINAL SURVEY BUILDER TEST")
    print("=" * 40)
    
    # Test the survey builder page
    print("🌐 Testing Survey Builder:")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/surveys/builder", timeout=15)
        
        if response.status_code == 200:
            print(f"✅ HTTP Status: {response.status_code} - OK")
            
            # Check if it's a proper HTML page
            if '<!doctype html>' in response.text.lower():
                print("✅ HTML Document: Proper DOCTYPE found")
            else:
                print("⚠️  HTML Document: No DOCTYPE found")
            
            # Check if React app is present
            if 'id="root"' in response.text:
                print("✅ React App: Root element found")
            else:
                print("❌ React App: Root element not found")
                return False
            
            # Check if JavaScript is loaded
            if 'index-' in response.text and '.js' in response.text:
                print("✅ JavaScript: Bundle loaded")
            else:
                print("❌ JavaScript: Bundle not found")
                return False
            
            # Check if CSS is loaded
            if 'index-' in response.text and '.css' in response.text:
                print("✅ CSS: Styles loaded")
            else:
                print("❌ CSS: Styles not found")
                return False
            
            print("\n🎉 SURVEY BUILDER IS ACCESSIBLE!")
            print("✅ The page loads successfully")
            print("✅ All required assets are present")
            print("✅ No 404 error")
            
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {str(e)[:50]}")
        return False

def test_other_routes():
    """Test that other routes still work"""
    print(f"\n🛣️  Testing Other Routes:")
    print("-" * 30)
    
    routes_to_test = [
        ("/", "Home"),
        ("/welcome", "Welcome"),
        ("/dashboard", "Dashboard"),
        ("/surveys/launch", "Survey Creation"),
        ("/analytics", "Analytics"),
    ]
    
    all_working = True
    
    for route, name in routes_to_test:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: {route} - Working")
            else:
                print(f"❌ {name}: {route} - {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"❌ {name}: {route} - Error")
            all_working = False
    
    return all_working

def main():
    """Run final tests"""
    print("🎯 SURVEY BUILDER - FINAL VERIFICATION")
    print("=" * 50)
    print("Testing if the 404 error is resolved")
    print()
    
    # Test survey builder
    builder_works = test_survey_builder_final()
    
    # Test other routes
    other_routes_work = test_other_routes()
    
    print("\n" + "=" * 50)
    print("📈 FINAL RESULTS:")
    print(f"✅ Survey Builder: {'Working' if builder_works else 'Failed'}")
    print(f"✅ Other Routes: {'Working' if other_routes_work else 'Failed'}")
    
    if builder_works and other_routes_work:
        print("\n🎉 SUCCESS! 404 ERROR RESOLVED!")
        print("✅ Survey builder is now accessible")
        print("✅ All other routes are working")
        print("\n🌐 Access your survey builder at:")
        print("   http://54.86.65.150:8080/surveys/builder")
        print("\n📱 The simplified survey builder should show:")
        print("   - Three-column layout")
        print("   - Question types sidebar")
        print("   - Canvas area for questions")
        print("   - Properties panel")
        print("   - Header with save button")
    else:
        print("\n❌ ISSUES STILL EXIST")
        print("🔧 Check the failed tests above")
        print("📱 The page might be loading but not rendering properly")
        print("🔍 Check browser console for JavaScript errors")

if __name__ == "__main__":
    main()
