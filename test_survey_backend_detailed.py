#!/usr/bin/env python3
"""
Detailed test of survey backend functionality
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://54.86.65.150:8080"

def test_survey_backend_comprehensive():
    """Test all survey backend functionality comprehensively"""
    print("🔍 DETAILED SURVEY BACKEND TEST")
    print("=" * 60)
    
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'details': []
    }
    
    def run_test(test_name, test_func):
        """Run a single test and record results"""
        results['total_tests'] += 1
        try:
            test_result = test_func()
            if test_result['success']:
                results['passed_tests'] += 1
                status = "✅ PASS"
                print(f"{status} {test_name}")
                print(f"   📝 {test_result['message']}")
                if 'data' in test_result:
                    print(f"   📊 Data: {test_result['data']}")
            else:
                results['failed_tests'] += 1
                status = "❌ FAIL"
                print(f"{status} {test_name}")
                print(f"   📝 {test_result['message']}")
            
            results['details'].append({
                'name': test_name,
                'success': test_result['success'],
                'message': test_result['message'],
                'data': test_result.get('data', {})
            })
            print()
            return test_result['success']
        except Exception as e:
            results['failed_tests'] += 1
            print(f"❌ ERROR {test_name}: {str(e)}")
            results['details'].append({
                'name': test_name,
                'success': False,
                'message': f"Exception: {str(e)}",
                'data': {}
            })
            return False
    
    # Test 1: Survey Generation API
    def test_survey_generation():
        try:
            survey_data = {
                "SurveyId": f"test_survey_{int(time.time())}",
                "template_name": "MK Survey",
                "Recipient": "Test User",
                "RiderName": "Test Rider",
                "RideId": "test_ride_123",
                "TenantId": "demo_tenant",
                "Phone": "+1234567890",
                "URL": f"{BASE_URL}/survey/test_{int(time.time())}",
                "Bilingual": False,
                "Name": "Test Survey"
            }
            
            response = requests.post(f"{BASE_URL}/api/surveys/generate", 
                                   json=survey_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                question_count = len(result.get('QuestionswithAns', []))
                return {
                    'success': True,
                    'message': f"Generated {question_count} questions successfully",
                    'data': {
                        'survey_id': survey_data['SurveyId'],
                        'question_count': question_count,
                        'response_size': len(str(result))
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"HTTP {response.status_code}: {response.text[:100]}"
                }
        except Exception as e:
            return {'success': False, 'message': f"Exception: {str(e)}"}
    
    # Test 2: Survey Listing API
    def test_survey_listing():
        try:
            response = requests.get(f"{BASE_URL}/api/surveys/list", timeout=10)
            
            if response.status_code == 200:
                surveys = response.json()
                survey_count = len(surveys) if isinstance(surveys, list) else 0
                return {
                    'success': True,
                    'message': f"Found {survey_count} surveys",
                    'data': {
                        'survey_count': survey_count,
                        'response_size': len(str(surveys))
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"HTTP {response.status_code}: {response.text[:100]}"
                }
        except Exception as e:
            return {'success': False, 'message': f"Exception: {str(e)}"}
    
    # Test 3: Template Listing API
    def test_template_listing():
        try:
            response = requests.get(f"{BASE_URL}/api/templates/list", timeout=10)
            
            if response.status_code == 200:
                templates = response.json()
                template_count = len(templates) if isinstance(templates, list) else 0
                return {
                    'success': True,
                    'message': f"Found {template_count} templates",
                    'data': {
                        'template_count': template_count,
                        'response_size': len(str(templates))
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"HTTP {response.status_code}: {response.text[:100]}"
                }
        except Exception as e:
            return {'success': False, 'message': f"Exception: {str(e)}"}
    
    # Test 4: Template Creation API
    def test_template_creation():
        try:
            template_data = {
                "TemplateName": f"Test Template {int(time.time())}",
                "Questions": [
                    {
                        "QuestionText": "How satisfied are you?",
                        "QuestionType": "rating",
                        "Options": ["1", "2", "3", "4", "5"]
                    }
                ]
            }
            
            response = requests.post(f"{BASE_URL}/api/templates/create", 
                                   json=template_data, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'message': "Template created successfully",
                    'data': {
                        'template_name': template_data['TemplateName'],
                        'response_status': response.status_code
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"HTTP {response.status_code}: {response.text[:100]}"
                }
        except Exception as e:
            return {'success': False, 'message': f"Exception: {str(e)}"}
    
    # Test 5: Survey Statistics API
    def test_survey_statistics():
        try:
            response = requests.get(f"{BASE_URL}/api/surveys/stat", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                return {
                    'success': True,
                    'message': "Survey statistics retrieved",
                    'data': {
                        'response_size': len(str(stats)),
                        'keys': list(stats.keys()) if isinstance(stats, dict) else []
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"HTTP {response.status_code}: {response.text[:100]}"
                }
        except Exception as e:
            return {'success': False, 'message': f"Exception: {str(e)}"}
    
    # Test 6: Template Statistics API
    def test_template_statistics():
        try:
            response = requests.get(f"{BASE_URL}/api/templates/stat", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                return {
                    'success': True,
                    'message': "Template statistics retrieved",
                    'data': {
                        'response_size': len(str(stats)),
                        'keys': list(stats.keys()) if isinstance(stats, dict) else []
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"HTTP {response.status_code}: {response.text[:100]}"
                }
        except Exception as e:
            return {'success': False, 'message': f"Exception: {str(e)}"}
    
    # Test 7: Database Connectivity (via survey data)
    def test_database_connectivity():
        try:
            response = requests.get(f"{BASE_URL}/api/surveys/list", timeout=10)
            
            if response.status_code == 200:
                surveys = response.json()
                # Check if we have actual data structure
                if isinstance(surveys, list) and len(surveys) > 0:
                    first_survey = surveys[0]
                    has_structure = isinstance(first_survey, dict)
                    return {
                        'success': True,
                        'message': "Database connected and returning structured data",
                        'data': {
                            'has_data': True,
                            'has_structure': has_structure,
                            'sample_keys': list(first_survey.keys()) if has_structure else []
                        }
                    }
                else:
                    return {
                        'success': True,
                        'message': "Database connected but no survey data",
                        'data': {'has_data': False}
                    }
            else:
                return {
                    'success': False,
                    'message': f"Database connectivity issue: HTTP {response.status_code}"
                }
        except Exception as e:
            return {'success': False, 'message': f"Database error: {str(e)}"}
    
    # Test 8: Bilingual Support
    def test_bilingual_support():
        try:
            survey_data = {
                "SurveyId": f"test_bilingual_{int(time.time())}",
                "template_name": "MK Survey",
                "Recipient": "Test User",
                "RiderName": "Test Rider",
                "RideId": "test_ride_123",
                "TenantId": "demo_tenant",
                "Phone": "+1234567890",
                "URL": f"{BASE_URL}/survey/test_bilingual_{int(time.time())}",
                "Bilingual": True,  # Enable bilingual
                "Name": "Test Bilingual Survey"
            }
            
            response = requests.post(f"{BASE_URL}/api/surveys/generate", 
                                   json=survey_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                question_count = len(result.get('QuestionswithAns', []))
                return {
                    'success': True,
                    'message': f"Bilingual survey generated with {question_count} questions",
                    'data': {
                        'bilingual_enabled': True,
                        'question_count': question_count
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"Bilingual test failed: HTTP {response.status_code}"
                }
        except Exception as e:
            return {'success': False, 'message': f"Bilingual error: {str(e)}"}
    
    # Test 9: Error Handling
    def test_error_handling():
        try:
            # Test with invalid data
            invalid_data = {
                "SurveyId": "",  # Empty survey ID
                "template_name": "Non-existent Template",
                "Recipient": "",  # Empty recipient
                "TenantId": "demo_tenant"
            }
            
            response = requests.post(f"{BASE_URL}/api/surveys/generate", 
                                   json=invalid_data, timeout=10)
            
            # Should return error (400, 422, etc.)
            if response.status_code >= 400:
                return {
                    'success': True,
                    'message': f"Error handling working: HTTP {response.status_code}",
                    'data': {
                        'error_status': response.status_code,
                        'has_error_response': len(response.text) > 0
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"Error handling failed: Expected error but got HTTP {response.status_code}"
                }
        except Exception as e:
            return {'success': False, 'message': f"Error handling test error: {str(e)}"}
    
    # Test 10: Performance Test
    def test_performance():
        try:
            start_time = time.time()
            
            # Test multiple API calls
            apis_to_test = [
                f"{BASE_URL}/api/surveys/list",
                f"{BASE_URL}/api/templates/list",
                f"{BASE_URL}/api/surveys/stat",
                f"{BASE_URL}/api/templates/stat"
            ]
            
            successful_calls = 0
            for api_url in apis_to_test:
                try:
                    response = requests.get(api_url, timeout=5)
                    if response.status_code == 200:
                        successful_calls += 1
                except:
                    pass
            
            end_time = time.time()
            total_time = end_time - start_time
            
            if successful_calls >= 3 and total_time < 5:
                return {
                    'success': True,
                    'message': f"Performance good: {successful_calls}/4 APIs in {total_time:.2f}s",
                    'data': {
                        'successful_calls': successful_calls,
                        'total_time': total_time,
                        'avg_time_per_call': total_time / len(apis_to_test)
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"Performance issue: {successful_calls}/4 APIs in {total_time:.2f}s"
                }
        except Exception as e:
            return {'success': False, 'message': f"Performance test error: {str(e)}"}
    
    # Run all tests
    tests = [
        ("Survey Generation API", test_survey_generation),
        ("Survey Listing API", test_survey_listing),
        ("Template Listing API", test_template_listing),
        ("Template Creation API", test_template_creation),
        ("Survey Statistics API", test_survey_statistics),
        ("Template Statistics API", test_template_statistics),
        ("Database Connectivity", test_database_connectivity),
        ("Bilingual Support", test_bilingual_support),
        ("Error Handling", test_error_handling),
        ("Performance Test", test_performance)
    ]
    
    print("🧪 Running comprehensive survey backend tests...\n")
    
    for test_name, test_func in tests:
        run_test(test_name, test_func)
    
    # Final results
    success_rate = (results['passed_tests'] / results['total_tests']) * 100
    
    print("📊 FINAL RESULTS")
    print("=" * 60)
    print(f"📈 Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed_tests']}")
    print(f"❌ Failed: {results['failed_tests']}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    print()
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Survey backend is working perfectly!")
    elif success_rate >= 75:
        print("✅ GOOD! Survey backend is mostly working with minor issues.")
    else:
        print("⚠️  NEEDS ATTENTION! Survey backend has significant issues.")
    
    print("\n🔍 Detailed Results:")
    for detail in results['details']:
        status = "✅" if detail['success'] else "❌"
        print(f"{status} {detail['name']}: {detail['message']}")
    
    return results

if __name__ == "__main__":
    test_survey_backend_comprehensive()
