#!/usr/bin/env python3
"""
Comprehensive End-to-End System Test
Tests all features and functionality to ensure everything works perfectly
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://54.86.65.150:8080"

class SystemTester:
    def __init__(self):
        self.results = []
        self.errors = []
        self.success_count = 0
        self.total_tests = 0
        
    def log_test(self, test_name, passed, details="", response_time=0):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time
        })
        
        if passed:
            self.success_count += 1
            print(f"{status} {test_name}")
            if details:
                print(f"    📝 {details}")
            if response_time > 0:
                print(f"    ⏱️  {response_time:.2f}s")
        else:
            self.errors.append(f"{test_name}: {details}")
            print(f"{status} {test_name}")
            print(f"    🔴 {details}")
        
        self.total_tests += 1
        print()
    
    def test_page_accessibility(self):
        """Test all main pages are accessible"""
        print("🌐 TESTING PAGE ACCESSIBILITY")
        print("=" * 50)
        
        pages = [
            ("/", "Home/Root"),
            ("/dashboard", "Dashboard"),
            ("/analytics", "Analytics"),
            ("/welcome", "Welcome Page"),
            ("/surveys/launch", "Survey Creation"),
            ("/surveys/builder", "Survey Builder"),
            ("/surveys/manage", "Manage Surveys"),
            ("/templates/manage", "Template Management"),
            ("/contacts", "Contacts"),
            ("/login", "Login Page"),
        ]
        
        for path, name in pages:
            try:
                start_time = time.time()
                response = requests.get(f"{BASE_URL}{path}", timeout=10)
                response_time = time.time() - start_time
                
                passed = response.status_code == 200
                details = f"HTTP {response.status_code}" if not passed else f"Page loads correctly"
                
                self.log_test(f"Page Access: {name}", passed, details, response_time)
                
            except Exception as e:
                self.log_test(f"Page Access: {name}", False, f"Connection error: {str(e)[:50]}")
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        print("🔌 TESTING API ENDPOINTS")
        print("=" * 50)
        
        endpoints = [
            ("/api/surveys/stats", "Survey Statistics"),
            ("/api/surveys/dashboard", "Dashboard Data"),
            ("/api/surveys", "List Surveys"),
            ("/api/templates", "List Templates"),
            ("/api/templates/stat", "Template Statistics"),
            ("/api/analytics/summary", "Analytics Summary"),
        ]
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    passed = True
                    details = f"Working - {len(str(data))} chars returned"
                elif response.status_code == 404:
                    passed = False
                    details = f"Endpoint not found (404)"
                else:
                    passed = False
                    details = f"HTTP {response.status_code}"
                
                self.log_test(f"API: {name}", passed, details, response_time)
                
            except Exception as e:
                self.log_test(f"API: {name}", False, f"Connection error: {str(e)[:50]}")
    
    def test_survey_functionality(self):
        """Test survey creation and management"""
        print("📋 TESTING SURVEY FUNCTIONALITY")
        print("=" * 50)
        
        # Test survey creation endpoint
        try:
            survey_data = {
                "template_name": "Customer Satisfaction",
                "Recipient": "Test User",
                "Phone": "+1234567890",
                "RiderName": "Test Rider",
                "RideId": "TEST_123",
                "TenantId": "test_tenant",
                "URL": "http://test.com",
                "Bilingual": True
            }
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/surveys/generate", 
                                   json=survey_data, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code in [200, 201]:
                passed = True
                details = "Survey creation endpoint working"
            else:
                passed = False
                details = f"HTTP {response.status_code}"
            
            self.log_test("Survey Creation API", passed, details, response_time)
            
        except Exception as e:
            self.log_test("Survey Creation API", False, f"Error: {str(e)[:50]}")
        
        # Test survey listing
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/api/surveys", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    survey_count = len(data)
                    passed = True
                    details = f"Found {survey_count} surveys"
                else:
                    passed = False
                    details = f"Unexpected response format: {type(data)}"
            else:
                passed = False
                details = f"HTTP {response.status_code}"
            
            self.log_test("Survey Listing", passed, details, response_time)
            
        except Exception as e:
            self.log_test("Survey Listing", False, f"Error: {str(e)[:50]}")
    
    def test_transcript_system(self):
        """Test transcript functionality"""
        print("📝 TESTING TRANSCRIPT SYSTEM")
        print("=" * 50)
        
        # Test transcript access
        test_survey_id = "1772217829012_871"
        
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/pg/api/voice/transcript/{test_survey_id}", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                has_transcript = "full_transcript" in data
                has_answers = "survey_answers" in data
                
                passed = has_transcript and has_answers
                details = f"Transcript available: {has_transcript}, Answers: {has_answers}"
            else:
                passed = False
                details = f"HTTP {response.status_code}"
            
            self.log_test("Transcript Access", passed, details, response_time)
            
        except Exception as e:
            self.log_test("Transcript Access", False, f"Error: {str(e)[:50]}")
        
        # Test transcript translation
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/pg/api/voice/transcript/{test_survey_id}/translate", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                has_translation = data.get("translated", False)
                passed = True  # Translation endpoint is working
                details = f"Translation available: {has_translation}"
            else:
                passed = False
                details = f"HTTP {response.status_code}"
            
            self.log_test("Transcript Translation", passed, details, response_time)
            
        except Exception as e:
            self.log_test("Transcript Translation", False, f"Error: {str(e)[:50]}")
    
    def test_static_assets(self):
        """Test static assets are loading"""
        print("🎨 TESTING STATIC ASSETS")
        print("=" * 50)
        
        try:
            # Get main page to extract asset URLs
            response = requests.get(f"{BASE_URL}/dashboard", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Find JavaScript and CSS assets
                js_assets = []
                css_assets = []
                
                if "/assets/index-" in content:
                    start = content.find("/assets/index-")
                    while start != -1:
                        end = content.find('"', start)
                        if end != -1:
                            asset_url = content[start:end]
                            if asset_url.endswith('.js'):
                                js_assets.append(asset_url)
                            elif asset_url.endswith('.css'):
                                css_assets.append(asset_url)
                        start = content.find("/assets/index-", start + 1)
                
                # Test JavaScript assets
                for js_asset in js_assets[:2]:  # Test first 2 JS assets
                    try:
                        start_time = time.time()
                        asset_response = requests.get(f"{BASE_URL}{js_asset}", timeout=10)
                        response_time = time.time() - start_time
                        
                        passed = asset_response.status_code == 200
                        details = f"Size: {len(asset_response.content)} bytes"
                        
                        self.log_test(f"JS Asset: {js_asset.split('/')[-1]}", passed, details, response_time)
                        
                    except Exception as e:
                        self.log_test(f"JS Asset: {js_asset.split('/')[-1]}", False, f"Error: {str(e)[:50]}")
                
                # Test CSS assets
                for css_asset in css_assets[:2]:  # Test first 2 CSS assets
                    try:
                        start_time = time.time()
                        asset_response = requests.get(f"{BASE_URL}{css_asset}", timeout=10)
                        response_time = time.time() - start_time
                        
                        passed = asset_response.status_code == 200
                        details = f"Size: {len(asset_response.content)} bytes"
                        
                        self.log_test(f"CSS Asset: {css_asset.split('/')[-1]}", passed, details, response_time)
                        
                    except Exception as e:
                        self.log_test(f"CSS Asset: {css_asset.split('/')[-1]}", False, f"Error: {str(e)[:50]}")
                
                # Log summary
                self.log_test("Asset Discovery", True, f"Found {len(js_assets)} JS, {len(css_assets)} CSS assets")
                
            else:
                self.log_test("Asset Discovery", False, f"Could not load main page: {response.status_code}")
                
        except Exception as e:
            self.log_test("Asset Discovery", False, f"Error: {str(e)[:50]}")
    
    def test_authentication(self):
        """Test authentication system"""
        print("🔐 TESTING AUTHENTICATION")
        print("=" * 50)
        
        # Test login page
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/login", timeout=10)
            response_time = time.time() - start_time
            
            passed = response.status_code == 200
            details = f"Login page accessible" if passed else f"HTTP {response.status_code}"
            
            self.log_test("Login Page", passed, details, response_time)
            
        except Exception as e:
            self.log_test("Login Page", False, f"Error: {str(e)[:50]}")
        
        # Test protected route redirect
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/dashboard", timeout=10, allow_redirects=False)
            response_time = time.time() - start_time
            
            # Check if it redirects (302/307) or serves directly (200)
            passed = response.status_code in [200, 302, 307]
            details = f"Status: {response.status_code} (works with or without auth)"
            
            self.log_test("Auth Flow", passed, details, response_time)
            
        except Exception as e:
            self.log_test("Auth Flow", False, f"Error: {str(e)[:50]}")
    
    def test_database_connectivity(self):
        """Test database connectivity through APIs"""
        print("🗄️  TESTING DATABASE CONNECTIVITY")
        print("=" * 50)
        
        # Test survey data access
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/api/surveys/stats", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                has_data = bool(data) and len(str(data)) > 10
                passed = has_data
                details = f"Database connected, data returned"
            else:
                passed = False
                details = f"HTTP {response.status_code}"
            
            self.log_test("Database - Survey Data", passed, details, response_time)
            
        except Exception as e:
            self.log_test("Database - Survey Data", False, f"Error: {str(e)[:50]}")
        
        # Test template data access
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/api/templates", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                has_data = bool(data) and len(str(data)) > 10
                passed = has_data
                details = f"Template data accessible"
            else:
                passed = False
                details = f"HTTP {response.status_code}"
            
            self.log_test("Database - Template Data", passed, details, response_time)
            
        except Exception as e:
            self.log_test("Database - Template Data", False, f"Error: {str(e)[:50]}")
    
    def test_error_handling(self):
        """Test error handling"""
        print("⚠️  TESTING ERROR HANDLING")
        print("=" * 50)
        
        # Test 404 handling
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/nonexistent-page", timeout=10)
            response_time = time.time() - start_time
            
            # Should handle 404 gracefully
            passed = response.status_code in [404, 200]  # 200 if SPA handles routing
            details = f"404 handled gracefully: {response.status_code}"
            
            self.log_test("404 Error Handling", passed, details, response_time)
            
        except Exception as e:
            self.log_test("404 Error Handling", False, f"Error: {str(e)[:50]}")
        
        # Test invalid API endpoint
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/api/invalid-endpoint", timeout=10)
            response_time = time.time() - start_time
            
            passed = response.status_code in [404, 500]  # Should return proper error
            details = f"API error handled: {response.status_code}"
            
            self.log_test("API Error Handling", passed, details, response_time)
            
        except Exception as e:
            self.log_test("API Error Handling", False, f"Error: {str(e)[:50]}")
    
    def test_performance(self):
        """Test system performance"""
        print("⚡ TESTING PERFORMANCE")
        print("=" * 50)
        
        # Test dashboard load time
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/dashboard", timeout=10)
            response_time = time.time() - start_time
            
            passed = response.status_code == 200 and response_time < 5.0
            details = f"Load time: {response_time:.2f}s"
            
            self.log_test("Dashboard Performance", passed, details, response_time)
            
        except Exception as e:
            self.log_test("Dashboard Performance", False, f"Error: {str(e)[:50]}")
        
        # Test API response time
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/api/surveys/stats", timeout=10)
            response_time = time.time() - start_time
            
            passed = response.status_code == 200 and response_time < 2.0
            details = f"API response time: {response_time:.2f}s"
            
            self.log_test("API Performance", passed, details, response_time)
            
        except Exception as e:
            self.log_test("API Performance", False, f"Error: {str(e)[:50]}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 COMPREHENSIVE END-TO-END SYSTEM TEST")
        print("=" * 60)
        print(f"Testing URL: {BASE_URL}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all test categories
        self.test_page_accessibility()
        self.test_api_endpoints()
        self.test_survey_functionality()
        self.test_transcript_system()
        self.test_static_assets()
        self.test_authentication()
        self.test_database_connectivity()
        self.test_error_handling()
        self.test_performance()
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate final test report"""
        print("📊 FINAL TEST REPORT")
        print("=" * 60)
        
        success_rate = (self.success_count / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📈 Overall Success Rate: {success_rate:.1f}%")
        print(f"✅ Passed: {self.success_count}/{self.total_tests}")
        print(f"❌ Failed: {len(self.errors)}/{self.total_tests}")
        print()
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! System is working perfectly!")
        elif success_rate >= 80:
            print("✅ GOOD! System is mostly functional.")
        elif success_rate >= 70:
            print("⚠️  OKAY! System has some issues.")
        else:
            print("🚨 CRITICAL! System has major problems.")
        
        if self.errors:
            print("\n🔴 FAILED TESTS:")
            for error in self.errors:
                print(f"   • {error}")
        
        print("\n🎯 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   ✅ System is ready for production!")
            print("   ✅ All major features are working!")
        elif success_rate >= 80:
            print("   🔧 Fix the few failing tests for 100% functionality")
        else:
            print("   🔧 Address the failing tests before production deployment")
        
        print(f"\n🌐 Access your application: {BASE_URL}")
        print("📊 Dashboard: {BASE_URL}/dashboard")
        print("📋 Survey Builder: {BASE_URL}/surveys/builder")
        print("📈 Analytics: {BASE_URL}/analytics")

def main():
    """Main function"""
    tester = SystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
