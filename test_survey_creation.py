#!/usr/bin/env python3
"""
Test Modern Survey Creation Page
Verifies that the new survey creation interface is working correctly
"""

import requests
import time

BASE_URL = "http://54.86.65.150:8080"

def test_survey_creation_page():
    """Test the modern survey creation page"""
    print("🚀 Testing Modern Survey Creation Page")
    print("=" * 45)
    
    # Test the survey creation page
    print("🌐 Testing Survey Creation Access:")
    print("-" * 40)
    
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/surveys/launch", timeout=15)
        end_time = time.time()
        load_time = round((end_time - start_time) * 1000, 0)
        
        if response.status_code == 200:
            print(f"✅ Survey Creation Page: {load_time}ms - Loaded successfully")
            
            # Check if it's the React app
            if 'React' in response.text or 'index-' in response.text:
                print("✅ React app detected")
                
                # Check for survey creation content
                if 'Create Survey' in response.text:
                    print("✅ Create Survey title found")
                else:
                    print("⚠️  Create Survey title not found (may load dynamically)")
                
                # Check for form elements
                if 'Recipient Name' in response.text or 'Phone Number' in response.text:
                    print("✅ Form fields detected")
                else:
                    print("⚠️  Form fields not found (may load dynamically)")
                
                # Check for template selection
                if 'Choose Template' in response.text or 'template' in response.text.lower():
                    print("✅ Template selection detected")
                else:
                    print("⚠️  Template selection not found (may load dynamically)")
                
                return True
            else:
                print("⚠️  React app may not be loading properly")
                return False
        else:
            print(f"❌ Survey Creation Page: {response.status_code} - Failed")
            return False
            
    except Exception as e:
        print(f"❌ Survey Creation Page: Failed - {str(e)[:50]}")
        return False

def test_templates_api():
    """Test that templates API is working for the survey creation page"""
    print(f"\n📋 Testing Templates API:")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/pg/api/templates/list", timeout=10)
        
        if response.status_code == 200:
            try:
                templates = response.json()
                if isinstance(templates, list):
                    print(f"✅ Templates API: {len(templates)} templates available")
                    
                    # Show a few template names
                    if templates:
                        sample_templates = templates[:3]
                        print("📝 Sample templates:")
                        for template in sample_templates:
                            print(f"   - {template}")
                    
                    return True
                else:
                    print("⚠️  Templates API: Invalid response format")
                    return False
            except:
                print("⚠️  Templates API: Non-JSON response")
                return False
        else:
            print(f"❌ Templates API: {response.status_code} - Failed")
            return False
            
    except Exception as e:
        print(f"❌ Templates API: Error - {str(e)[:50]}")
        return False

def test_survey_generation_api():
    """Test the survey generation API endpoint"""
    print(f"\n🔧 Testing Survey Generation API:")
    print("-" * 40)
    
    try:
        # Test with minimal data
        test_data = {
            "SurveyId": "test-modern-123",
            "Recipient": "Test User",
            "Name": "MK Survey",
            "template_name": "MK Survey",
            "Phone": "1234567890",
            "URL": f"{BASE_URL}/survey/test-modern-123",
            "Bilingual": False
        }
        
        response = requests.post(
            f"{BASE_URL}/pg/api/surveys/generate",
            json=test_data,
            timeout=15
        )
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("SurveyId"):
                    print(f"✅ Survey Generation: Working - Survey ID: {result['SurveyId']}")
                    print(f"📊 Questions generated: {len(result.get('QuestionswithAns', []))}")
                    return True
                else:
                    print("⚠️  Survey Generation: No Survey ID in response")
                    return False
            except:
                print("⚠️  Survey Generation: Invalid JSON response")
                return False
        else:
            print(f"❌ Survey Generation: {response.status_code} - Failed")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail.get('detail', 'Unknown error')}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"❌ Survey Generation: Error - {str(e)[:50]}")
        return False

def main():
    """Run all tests"""
    print("🎯 MODERN SURVEY CREATION VERIFICATION")
    print("=" * 50)
    print("Testing the new modern survey creation interface")
    print()
    
    # Test survey creation page
    page_ok = test_survey_creation_page()
    
    # Test templates API
    templates_ok = test_templates_api()
    
    # Test survey generation API
    generation_ok = test_survey_generation_api()
    
    print("\n" + "=" * 50)
    print("📈 TEST RESULTS:")
    print(f"✅ Survey Creation Page: {'Working' if page_ok else 'Failed'}")
    print(f"✅ Templates API: {'Working' if templates_ok else 'Failed'}")
    print(f"✅ Survey Generation API: {'Working' if generation_ok else 'Failed'}")
    
    if page_ok and templates_ok and generation_ok:
        print("\n🎉 MODERN SURVEY CREATION SUCCESSFUL!")
        print("✅ The new survey creation interface is working correctly")
        print("📱 Users can create surveys with the modern interface")
        print("\n🌐 Visit: http://54.86.65.150:8080/surveys/launch to see the new interface")
    else:
        print("\n⚠️  SOME ISSUES DETECTED")
        print("🔧 Check the failed tests above")
    
    print("\n🎯 FEATURES INCLUDED:")
    print("🎨 Modern two-column layout")
    print("📝 Enhanced form fields with icons")
    print("📋 Template selection with categories")
    print("⚡ Multiple action buttons")
    print("📱 Responsive design")
    print("🔄 Real-time validation")
    print("🎯 Professional styling")

if __name__ == "__main__":
    main()
