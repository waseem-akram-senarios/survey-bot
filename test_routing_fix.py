#!/usr/bin/env python3
"""
Test different routing approaches to fix the client-side routing issue
"""

import requests
import time

BASE_URL = "http://54.86.65.150:8080"

def test_different_routing_approaches():
    """Test different URL formats and routing approaches"""
    print("🔧 TESTING ROUTING APPROACHES")
    print("=" * 50)
    
    # Test different URL formats
    test_urls = [
        "/surveys/launch",
        "/surveys/launch/",
        "/#/surveys/launch",  # HashRouter style
        "/surveys/builder",
        "/surveys/builder/",
        "/#/surveys/builder",  # HashRouter style
    ]
    
    for url in test_urls:
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=10)
            print(f"✅ {url}: HTTP {response.status_code} - {len(response.text)} bytes")
            
            # Check if content is different from dashboard
            dashboard_response = requests.get(f"{BASE_URL}/dashboard", timeout=10)
            is_different = response.text != dashboard_response.text
            print(f"   📝 Different from dashboard: {is_different}")
            
            # Check for specific content
            has_create_survey = "Create Survey" in response.text
            has_survey_builder = "Survey Builder" in response.text
            print(f"   📋 Create Survey content: {has_create_survey}")
            print(f"   🏗️  Survey Builder content: {has_survey_builder}")
            print()
            
        except Exception as e:
            print(f"❌ {url}: Error - {e}")
    
    # Test if JavaScript bundle is loading correctly
    try:
        js_response = requests.get(f"{BASE_URL}/assets/index--vu4vCRi.js", timeout=10)
        if js_response.status_code == 200:
            has_components = "CreateSurveyModern" in js_response.text and "SurveyBuilderAdvanced" in js_response.text
            print(f"✅ JavaScript Bundle: Components included - {has_components}")
        else:
            print(f"❌ JavaScript Bundle: HTTP {js_response.status_code}")
    except Exception as e:
        print(f"❌ JavaScript Bundle: Error - {e}")

if __name__ == "__main__":
    test_different_routing_approaches()
