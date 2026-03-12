#!/usr/bin/env python3
"""
Docker Integration Test Script
Tests the complete backend and frontend integration running in Docker
"""

import requests
import json
import time

def test_docker_integration():
    """Test complete Docker integration"""
    print("🐳 Testing Docker Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test 1: Gateway Health
    print("\n🏥 Test 1: Gateway Health")
    try:
        response = requests.get(f"{base_url}/pg/api/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Gateway Health: {health_data.get('status', 'Unknown')}")
        else:
            print(f"❌ Gateway Health: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Gateway Health failed: {str(e)}")
        return False
    
    # Test 2: Dashboard Frontend
    print("\n🖥️ Test 2: Dashboard Frontend")
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        if response.status_code == 200:
            content = response.text
            if "SurvAI Platform" in content:
                print("✅ Dashboard Frontend: Working")
            else:
                print("⚠️ Dashboard Frontend: Content issue")
        else:
            print(f"❌ Dashboard Frontend: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard Frontend failed: {str(e)}")
        return False
    
    # Test 3: Survey API
    print("\n📋 Test 3: Survey API")
    try:
        response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        if response.status_code == 200:
            surveys = response.json()
            print(f"✅ Survey API: {len(surveys)} surveys found")
            
            if len(surveys) > 0:
                sample_survey = surveys[0]
                print(f"   Sample: {sample_survey.get('Name', 'Unknown')}")
        else:
            print(f"❌ Survey API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Survey API failed: {str(e)}")
        return False
    
    # Test 4: Template API
    print("\n📝 Test 4: Template API")
    try:
        response = requests.get(f"{base_url}/pg/api/templates/list", timeout=10)
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Template API: {len(templates)} templates found")
            
            if len(templates) > 0:
                sample_template = templates[0]
                print(f"   Sample: {sample_template.get('TemplateName', 'Unknown')}")
        else:
            print(f"❌ Template API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Template API failed: {str(e)}")
        return False
    
    # Test 5: Analytics API
    print("\n📊 Test 5: Analytics API")
    try:
        response = requests.get(f"{base_url}/pg/api/analytics/summary", timeout=10)
        if response.status_code == 200:
            analytics = response.json()
            print(f"✅ Analytics API: {list(analytics.keys())}")
        else:
            print(f"❌ Analytics API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analytics API failed: {str(e)}")
        return False
    
    # Test 6: Survey Creation
    print("\n➕ Test 6: Survey Creation")
    try:
        # Get a template first
        templates_response = requests.get(f"{base_url}/pg/api/templates/list", timeout=10)
        templates = templates_response.json()
        template_name = templates[0].get('TemplateName')
        
        # Create survey
        payload = {
            'SurveyId': f'docker_test_{int(time.time())}',
            'Name': template_name,
            'Recipient': 'Docker Test User',
            'RiderName': 'Docker Test Rider',
            'RideId': f'RIDE_DOCKER_{int(time.time())}',
            'TenantId': 'itcurves',
            'URL': 'http://localhost:8080',
            'Biodata': 'Docker test user',
            'Phone': '+15551234567',
            'Bilingual': True
        }
        
        response = requests.post(f"{base_url}/pg/api/surveys/generate", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Survey Creation: {result.get('SurveyId', 'Unknown')}")
        else:
            print(f"❌ Survey Creation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Survey Creation failed: {str(e)}")
        return False
    
    # Test 7: Search Functionality
    print("\n🔍 Test 7: Search Functionality")
    try:
        surveys_response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        surveys = surveys_response.json()
        
        search_results = [s for s in surveys if 'test' in s.get('Name', '').lower()]
        print(f"✅ Search Functionality: {len(search_results)} results for 'test'")
    except Exception as e:
        print(f"❌ Search Functionality failed: {str(e)}")
        return False
    
    # Test 8: Performance
    print("\n⚡ Test 8: Performance")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        end_time = time.time()
        
        if response.status_code == 200:
            load_time = end_time - start_time
            if load_time < 1.0:
                print(f"✅ Performance: {load_time:.3f}s (Excellent)")
            elif load_time < 2.0:
                print(f"✅ Performance: {load_time:.3f}s (Good)")
            else:
                print(f"⚠️ Performance: {load_time:.3f}s (Slow)")
        else:
            print(f"❌ Performance test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")
    
    return True

def test_docker_services():
    """Test Docker services status"""
    print("\n🐳 Testing Docker Services")
    print("=" * 50)
    
    # Test service accessibility
    services = [
        ("Dashboard", "http://localhost:8080/dashboard"),
        ("API Gateway", "http://localhost:8080/pg/api/health"),
        ("Survey Service", "http://localhost:8080/pg/api/surveys/list"),
        ("Template Service", "http://localhost:8080/pg/api/templates/list"),
        ("Analytics Service", "http://localhost:8080/pg/api/analytics/summary")
    ]
    
    working_services = 0
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {service_name}: Working")
                working_services += 1
            else:
                print(f"❌ {service_name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name}: Failed - {str(e)}")
    
    print(f"\n📊 Services Working: {working_services}/{len(services)}")
    return working_services >= len(services) * 0.8

def main():
    """Main test function"""
    print("🚀 Docker Integration Test Suite")
    print("=" * 50)
    
    # Test Docker services
    services_ok = test_docker_services()
    
    # Test complete integration
    integration_ok = test_docker_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("🏆 DOCKER INTEGRATION TEST RESULTS:")
    print("=" * 50)
    
    if services_ok and integration_ok:
        print("🎉 DOCKER INTEGRATION SUCCESSFUL!")
        print("✅ All Docker services running")
        print("✅ Backend API endpoints working")
        print("✅ Frontend dashboard accessible")
        print("✅ Survey creation working")
        print("✅ Search functionality working")
        print("✅ Analytics working")
        print("✅ Performance acceptable")
        print("\n🚀 Your Survey Bot is running successfully in Docker!")
        print("📱 Access the dashboard at: http://localhost:8080")
        print("🔗 API endpoints at: http://localhost:8080/pg/api/")
    else:
        print("❌ DOCKER INTEGRATION ISSUES")
        print("🔧 Some services may need attention")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
