#!/usr/bin/env python3
"""
Test the actual content of the Survey Builder page
"""

import requests
import time

BASE_URL = "http://54.86.65.150:8080"

def test_survey_builder_content():
    """Test the actual content being served"""
    print("🔍 TESTING SURVEY BUILDER CONTENT")
    print("=" * 50)
    
    try:
        # Get survey builder page
        response = requests.get(f"{BASE_URL}/surveys/builder", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ Page loaded successfully - {len(content)} bytes")
            
            # Check for debug component content
            if "Survey Builder Debug Page" in content:
                print("✅ Debug component content found!")
                print("   🎉 Routing is working correctly!")
            else:
                print("❌ Debug component content NOT found")
                print("   🔍 Looking for specific content...")
                
                # Check for dashboard content
                if "Dashboard" in content:
                    print("   ❌ Dashboard content found instead")
                
                # Check for any React content
                if "root" in content:
                    print("   ✅ React root element found")
                
                # Check for JavaScript bundle
                if "index-" in content and ".js" in content:
                    print("   ✅ JavaScript bundle found")
                
                # Print first 500 characters to debug
                print("\n📄 First 500 characters of page content:")
                print("-" * 40)
                print(content[:500])
                print("-" * 40)
            
            # Test different URLs to compare
            print("\n🔄 COMPARING WITH OTHER PAGES:")
            
            # Test dashboard
            dashboard_response = requests.get(f"{BASE_URL}/dashboard", timeout=10)
            if dashboard_response.status_code == 200:
                dashboard_content = dashboard_response.text
                if content == dashboard_content:
                    print("❌ Survey Builder is IDENTICAL to Dashboard")
                    print("   🔧 This confirms a routing issue")
                else:
                    print("✅ Survey Builder is DIFFERENT from Dashboard")
                    print(f"   📊 Dashboard: {len(dashboard_content)} bytes")
                    print(f"   📋 Survey Builder: {len(content)} bytes")
            
            # Test a working page
            analytics_response = requests.get(f"{BASE_URL}/analytics", timeout=10)
            if analytics_response.status_code == 200:
                analytics_content = analytics_response.text
                if content == analytics_content:
                    print("❌ Survey Builder is IDENTICAL to Analytics")
                else:
                    print("✅ Survey Builder is DIFFERENT from Analytics")
            
        else:
            print(f"❌ Failed to load page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_survey_builder_content()
