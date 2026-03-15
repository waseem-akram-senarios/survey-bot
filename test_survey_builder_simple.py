#!/usr/bin/env python3
"""
Simple test to verify the Survey Builder page loads and works.
"""

import requests
import time

BASE_URL = "http://54.86.65.150:8080"

def test_survey_builder():
    """Test if survey builder loads correctly"""
    print("🚀 TESTING SURVEY BUILDER")
    print("=" * 40)
    
    try:
        # Test page loads
        response = requests.get(f"{BASE_URL}/surveys/builder", timeout=10)
        
        if response.status_code == 200:
            print("✅ Survey Builder page loads successfully")
            print(f"   📝 Status: {response.status_code}")
            print(f"   ⏱️  Load time: {response.elapsed.total_seconds():.2f}s")
            
            # Check for React app
            if "root" in response.text:
                print("✅ React app container found")
            else:
                print("❌ React app container not found")
            
            # Check for JavaScript bundle
            if "index-" in response.text and ".js" in response.text:
                print("✅ JavaScript bundle found")
            else:
                print("❌ JavaScript bundle not found")
            
            # Check if it's the same as dashboard (should be different)
            dashboard_response = requests.get(f"{BASE_URL}/dashboard", timeout=10)
            if response.text != dashboard_response.text:
                print("✅ Survey Builder is different from dashboard")
            else:
                print("❌ Survey Builder appears to be same as dashboard")
            
            # Test API integration
            try:
                api_response = requests.get(f"{BASE_URL}/api/surveys", timeout=5)
                if api_response.status_code == 200:
                    print("✅ Survey API is working")
                else:
                    print(f"❌ Survey API returned {api_response.status_code}")
            except:
                print("❌ Survey API test failed")
            
            print("\n🎯 SUMMARY:")
            print("   🌐 Survey Builder: http://54.86.65.150:8080/surveys/builder")
            print("   📊 Dashboard: http://54.86.65.150:8080/dashboard")
            
        else:
            print(f"❌ Survey Builder failed to load: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing Survey Builder: {e}")

if __name__ == "__main__":
    test_survey_builder()
