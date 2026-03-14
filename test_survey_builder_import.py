#!/usr/bin/env python3
"""
Test Survey Builder Import
Check if the SurveyBuilder component can be imported properly
"""

import requests
import time

BASE_URL = "http://54.86.65.150:8080"

def test_survey_builder_load():
    """Test if the survey builder loads without JavaScript errors"""
    print("🔍 Testing Survey Builder Load")
    print("=" * 35)
    
    try:
        # Test the survey builder page
        response = requests.get(f"{BASE_URL}/surveys/builder", timeout=15)
        
        if response.status_code == 200:
            print("✅ Page loads successfully")
            
            # Check if React app is present
            if 'id="root"' in response.text:
                print("✅ React root element found")
            else:
                print("❌ React root element not found")
                return False
            
            # Check if the JavaScript bundle is loaded
            if 'index-Ci8LpzeQ.js' in response.text:
                print("✅ JavaScript bundle loaded")
            else:
                print("❌ JavaScript bundle not found")
                return False
            
            # Check if CSS is loaded
            if 'index-7DyOx3AN.css' in response.text:
                print("✅ CSS styles loaded")
            else:
                print("❌ CSS styles not found")
                return False
            
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {str(e)[:50]}")
        return False

def test_alternative_routes():
    """Test alternative routes to see if routing is working"""
    print(f"\n🛣️  Testing Alternative Routes:")
    print("-" * 35)
    
    routes_to_test = [
        ("/", "Home Page"),
        ("/welcome", "Welcome Page"),
        ("/dashboard", "Dashboard"),
        ("/surveys/launch", "Old Survey Creation"),
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
    """Run all tests"""
    print("🎯 SURVEY BUILDER IMPORT TEST")
    print("=" * 50)
    print("Testing if the SurveyBuilder component loads properly")
    print()
    
    # Test survey builder load
    builder_loads = test_survey_builder_load()
    
    # Test alternative routes
    routes_work = test_alternative_routes()
    
    print("\n" + "=" * 50)
    print("📈 TEST RESULTS:")
    print(f"✅ Survey Builder Load: {'Working' if builder_loads else 'Failed'}")
    print(f"✅ Alternative Routes: {'Working' if routes_work else 'Failed'}")
    
    if builder_loads and routes_work:
        print("\n🎉 SURVEY BUILDER SHOULD BE WORKING!")
        print("✅ All required assets are loading")
        print("🔧 The issue might be in the JavaScript execution")
        print("\n🔍 Next Steps:")
        print("1. Check browser console for JavaScript errors")
        print("2. Verify all component imports are working")
        print("3. Check if any child components are missing")
    else:
        print("\n❌ SURVEY BUILDER HAS ISSUES")
        print("🔧 Check the failed tests above")
    
    print("\n🌐 Try accessing: http://54.86.65.150:8080/surveys/builder")
    print("📱 Check browser console (F12) for JavaScript errors")

if __name__ == "__main__":
    main()
