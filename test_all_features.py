#!/usr/bin/env python3
"""
Comprehensive Feature Test
Test all major features of the Survey Bot application
"""

import requests
import time
import json

BASE_URL = "http://54.86.65.150:8080"

def test_page_access():
    """Test all main pages are accessible"""
    print("🌐 TESTING PAGE ACCESS")
    print("=" * 40)
    
    pages = [
        ("/", "Home/Root"),
        ("/dashboard", "Dashboard"),
        ("/analytics", "Analytics"),
        ("/welcome", "Welcome Page"),
        ("/surveys/launch", "Survey Creation"),
        ("/surveys/builder", "Survey Builder"),
        ("/surveys/manage", "Manage Surveys"),
        ("/templates/manage", "Template Management"),
        ("/contacts", "Contacts"),
    ]
    
    results = {}
    
    for path, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
            status = "✅ Working" if response.status_code == 200 else f"❌ {response.status_code}"
            results[name] = {"status": response.status_code, "working": response.status_code == 200}
            print(f"{status} {name}: {path}")
        except Exception as e:
            results[name] = {"status": "Error", "working": False}
            print(f"❌ Error {name}: {path} - {str(e)[:50]}")
    
    return results

def test_api_endpoints():
    """Test backend API endpoints"""
    print(f"\n🔌 TESTING API ENDPOINTS")
    print("=" * 40)
    
    api_endpoints = [
        ("/api/surveys/stats", "Survey Stats"),
        ("/api/surveys/dashboard", "Dashboard Data"),
        ("/api/surveys", "List Surveys"),
        ("/api/templates", "List Templates"),
    ]
    
    results = {}
    
    for endpoint, name in api_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Working ({response.status_code})")
                results[name] = {"status": response.status_code, "working": True}
            elif response.status_code == 404:
                print(f"⚠️  {name}: Not found (404) - might need implementation")
                results[name] = {"status": response.status_code, "working": False}
            else:
                print(f"❌ {name}: Error {response.status_code}")
                results[name] = {"status": response.status_code, "working": False}
        except Exception as e:
            print(f"❌ {name}: Connection error")
            results[name] = {"status": "Error", "working": False}
    
    return results

def test_survey_builder_content():
    """Test Survey Builder has expected content"""
    print(f"\n📋 TESTING SURVEY BUILDER CONTENT")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/surveys/builder", timeout=10)
        content = response.text
        
        checks = [
            ("ITCurves", "Branding"),
            ("Rider Voice", "User context"),
            ("Question Types", "Sidebar"),
            ("Create Survey", "Canvas"),
            ("Preview Survey", "Right panel"),
            ("Questions", "Tab system"),
            ("Settings", "Tab system"),
            ("Distribution", "Tab system"),
        ]
        
        results = {}
        for check_text, description in checks:
            found = check_text in content
            status = "✅" if found else "❌"
            print(f"{status} {description}: {'Found' if found else 'Not found'}")
            results[description] = found
        
        return results
        
    except Exception as e:
        print(f"❌ Error checking Survey Builder: {e}")
        return {}

def test_authentication():
    """Test authentication flows"""
    print(f"\n🔐 TESTING AUTHENTICATION")
    print("=" * 40)
    
    # Test login page
    try:
        response = requests.get(f"{BASE_URL}/login", timeout=10)
        login_working = response.status_code == 200
        print(f"{'✅' if login_working else '❌'} Login page: {'Working' if login_working else 'Not working'}")
    except Exception as e:
        print(f"❌ Login page: Error - {e}")
        login_working = False
    
    # Test protected route redirect
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=10, allow_redirects=False)
        # If it redirects to login, auth is working
        auth_redirect = response.status_code in [302, 307]
        print(f"{'✅' if auth_redirect else '❌'} Auth redirect: {'Working' if auth_redirect else 'Not redirecting'}")
    except Exception as e:
        print(f"❌ Auth redirect: Error - {e}")
        auth_redirect = False
    
    return {"login_page": login_working, "auth_redirect": auth_redirect}

