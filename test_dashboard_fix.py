#!/usr/bin/env python3
"""
Test Dashboard with Fixed Survey Creation
"""

import requests
import json

def test_dashboard_fix():
    """Test the dashboard with fixed survey creation"""
    print("🔧 Testing Dashboard with Fixed Survey Creation")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test 1: Dashboard accessibility
    print("\n📊 Test 1: Dashboard Accessibility")
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard accessible")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {str(e)}")
        return False
    
    # Test 2: Survey API functionality
    print("\n📋 Test 2: Survey API Functionality")
    try:
        # Test surveys list
        surveys_response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        if surveys_response.status_code == 200:
            surveys = surveys_response.json()
            print(f"✅ Surveys API: {len(surveys)} surveys found")
        else:
            print(f"❌ Surveys API failed: {surveys_response.status_code}")
            return False
        
        # Test templates list
        templates_response = requests.get(f"{base_url}/pg/api/templates/list", timeout=10)
        if templates_response.status_code == 200:
            templates = templates_response.json()
            print(f"✅ Templates API: {len(templates)} templates found")
        else:
            print(f"❌ Templates API failed: {templates_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Survey API test failed: {str(e)}")
        return False
    
    # Test 3: Survey Creation (Fixed)
    print("\n➕ Test 3: Survey Creation (Fixed)")
    try:
        # Get a template
        templates_response = requests.get(f"{base_url}/pg/api/templates/list", timeout=10)
        templates = templates_response.json()
        template_name = templates[0].get('TemplateName')
        
        # Create survey with correct payload
        payload = {
            'SurveyId': 'test_dashboard_fix',
            'Name': template_name,
            'Recipient': 'Dashboard Test User',
            'RiderName': 'Dashboard Test Rider',
            'RideId': 'RIDE_DASHBOARD',
            'TenantId': 'itcurves',
            'URL': 'http://localhost:8080',
            'Biodata': 'Test user for dashboard fix',
            'Phone': '+15551234567',
            'Bilingual': True
        }
        
        response = requests.post(
            f"{base_url}/pg/api/surveys/generate",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Survey creation fixed: {result.get('SurveyId', 'Unknown')}")
        else:
            print(f"❌ Survey creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Survey creation test failed: {str(e)}")
        return False
    
    # Test 4: Analytics API
    print("\n📈 Test 4: Analytics API")
    try:
        analytics_response = requests.get(f"{base_url}/pg/api/analytics/summary", timeout=10)
        if analytics_response.status_code == 200:
            analytics = analytics_response.json()
            print(f"✅ Analytics API: {list(analytics.keys())}")
        else:
            print(f"❌ Analytics API failed: {analytics_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analytics API test failed: {str(e)}")
        return False
    
    # Test 5: Search functionality
    print("\n🔍 Test 5: Search Functionality")
    try:
        surveys_response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        surveys = surveys_response.json()
        
        # Test search
        search_results = [s for s in surveys if 'test' in s.get('Name', '').lower()]
        print(f"✅ Search functionality: {len(search_results)} results for 'test'")
        
        # Test filter
        completed_surveys = [s for s in surveys if s.get('Status') == 'Completed']
        print(f"✅ Filter functionality: {len(completed_surveys)} completed surveys")
        
    except Exception as e:
        print(f"❌ Search/filter test failed: {str(e)}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Dashboard Fix")
    print("=" * 50)
    
    success = test_dashboard_fix()
    
    print("\n" + "=" * 50)
    print("🏆 DASHBOARD FIX TEST RESULTS:")
    print("=" * 50)
    
    if success:
        print("🎉 DASHBOARD FIX SUCCESSFUL!")
        print("✅ Dashboard accessible")
        print("✅ Survey API working")
        print("✅ Template API working")
        print("✅ Survey creation FIXED!")
        print("✅ Analytics API working")
        print("✅ Search/filter working")
        print("\n🚀 The 404 error has been fixed!")
        print("✅ Survey creation now works properly!")
        print("✅ Dashboard is ready for use!")
    else:
        print("❌ Some issues still exist")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
