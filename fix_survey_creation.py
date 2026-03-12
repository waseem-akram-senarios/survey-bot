#!/usr/bin/env python3
"""
Fix Survey Creation Issue
Debug and fix the survey creation problem
"""

import requests
import json

def test_survey_creation_fix():
    """Test and fix survey creation"""
    print("🔧 Testing Survey Creation Fix")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Get available templates first
    print("\n📋 Step 1: Get Available Templates")
    try:
        templates_response = requests.get(f"{base_url}/pg/api/templates/list", timeout=10)
        if templates_response.status_code == 200:
            templates = templates_response.json()
            print(f"✅ Found {len(templates)} templates")
            
            # Use the first available template
            if templates:
                template_name = templates[0].get('TemplateName')
                print(f"   Using template: {template_name}")
                
                # Test 1: Simple payload
                print(f"\n📝 Step 2: Test Simple Payload")
                simple_payload = {
                    "SurveyId": "test_survey_fix_1",
                    "Name": template_name,
                    "Recipient": "Test User",
                    "RiderName": "Test Rider",
                    "RideId": "RIDE_123",
                    "TenantId": "itcurves",
                    "URL": "http://localhost:8080",
                    "Biodata": "Test user for fixing",
                    "Phone": "+15551234567",
                    "Bilingual": True
                }
                
                try:
                    response = requests.post(
                        f"{base_url}/pg/api/surveys/generate",
                        json=simple_payload,
                        timeout=10
                    )
                    
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ Survey created: {result.get('SurveyId', 'Unknown')}")
                        return True
                    else:
                        print(f"   ❌ Error: {response.text}")
                        
                except Exception as e:
                    print(f"   ❌ Exception: {str(e)}")
                
                # Test 2: Minimal payload
                print(f"\n📝 Step 3: Test Minimal Payload")
                minimal_payload = {
                    "SurveyId": "test_survey_fix_2",
                    "Name": template_name,
                    "Recipient": "Test User",
                    "URL": "http://localhost:8080"
                }
                
                try:
                    response = requests.post(
                        f"{base_url}/pg/api/surveys/generate",
                        json=minimal_payload,
                        timeout=10
                    )
                    
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ Survey created: {result.get('SurveyId', 'Unknown')}")
                        return True
                    else:
                        print(f"   ❌ Error: {response.text}")
                        
                except Exception as e:
                    print(f"   ❌ Exception: {str(e)}")
                
                # Test 3: Check what fields are actually required
                print(f"\n📝 Step 4: Test Different Combinations")
                
                # Test without optional fields
                test_payloads = [
                    {
                        "SurveyId": "test_survey_fix_3",
                        "Name": template_name,
                        "Recipient": "Test User"
                    },
                    {
                        "SurveyId": "test_survey_fix_4",
                        "Name": template_name,
                        "Recipient": "Test User",
                        "URL": "http://localhost:8080"
                    },
                    {
                        "SurveyId": "test_survey_fix_5",
                        "Name": template_name,
                        "Recipient": "Test User",
                        "RiderName": "Test Rider"
                    }
                ]
                
                for i, payload in enumerate(test_payloads):
                    try:
                        response = requests.post(
                            f"{base_url}/pg/api/surveys/generate",
                            json=payload,
                            timeout=10
                        )
                        
                        print(f"   Test {i+1}: Status {response.status_code}")
                        if response.status_code == 200:
                            result = response.json()
                            print(f"   ✅ Success! Survey created: {result.get('SurveyId', 'Unknown')}")
                            print(f"   Working payload: {payload}")
                            return True
                        else:
                            print(f"   ❌ Error: {response.text}")
                            
                    except Exception as e:
                        print(f"   ❌ Exception: {str(e)}")
                
        else:
            print("❌ No templates found")
            return False
            
    except Exception as e:
        print(f"❌ Failed to get templates: {str(e)}")
        return False
    
    return False

def check_survey_service_status():
    """Check if survey service is running"""
    print("\n🔍 Checking Survey Service Status")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test basic endpoints
    endpoints = [
        ("/pg/api/health", "Health Check"),
        ("/pg/api/surveys/list", "Surveys List"),
        ("/pg/api/surveys/stats", "Surveys Stats")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Failed - {str(e)}")

def main():
    """Main function"""
    print("🚀 Survey Creation Fix Tool")
    print("=" * 50)
    
    # Check service status
    check_survey_service_status()
    
    # Try to fix survey creation
    success = test_survey_creation_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SURVEY CREATION ISSUE FIXED!")
        print("✅ Survey creation is now working!")
    else:
        print("❌ SURVEY CREATION STILL HAS ISSUES")
        print("🔧 Check the survey service logs for more details")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