def test_static_assets():
    """Test static assets are loading"""
    print(f"\n🎨 TESTING STATIC ASSETS")
    print("=" * 40)
    
    assets = [
        ("/assets/index-", "JavaScript bundle"),
        ("/assets/index-", "CSS bundle"),
    ]
    
    results = {}
    
    # Get the main page to find asset URLs
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=10)
        content = response.text
        
        for asset_pattern, name in assets:
            if asset_pattern in content:
                # Extract the actual asset URL
                start = content.find(asset_pattern)
                if start != -1:
                    end = content.find('"', start)
                    if end != -1:
                        asset_url = content[start:end]
                        try:
                            asset_response = requests.get(f"{BASE_URL}{asset_url}", timeout=10)
                            working = asset_response.status_code == 200
                            print(f"{'✅' if working else '❌'} {name}: {'Loading' if working else 'Not loading'}")
                            results[name] = working
                        except Exception as e:
                            print(f"❌ {name}: Error - {e}")
                            results[name] = False
            else:
                print(f"❌ {name}: Not found in HTML")
                results[name] = False
                
    except Exception as e:
        print(f"❌ Error checking assets: {e}")
    
    return results

def generate_summary(page_results, api_results, builder_content, auth_results, asset_results):
    """Generate summary report"""
    print(f"\n📊 FEATURE SUMMARY REPORT")
    print("=" * 50)
    
    # Page Access Summary
    total_pages = len(page_results)
    working_pages = sum(1 for r in page_results.values() if r["working"])
    print(f"📄 Page Access: {working_pages}/{total_pages} working")
    
    # API Summary
    total_apis = len(api_results)
    working_apis = sum(1 for r in api_results.values() if r["working"])
    print(f"🔌 API Endpoints: {working_apis}/{total_apis} working")
    
    # Survey Builder Summary
    total_builder = len(builder_content)
    working_builder = sum(1 for r in builder_content.values() if r)
    print(f"📋 Survey Builder: {working_builder}/{total_builder} features found")
    
    # Authentication Summary
    auth_working = sum(auth_results.values())
    total_auth = len(auth_results)
    print(f"🔐 Authentication: {auth_working}/{total_auth} working")
    
    # Assets Summary
    total_assets = len(asset_results)
    working_assets = sum(1 for r in asset_results.values() if r)
    print(f"🎨 Static Assets: {working_assets}/{total_assets} loading")
    
    # Overall Status
    total_features = total_pages + total_apis + total_builder + total_auth + total_assets
    total_working = working_pages + working_apis + working_builder + auth_working + working_assets
    percentage = (total_working / total_features * 100) if total_features > 0 else 0
    
    print(f"\n🎯 OVERALL STATUS: {total_working}/{total_features} features working ({percentage:.1f}%)")
    
    if percentage >= 80:
        print("🎉 EXCELLENT! Most features are working!")
    elif percentage >= 60:
        print("✅ GOOD! Most core features are working.")
    elif percentage >= 40:
        print("⚠️  OKAY! Some features need attention.")
    else:
        print("❌ NEEDS WORK! Many features have issues.")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if working_pages < total_pages:
        print("🔧 Fix page routing issues")
    if working_apis < total_apis:
        print("🔧 Implement missing API endpoints")
    if working_builder < total_builder:
        print("🔧 Complete Survey Builder implementation")
    if auth_working < total_auth:
        print("🔧 Fix authentication flows")
    if working_assets < total_assets:
        print("🔧 Check static asset loading")

def main():
    """Run all feature tests"""
    print("🚀 COMPREHENSIVE FEATURE TEST")
    print("=" * 50)
    print("Testing all major features of the Survey Bot application")
    print()
    
    # Run all tests
    page_results = test_page_access()
    api_results = test_api_endpoints()
    builder_content = test_survey_builder_content()
    auth_results = test_authentication()
    asset_results = test_static_assets()
    
    # Generate summary
    generate_summary(page_results, api_results, builder_content, auth_results, asset_results)
    
    print(f"\n🌐 Access your application at: {BASE_URL}")
    print("📋 Survey Builder: {BASE_URL}/surveys/builder")
    print("📊 Dashboard: {BASE_URL}/dashboard")
    print("📈 Analytics: {BASE_URL}/analytics")

if __name__ == "__main__":
    main()
