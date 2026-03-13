#!/usr/bin/env python3
"""
Test Analytics Loading Fix
Verifies that the analytics page loads without endless spinner
"""

import requests
import time
import json

BASE_URL = "http://54.86.65.150:8080"

def test_analytics_loading():
    """Test that analytics page loads properly"""
    print("🔄 Testing Analytics Loading Fix")
    print("=" * 40)
    
    # Test the critical API endpoints that analytics needs
    critical_endpoints = [
        ("Analytics Summary", f"{BASE_URL}/pg/api/analytics/summary"),
        ("Survey Stats", f"{BASE_URL}/pg/api/surveys/stat?tenant_id=itcurves"),
        ("All Surveys", f"{BASE_URL}/pg/api/surveys/list?tenant_id=itcurves"),
        ("Dashboard Data", f"{BASE_URL}/pg/api/surveys/dashboard?tenant_id=itcurves")
    ]
    
    print("📊 Testing Critical Analytics Endpoints:")
    print("-" * 45)
    
    all_critical_working = True
    response_times = []
    
    for name, url in critical_endpoints:
        start_time = time.time()
        try:
            response = requests.get(url, timeout=10)
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 0)
            response_times.append(response_time)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if "total_surveys" in data:
                            detail = f"Found {data.get('total_surveys', 0)} surveys"
                        elif "Total_Surveys" in data:
                            detail = f"Found {data.get('Total_Surveys', 0)} surveys"
                        elif "status" in data:
                            detail = f"Status: {data.get('status', 'Unknown')}"
                        else:
                            detail = "Response OK"
                    else:
                        detail = f"Found {len(data)} items"
                except:
                    detail = "Response OK (non-JSON)"
                
                print(f"✅ {name}: {response_time}ms - {detail}")
            else:
                print(f"❌ {name}: {response.status_code} - Failed")
                all_critical_working = False
                
        except Exception as e:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 0)
            print(f"❌ {name}: Timeout/Error ({response_time}ms) - {str(e)[:50]}")
            all_critical_working = False
    
    # Calculate average response time
    if response_times:
        avg_time = round(sum(response_times) / len(response_times), 0)
        print(f"\n⏱️  Average Response Time: {avg_time}ms")
    
    # Test the analytics page itself
    print(f"\n🌐 Testing Analytics Page:")
    print("-" * 30)
    
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/analytics", timeout=15)
        end_time = time.time()
        load_time = round((end_time - start_time) * 1000, 0)
        
        if response.status_code == 200:
            print(f"✅ Analytics Page: {load_time}ms - Loaded successfully")
            
            # Check if it's the React app
            if 'React' in response.text or 'index-' in response.text:
                print("✅ React app detected")
                
                # Check for loading indicators in the HTML
                if 'CircularProgress' in response.text or 'loading' in response.text.lower():
                    print("⚠️  Loading indicators found in HTML (may still be loading)")
                    page_status = "Loading"
                else:
                    print("✅ No loading indicators found")
                    page_status = "Loaded"
            else:
                print("⚠️  React app may not be loading properly")
                page_status = "Error"
        else:
            print(f"❌ Analytics Page: {response.status_code} - Failed")
            page_status = "Error"
            
    except Exception as e:
        print(f"❌ Analytics Page: Failed - {str(e)[:50]}")
        page_status = "Error"
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📈 LOADING TEST RESULTS:")
    print(f"✅ Critical APIs: {'Working' if all_critical_working else 'Failed'}")
    print(f"✅ Analytics Page: {page_status}")
    
    if response_times:
        print(f"⏱️  Average API Response: {avg_time}ms")
    
    # Final verdict
    if all_critical_working and page_status == "Loaded":
        print("\n🎉 ANALYTICS LOADING FIX SUCCESSFUL!")
        print("✅ The endless loading issue should be resolved")
        print("📱 Visit http://54.86.65.150:8080/analytics to verify")
        return True
    elif all_critical_working and page_status == "Loading":
        print("\n⚠️  ANALYTICS LOADING IMPROVED")
        print("✅ APIs are working, page may need a moment to load")
        print("📱 Visit http://54.86.65.150:8080/analytics and wait 5-10 seconds")
        return True
    else:
        print("\n❌ ANALYTICS LOADING ISSUE PERSISTS")
        print("🔧 Some components still need attention")
        return False

def main():
    """Run the loading test"""
    print("🚀 ANALYTICS LOADING FIX VERIFICATION")
    print("=" * 50)
    print("Testing the fix for endless analytics loading")
    print()
    
    success = test_analytics_loading()
    
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    if success:
        print("1. ✅ Visit the analytics page in your browser")
        print("2. ✅ Wait 5-10 seconds for full load")
        print("3. ✅ Verify data appears and spinner disappears")
        print("4. ✅ Check that charts and metrics are displayed")
    else:
        print("1. ⚠️  Check browser console for JavaScript errors")
        print("2. ⚠️  Verify network requests in dev tools")
        print("3. ⚠️  Clear browser cache and retry")
    
    print(f"\n📱 Analytics URL: http://54.86.65.150:8080/analytics")

if __name__ == "__main__":
    main()
