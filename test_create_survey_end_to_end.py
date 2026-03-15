#!/usr/bin/env python3
"""
Comprehensive end-to-end test for Create Survey functionality.
Tests both frontend accessibility and backend API integration.
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://54.86.65.150:8080"

class CreateSurveyTester:
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
    
    def log_test(self, test_name, passed, details, response_time=0):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"    📝 {details}")
        if response_time > 0:
            print(f"    ⏱️  {response_time:.2f}s")
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "details": details,
            "response_time": response_time
        })
    
    def test_frontend_accessibility(self):
        """Test if Create Survey frontend page loads correctly"""
        print("🌐 TESTING CREATE SURVEY FRONTEND")
        print("=" * 50)
        
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/surveys/launch", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text
                has_create_survey = "Create Survey" in content or "create" in content.lower()
                has_template_selection = "template" in content.lower()
                has_form_elements = "input" in content.lower() or "textfield" in content.lower()
                has_submit_button = "button" in content.lower() and ("create" in content.lower() or "launch" in content.lower())
                
                passed = has_create_survey and has_form_elements
                details = f"Page loads - Create Survey: {has_create_survey}, Forms: {has_form_elements}"
                
                self.log_test("Create Survey Page Access", passed, details, response_time)
                
                # Test for template selection functionality
                self.log_test("Template Selection Available", has_template_selection, 
                            f"Template selection detected: {has_template_selection}")
                
                # Test for form functionality
                self.log_test("Form Elements Present", has_form_elements, 
                            f"Form elements detected: {has_form_elements}")
                
                # Test for submit functionality
                self.log_test("Submit Button Available", has_submit_button, 
                            f"Submit button detected: {has_submit_button}")
                
            else:
                self.log_test("Create Survey Page Access", False, f"HTTP {response.status_code}", response_time)
                
        except Exception as e:
            self.log_test("Create Survey Page Access", False, f"Error: {str(e)[:50]}")
    
    def test_template_availability(self):
        """Test if templates are available for survey creation"""
        print("\n📋 TESTING TEMPLATE AVAILABILITY")
        print("=" * 50)
        
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/pg/api/templates/list", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                templates = response.json()
                has_templates = len(templates) > 0
                template_count = len(templates)
                
                # Check for specific template types
                has_customer_satisfaction = any("Customer Satisfaction" in str(t) for t in templates)
                has_product_feedback = any("Product Feedback" in str(t) for t in templates)
                
                passed = has_templates
                details = f"Templates available: {template_count}"
                
                self.log_test("Template Availability", passed, details, response_time)
                self.log_test("Customer Satisfaction Template", has_customer_satisfaction, 
                            f"Customer Satisfaction template found: {has_customer_satisfaction}")
                self.log_test("Product Feedback Template", has_product_feedback, 
                            f"Product Feedback template found: {has_product_feedback}")
                
                return templates
            else:
                self.log_test("Template Availability", False, f"HTTP {response.status_code}", response_time)
                return []
                
        except Exception as e:
            self.log_test("Template Availability", False, f"Error: {str(e)[:50]}")
            return []
    
    def test_survey_generation_api(self):
        """Test the survey generation API endpoint"""
        print("\n🔌 TESTING SURVEY GENERATION API")
        print("=" * 50)
        
        try:
            # Test survey generation with valid data
            survey_data = {
                "SurveyId": f"test_survey_{int(time.time())}",
                "template_name": "MK Survey",  # Use existing template
                "Recipient": "Test User",
                "Phone": "+1234567890",
                "RiderName": "Test Rider",
                "RideId": "TEST_123",
                "TenantId": "test_tenant",
                "URL": "http://test.com",
                "Bilingual": True,
                "Name": "Test Survey Name"
            }
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/surveys/generate", 
                                   json=survey_data, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code in [200, 201]:
                data = response.json()
                has_questions = "QuestionswithAns" in data or "questions" in data
                has_survey_id = "SurveyId" in data or "survey_id" in data
                
                passed = has_questions and has_survey_id
                details = f"Survey generated - Questions: {has_questions}, ID: {has_survey_id}"
                
                self.log_test("Survey Generation API", passed, details, response_time)
                
                # Test response structure
                if has_questions:
                    questions = data.get("QuestionswithAns", data.get("questions", []))
                    question_count = len(questions)
                    self.log_test("Questions Generated", question_count > 0, 
                                f"Number of questions: {question_count}")
                
                return data
            else:
                error_details = f"HTTP {response.status_code} - {response.text[:100]}"
                self.log_test("Survey Generation API", False, error_details, response_time)
                return None
                
        except Exception as e:
            self.log_test("Survey Generation API", False, f"Error: {str(e)[:50]}")
            return None
    
    def test_survey_creation_vs_template_parity(self):
        """Test if survey creation and template creation are similar in backend"""
        print("\n🔄 TESTING SURVEY vs TEMPLATE PARITY")
        print("=" * 50)
        
        # Test template creation endpoint
        try:
            template_data = {
                "TemplateName": f"test_template_{int(time.time())}",
                "Description": "Test template for parity check",
                "Status": "Draft"
            }
            
            start_time = time.time()
            template_response = requests.post(f"{BASE_URL}/pg/api/templates/create", 
                                            json=template_data, timeout=10)
            template_time = time.time() - start_time
            
            template_success = template_response.status_code in [200, 201]
            self.log_test("Template Creation API", template_success, 
                        f"Template creation: {template_success}", template_time)
            
        except Exception as e:
            self.log_test("Template Creation API", False, f"Error: {str(e)[:50]}")
        
        # Test survey creation endpoint
        try:
            survey_data = {
                "SurveyId": f"test_parity_{int(time.time())}",
                "template_name": "MK Survey",
                "Recipient": "Parity Test",
                "Phone": "+1234567890",
                "RiderName": "Test Rider",
                "RideId": "PARITY_123",
                "TenantId": "test_tenant",
                "URL": "http://test.com",
                "Bilingual": True,
                "Name": "Parity Test Survey"
            }
            
            start_time = time.time()
            survey_response = requests.post(f"{BASE_URL}/api/surveys/generate", 
                                           json=survey_data, timeout=10)
            survey_time = time.time() - start_time
            
            survey_success = survey_response.status_code in [200, 201]
            self.log_test("Survey Creation API", survey_success, 
                        f"Survey creation: {survey_success}", survey_time)
            
            # Compare response structures
            if template_success and survey_success:
                template_data = template_response.json()
                survey_data = survey_response.json()
                
                # Check if both return similar structure
                both_have_id = bool(template_data) and bool(survey_data)
                self.log_test("Response Structure Parity", both_have_id, 
                            f"Both return structured data: {both_have_id}")
                
        except Exception as e:
            self.log_test("Survey Creation API", False, f"Error: {str(e)[:50]}")
    
    def test_form_validation(self):
        """Test form validation for survey creation"""
        print("\n✅ TESTING FORM VALIDATION")
        print("=" * 50)
        
        # Test missing required fields
        try:
            invalid_data = {
                "SurveyId": f"test_invalid_{int(time.time())}",
                "template_name": "",  # Empty template name
                "Recipient": "",      # Empty recipient
                "Phone": "",          # Empty phone
            }
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/surveys/generate", 
                                   json=invalid_data, timeout=10)
            response_time = time.time() - start_time
            
            # Should return validation error
            validation_error = response.status_code in [400, 422]
            self.log_test("Required Fields Validation", validation_error, 
                        f"Validation error returned: {validation_error}", response_time)
            
        except Exception as e:
            self.log_test("Required Fields Validation", False, f"Error: {str(e)[:50]}")
        
        # Test invalid template name
        try:
            invalid_template_data = {
                "SurveyId": f"test_invalid_template_{int(time.time())}",
                "template_name": "NonExistentTemplate",
                "Recipient": "Test User",
                "Phone": "+1234567890",
                "RiderName": "Test Rider",
                "RideId": "TEST_123",
                "TenantId": "test_tenant",
                "URL": "http://test.com",
                "Bilingual": True,
                "Name": "Test Survey"
            }
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/surveys/generate", 
                                   json=invalid_template_data, timeout=10)
            response_time = time.time() - start_time
            
            # Should return 404 for non-existent template
            template_not_found = response.status_code == 404
            self.log_test("Template Name Validation", template_not_found, 
                        f"Template not found error: {template_not_found}", response_time)
            
        except Exception as e:
            self.log_test("Template Name Validation", False, f"Error: {str(e)[:50]}")
    
    def test_survey_workflow(self):
        """Test complete survey creation workflow"""
        print("\n🔄 TESTING COMPLETE WORKFLOW")
        print("=" * 50)
        
        try:
            # Step 1: Get available templates
            templates_response = requests.get(f"{BASE_URL}/pg/api/templates/list", timeout=10)
            templates_available = templates_response.status_code == 200
            
            if not templates_available:
                self.log_test("Complete Workflow", False, "Templates not available")
                return
            
            templates = templates_response.json()
            if not templates:
                self.log_test("Complete Workflow", False, "No templates found")
                return
            
            template_name = templates[0].get("TemplateName", templates[0].get("name", "MK Survey"))
            
            # Step 2: Create survey
            survey_data = {
                "SurveyId": f"workflow_test_{int(time.time())}",
                "template_name": template_name,
                "Recipient": "Workflow Test User",
                "Phone": "+1234567890",
                "RiderName": "Workflow Test Rider",
                "RideId": "WORKFLOW_123",
                "TenantId": "test_tenant",
                "URL": "http://test.com",
                "Bilingual": True,
                "Name": "Workflow Test Survey"
            }
            
            start_time = time.time()
            survey_response = requests.post(f"{BASE_URL}/api/surveys/generate", 
                                           json=survey_data, timeout=10)
            response_time = time.time() - start_time
            
            survey_created = survey_response.status_code in [200, 201]
            
            if survey_created:
                # Step 3: Verify survey was created
                survey_id = survey_data["SurveyId"]
                verify_response = requests.get(f"{BASE_URL}/api/surveys/{survey_id}", timeout=10)
                survey_exists = verify_response.status_code == 200
                
                self.log_test("Complete Workflow", survey_exists and survey_created, 
                            f"Survey created and verified: {survey_created and survey_exists}", response_time)
                
                # Step 4: Check if survey appears in list
                list_response = requests.get(f"{BASE_URL}/api/surveys", timeout=10)
                if list_response.status_code == 200:
                    surveys = list_response.json()
                    new_survey_found = any(s.get("SurveyId") == survey_id or s.get("id") == survey_id for s in surveys)
                    self.log_test("Survey in List", new_survey_found, 
                                f"New survey found in list: {new_survey_found}")
                
            else:
                self.log_test("Complete Workflow", False, f"Survey creation failed: {survey_response.status_code}")
                
        except Exception as e:
            self.log_test("Complete Workflow", False, f"Error: {str(e)[:50]}")
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 COMPREHENSIVE CREATE SURVEY TEST")
        print("=" * 60)
        print(f"Testing URL: {BASE_URL}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all test suites
        self.test_frontend_accessibility()
        templates = self.test_template_availability()
        survey_data = self.test_survey_generation_api()
        self.test_survey_creation_vs_template_parity()
        self.test_form_validation()
        self.test_survey_workflow()
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate final test report"""
        print("\n📊 FINAL TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"📈 Overall Success Rate: {success_rate:.1f}%")
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
        print()
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! Create Survey is working perfectly!")
        elif success_rate >= 75:
            print("👍 GOOD! Create Survey is mostly functional")
        elif success_rate >= 50:
            print("⚠️  FAIR! Create Survey needs some improvements")
        else:
            print("🚨 POOR! Create Survey needs significant fixes")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["passed"]]
        if failed_tests:
            print("\n🔴 FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['name']}: {test['details']}")
        
        print("\n🎯 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   ✅ Create Survey is ready for production!")
            print("   ✅ Survey and Template creation are working properly")
        else:
            print("   🔧 Focus on fixing failed tests")
            print("   🔧 Ensure frontend and backend integration is working")
        
        print(f"\n🌐 Access Create Survey: {BASE_URL}/surveys/launch")
        print(f"📋 Access Survey Builder: {BASE_URL}/surveys/builder")
        
        total_time = time.time() - self.start_time
        print(f"\n⏱️  Total test time: {total_time:.2f}s")

if __name__ == "__main__":
    tester = CreateSurveyTester()
    tester.run_all_tests()
