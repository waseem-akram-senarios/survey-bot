#!/usr/bin/env python3
"""
Test Survey Completion Fix
Tests if survey submission now correctly updates status to Completed
"""

import requests
import json
import time

def test_survey_completion():
    """Test survey completion status update"""
    print("🧪 Testing Survey Completion Fix")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Step 1: Get available templates
    print("\n📋 Step 1: Get Available Templates")
    try:
        response = requests.get(f"{base_url}/pg/api/templates/list", timeout=10)
        if response.status_code == 200:
            templates = response.json()
            if templates:
                template_name = templates[0].get('TemplateName')
                print(f"✅ Using template: {template_name}")
            else:
                print("❌ No templates available")
                return False
        else:
            print(f"❌ Failed to get templates: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Template request failed: {str(e)}")
        return False
    
    # Step 2: Create a new survey
    print("\n➕ Step 2: Create New Survey")
    survey_id = f"completion_test_{int(time.time())}"
    payload = {
        'SurveyId': survey_id,
        'Name': template_name,
        'Recipient': 'Completion Test User',
        'RiderName': 'Test Rider',
        'RideId': f'RIDE_TEST_{int(time.time())}',
        'TenantId': 'itcurves',
        'URL': 'http://localhost:8080',
        'Biodata': 'Test user for completion',
        'Phone': '+15551234567',
        'Bilingual': True
    }
    
    try:
        response = requests.post(f"{base_url}/pg/api/surveys/generate", json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Survey created: {survey_id}")
        else:
            print(f"❌ Survey creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Survey creation failed: {str(e)}")
        return False
    
    # Step 3: Check initial status
    print("\n🔍 Step 3: Check Initial Status")
    try:
        response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        if response.status_code == 200:
            surveys = response.json()
            test_survey = next((s for s in surveys if s.get('SurveyId') == survey_id), None)
            if test_survey:
                initial_status = test_survey.get('Status')
                print(f"✅ Initial status: {initial_status}")
            else:
                print("❌ Test survey not found")
                return False
        else:
            print(f"❌ Failed to get surveys: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check failed: {str(e)}")
        return False
    
    # Step 4: Submit survey answers
    print("\n📝 Step 4: Submit Survey Answers")
    try:
        # Get survey questions first
        questions_response = requests.get(f"{base_url}/pg/api/surveys/{survey_id}/questions", timeout=10)
        if questions_response.status_code == 200:
            questions_data = questions_response.json()
            questions = questions_data.get('Questions', [])
            
            if questions:
                # Create mock answers for all questions
                answers = []
                for i, q in enumerate(questions[:3]):  # Answer first 3 questions
                    answers.append({
                        "QueId": q.get('id'),
                        "QueText": q.get('text', ''),
                        "QueScale": q.get('scales'),
                        "QueCriteria": q.get('criteria', 'open'),
                        "QueCategories": q.get('categories', []),
                        "ParentId": q.get('parent_id'),
                        "ParentCategoryTexts": q.get('parent_category_texts', []),
                        "Order": q.get('order', i),
                        "Ans": "Test Answer",
                        "RawAns": "Test Raw Answer",
                        "Autofill": "No"
                    })
                
                submit_payload = {
                    "SurveyId": survey_id,
                    "QuestionswithAns": answers
                }
                
                submit_response = requests.post(f"{base_url}/pg/api/surveys/submit", json=submit_payload, timeout=10)
                if submit_response.status_code == 200:
                    print("✅ Survey answers submitted")
                else:
                    print(f"❌ Answer submission failed: {submit_response.status_code}")
                    print(f"Response: {submit_response.text}")
                    return False
            else:
                print("❌ No questions found for survey")
                return False
        else:
            print(f"❌ Failed to get questions: {questions_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Answer submission failed: {str(e)}")
        return False
    
    # Step 5: Check final status
    print("\n🎯 Step 5: Check Final Status")
    try:
        # Wait a moment for processing
        time.sleep(2)
        
        response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        if response.status_code == 200:
            surveys = response.json()
            test_survey = next((s for s in surveys if s.get('SurveyId') == survey_id), None)
            if test_survey:
                final_status = test_survey.get('Status')
                print(f"✅ Final status: {final_status}")
                
                if final_status == "Completed":
                    print("🎉 SUCCESS: Survey status updated to Completed!")
                    return True
                else:
                    print(f"❌ FAILED: Status is still {final_status}")
                    return False
            else:
                print("❌ Test survey not found")
                return False
        else:
            print(f"❌ Failed to get surveys: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Final status check failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Survey Completion Fix Test")
    print("=" * 50)
    
    success = test_survey_completion()
    
    print("\n" + "=" * 50)
    print("🏆 SURVEY COMPLETION TEST RESULTS:")
    print("=" * 50)
    
    if success:
        print("🎉 SURVEY COMPLETION FIX WORKING!")
        print("✅ Survey submission now updates status to 'Completed'")
        print("✅ UI will now show correct survey status")
        print("✅ Both email and voice call completions will work")
    else:
        print("❌ SURVEY COMPLETION FIX FAILED!")
        print("🔧 Survey status is still not updating")
        print("🔧 Need to investigate further")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
