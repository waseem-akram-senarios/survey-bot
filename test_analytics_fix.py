#!/usr/bin/env python3
"""
Test Analytics Fix
Verifies that all analytics endpoints are working after dashboard endpoint fix
"""

import requests
import json

BASE_URL = "http://54.86.65.150:8080"

def test_analytics_endpoints():
    """Test all analytics-related endpoints"""
    print("🔍 Testing Analytics Endpoints")
    print("=" * 40)
    
    endpoints = [
        {
            "name": "Analytics Summary",
            "url": f"{BASE_URL}/pg/api/analytics/summary",
            "description": "Main analytics data"
        },
        {
            "name": "Survey Stats",
            "url": f"{BASE_URL}/pg/api/surveys/stat?tenant_id=itcurves",
            "description": "Survey statistics"
        },
        {
            "name": "Dashboard Data (FIXED)",
            "url": f"{BASE_URL}/pg/api/surveys/dashboard?tenant_id=itcurves",
            "description": "Dashboard endpoint that was missing"
        },
        {
            "name": "All Surveys",
            "url": f"{BASE_URL}/pg/api/surveys/list?tenant_id=itcurves",
            "description": "List of all surveys"
        },
        {
            "name": "Completed Surveys",
            "url": f"{BASE_URL}/pg/api/surveys/list_completed?tenant_id=itcurves",
            "description": "Completed surveys only"
        },
        {
            "name": "In-Progress Surveys",
            "url": f"{BASE_URL}/pg/api/surveys/list_inprogress?tenant_id=itcurves",
            "description": "Active surveys"
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint["url"], timeout=10)
            status = "✅ Working" if response.status_code == 200 else f"❌ Error ({response.status_code})"
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if "total_surveys" in data:
                            detail = f"Found {data.get('total_surveys', 0)} surveys"
                        elif "status" in data:
                            detail = f"Status: {data.get('status', 'Unknown')}"
                        elif isinstance(data, list):
                            detail = f"Found {len(data)} items"
                        else:
                            detail = "Response OK"
                    else:
                        detail = "Response OK"
                except:
                    detail = "Response OK (non-JSON)"
            else:
                detail = response.text[:100] if response.text else "No response"
            
            results.append({
                "name": endpoint["name"],
                "status": status,
                "detail": detail,
                "description": endpoint["description"]
            })
            
        except Exception as e:
            results.append({
                "name": endpoint["name"],
                "status": "❌ Failed",
                "detail": str(e),
                "description": endpoint["description"]
            })
    
    # Display results
    print("\n📊 Analytics Endpoint Test Results:")
    print("=" * 50)
    
    for result in results:
        print(f"\n{result['status']} {result['name']}")
        print(f"   📝 {result['description']}")
        print(f"   📄 {result['detail']}")
    
    # Summary
    working = sum(1 for r in results if "✅" in r["status"])
    total = len(results)
    
    print(f"\n" + "=" * 50)
    print(f"📈 SUMMARY: {working}/{total} endpoints working")
    
    if working == total:
        print("🎉 ALL ANALYTICS ENDPOINTS ARE WORKING!")
        print("✅ Analytics page should now load successfully")
    else:
        print("⚠️  Some endpoints are still failing")
        print("🔧 Check the failed endpoints above")
    
    return working == total

def test_analytics_page_access():
    """Test if the analytics page itself is accessible"""
    print("\n🌐 Testing Analytics Page Access")
    print("=" * 35)
    
    try:
        response = requests.get(f"{BASE_URL}/analytics", timeout=10)
        
        if response.status_code == 200:
            print("✅ Analytics page accessible")
            print("   📱 URL: http://54.86.65.150:8080/analytics")
            
            # Check if it's the React app
            if 'React' in response.text or 'index-' in response.text:
                print("✅ React app loading correctly")
                return True
            else:
                print("⚠️  React app may not be loading properly")
                return False
        else:
            print(f"❌ Analytics page error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Analytics page failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ANALYTICS FIX VERIFICATION")
    print("=" * 40)
    print("Testing the fix for 'Failed to load analytics data'")
    print()
    
    # Test endpoints
    endpoints_ok = test_analytics_endpoints()
    
    # Test page access
    page_ok = test_analytics_page_access()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULTS:")
    print(f"✅ API Endpoints: {'Working' if endpoints_ok else 'Failed'}")
    print(f"✅ Page Access: {'Working' if page_ok else 'Failed'}")
    
    if endpoints_ok and page_ok:
        print("\n🎉 ANALYTICS FIX SUCCESSFUL!")
        print("✅ The 'Failed to load analytics data' issue is resolved")
        print("📱 Visit http://54.86.65.150:8080/analytics to see your analytics")
    else:
        print("\n⚠️  ANALYTICS ISSUE PERSISTS")
        print("🔧 Some components may still need fixing")
    
    print("\n🔋 NEXT STEPS:")
    print("1. Visit the analytics page in your browser")
    print("2. Check for any remaining error messages")
    print("3. Verify all charts and data are loading")
    print("4. Test real-time data updates")

if __name__ == "__main__":
    main()
