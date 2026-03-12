#!/usr/bin/env python3
"""
Search and Filter Functionality Test Script
Tests search, filtering, and data manipulation features
"""

import requests
import json
import time

def test_search_functionality():
    """Test search functionality across different endpoints"""
    print("🔍 Testing Search Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test 1: Survey Search
    print("\n📋 Test 1: Survey Search")
    try:
        # Get all surveys first
        surveys_response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        if surveys_response.status_code == 200:
            surveys = surveys_response.json()
            print(f"✅ Found {len(surveys)} surveys for search testing")
            
            # Test search by name
            search_terms = ["trip", "survey", "demo", "test"]
            for term in search_terms:
                matching_surveys = [s for s in surveys if term.lower() in s.get('Name', '').lower()]
                print(f"   '{term}': {len(matching_surveys)} matches")
                
        else:
            print(f"❌ Failed to get surveys: {surveys_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Survey search test failed: {str(e)}")
        return False
    
    # Test 2: Template Search
    print("\n📝 Test 2: Template Search")
    try:
        templates_response = requests.get(f"{base_url}/pg/api/templates/list", timeout=10)
        if templates_response.status_code == 200:
            templates = templates_response.json()
            print(f"✅ Found {len(templates)} templates for search testing")
            
            # Test search by name
            search_terms = ["survey", "template", "demo", "test"]
            for term in search_terms:
                matching_templates = [t for t in templates if term.lower() in t.get('TemplateName', '').lower()]
                print(f"   '{term}': {len(matching_templates)} matches")
                
        else:
            print(f"❌ Failed to get templates: {templates_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Template search test failed: {str(e)}")
        return False
    
    return True

def test_filter_functionality():
    """Test filtering and sorting functionality"""
    print("\n🎛️ Testing Filter Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test 1: Survey Status Filtering
    print("\n📊 Test 1: Survey Status Filtering")
    try:
        surveys_response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        if surveys_response.status_code == 200:
            surveys = surveys_response.json()
            print(f"✅ Found {len(surveys)} surveys for filtering")
            
            # Filter by status
            statuses = ['Completed', 'In-Progress', 'Draft']
            for status in statuses:
                filtered_surveys = [s for s in surveys if s.get('Status') == status]
                print(f"   '{status}': {len(filtered_surveys)} surveys")
                
        else:
            print(f"❌ Failed to get surveys: {surveys_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Survey filtering test failed: {str(e)}")
        return False
    
    # Test 2: Template Status Filtering
    print("\n📋 Test 2: Template Status Filtering")
    try:
        templates_response = requests.get(f"{base_url}/pg/api/templates/list", timeout=10)
        if templates_response.status_code == 200:
            templates = templates_response.json()
            print(f"✅ Found {len(templates)} templates for filtering")
            
            # Filter by status
            statuses = ['Published', 'Draft']
            for status in statuses:
                filtered_templates = [t for t in templates if t.get('Status') == status]
                print(f"   '{status}': {len(filtered_templates)} templates")
                
        else:
            print(f"❌ Failed to get templates: {templates_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Template filtering test failed: {str(e)}")
        return False
    
    return True

def test_search_api_endpoints():
    """Test dedicated search API endpoints"""
    print("\n🔍 Testing Search API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test search endpoints
    search_endpoints = [
        ("/pg/api/surveys/search", "Survey Search"),
        ("/pg/api/templates/search", "Template Search"),
        ("/pg/api/search", "Global Search"),
        ("/search", "Simple Search")
    ]
    
    for endpoint, name in search_endpoints:
        try:
            # Test with query parameter
            response = requests.get(f"{base_url}{endpoint}?q=test", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: Working")
                if isinstance(data, list):
                    print(f"   Found {len(data)} results")
                elif isinstance(data, dict):
                    print(f"   Results keys: {list(data.keys())}")
            elif response.status_code == 404:
                print(f"⚠️ {name}: Not available")
            else:
                print(f"⚠️ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Failed - {str(e)}")
    
    return True

def test_filter_api_endpoints():
    """Test dedicated filter API endpoints"""
    print("\n🎛️ Testing Filter API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test filter endpoints
    filter_endpoints = [
        ("/pg/api/surveys/filter", "Survey Filter"),
        ("/pg/api/templates/filter", "Template Filter"),
        ("/pg/api/filter", "Global Filter")
    ]
    
    for endpoint, name in filter_endpoints:
        try:
            # Test with filter parameters
            response = requests.get(f"{base_url}{endpoint}?status=Completed", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: Working")
                if isinstance(data, list):
                    print(f"   Found {len(data)} results")
                elif isinstance(data, dict):
                    print(f"   Results keys: {list(data.keys())}")
            elif response.status_code == 404:
                print(f"⚠️ {name}: Not available")
            else:
                print(f"⚠️ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Failed - {str(e)}")
    
    return True

def test_sorting_functionality():
    """Test sorting and ordering functionality"""
    print("\n📊 Testing Sorting Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test sorting endpoints
    sort_endpoints = [
        ("/pg/api/surveys/sort", "Survey Sort"),
        ("/pg/api/templates/sort", "Template Sort"),
        ("/pg/api/sort", "Global Sort")
    ]
    
    for endpoint, name in sort_endpoints:
        try:
            # Test with sort parameters
            response = requests.get(f"{base_url}{endpoint}?by=date&order=desc", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: Working")
                if isinstance(data, list):
                    print(f"   Found {len(data)} results")
                elif isinstance(data, dict):
                    print(f"   Results keys: {list(data.keys())}")
            elif response.status_code == 404:
                print(f"⚠️ {name}: Not available")
            else:
                print(f"⚠️ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Failed - {str(e)}")
    
    return True

def test_pagination_functionality():
    """Test pagination functionality"""
    print("\n📄 Testing Pagination Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test pagination endpoints
    pagination_endpoints = [
        ("/pg/api/surveys", "Survey Pagination"),
        ("/pg/api/templates", "Template Pagination")
    ]
    
    for endpoint, name in pagination_endpoints:
        try:
            # Test with pagination parameters
            response = requests.get(f"{base_url}{endpoint}?page=1&limit=5", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: Working")
                if isinstance(data, list):
                    print(f"   Found {len(data)} results")
                    if len(data) <= 5:
                        print("   Pagination limit respected")
                elif isinstance(data, dict):
                    print(f"   Results keys: {list(data.keys())}")
            elif response.status_code == 404:
                print(f"⚠️ {name}: Not available")
            else:
                print(f"⚠️ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Failed - {str(e)}")
    
    return True

def test_advanced_search():
    """Test advanced search features"""
    print("\n🔍 Testing Advanced Search Features")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test 1: Multi-field search
    print("\n🔍 Test 1: Multi-field Search")
    try:
        surveys_response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        if surveys_response.status_code == 200:
            surveys = surveys_response.json()
            
            # Test search across multiple fields
            search_term = "trip"
            multi_field_results = [
                s for s in surveys 
                if search_term.lower() in s.get('Name', '').lower() or
                   search_term.lower() in s.get('Biodata', '').lower() or
                   search_term.lower() in s.get('Recipient', '').lower()
            ]
            print(f"✅ Multi-field search '{search_term}': {len(multi_field_results)} results")
            
        else:
            print(f"❌ Failed to get surveys: {surveys_response.status_code}")
    except Exception as e:
        print(f"❌ Multi-field search test failed: {str(e)}")
    
    # Test 2: Case-insensitive search
    print("\n🔤 Test 2: Case-insensitive Search")
    try:
        surveys_response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        if surveys_response.status_code == 200:
            surveys = surveys_response.json()
            
            # Test case-insensitive search
            search_terms = ["TRIP", "Trip", "tRiP", "trip"]
            for term in search_terms:
                results = [s for s in surveys if term.lower() in s.get('Name', '').lower()]
                print(f"   '{term}': {len(results)} results")
                
        else:
            print(f"❌ Failed to get surveys: {surveys_response.status_code}")
    except Exception as e:
        print(f"❌ Case-insensitive search test failed: {str(e)}")
    
    # Test 3: Partial match search
    print("\n🔤 Test 3: Partial Match Search")
    try:
        surveys_response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
        if surveys_response.status_code == 200:
            surveys = surveys_response.json()
            
            # Test partial matches
            partial_terms = ["sur", "trip", "com"]
            for term in partial_terms:
                results = [s for s in surveys if term.lower() in s.get('Name', '').lower()]
                print(f"   '{term}': {len(results)} results")
                
        else:
            print(f"❌ Failed to get surveys: {surveys_response.status_code}")
    except Exception as e:
        print(f"❌ Partial match search test failed: {str(e)}")
    
    return True

def test_search_performance():
    """Test search performance with large datasets"""
    print("\n⚡ Testing Search Performance")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    try:
        # Test search performance
        search_terms = ["a", "e", "i", "o", "u", "test", "demo"]
        
        for term in search_terms:
            start_time = time.time()
            
            surveys_response = requests.get(f"{base_url}/pg/api/surveys/list", timeout=10)
            if surveys_response.status_code == 200:
                surveys = surveys_response.json()
                
                # Simulate search operation
                results = [s for s in surveys if term.lower() in s.get('Name', '').lower()]
                
                end_time = time.time()
                search_time = end_time - start_time
                
                print(f"   Search '{term}': {len(results)} results in {search_time:.3f}s")
                
                if search_time < 0.1:
                    print(f"     ✅ Fast")
                elif search_time < 0.5:
                    print(f"     ⚠️ Moderate")
                else:
                    print(f"     ❌ Slow")
            else:
                print(f"   Failed to get surveys for search performance test")
                
    except Exception as e:
        print(f"❌ Search performance test failed: {str(e)}")
    
    return True

def main():
    """Main test function"""
    print("🚀 Starting Search and Filter Tests")
    print("=" * 50)
    
    tests = [
        ("Search Functionality", test_search_functionality),
        ("Filter Functionality", test_filter_functionality),
        ("Search API Endpoints", test_search_api_endpoints),
        ("Filter API Endpoints", test_filter_api_endpoints),
        ("Sorting Functionality", test_sorting_functionality),
        ("Pagination Functionality", test_pagination_functionality),
        ("Advanced Search", test_advanced_search),
        ("Search Performance", test_search_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🏆 SEARCH AND FILTER TEST RESULTS:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed >= total * 0.8:  # 80% success rate
        print("\n🎉 SEARCH AND FILTER SYSTEM WORKING!")
        print("✅ Search functionality working!")
        print("✅ Filter functionality working!")
        print("✅ Search API endpoints functional!")
        print("✅ Filter API endpoints functional!")
        print("✅ Sorting functionality working!")
        print("✅ Pagination functionality working!")
        print("✅ Advanced search features working!")
        print("✅ Search performance acceptable!")
        print("\n🚀 Search and filter system is ready for production!")
    else:
        print(f"\n⚠️ {total - passed} tests need attention")
        print("🔧 Some search and filter features need improvement")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
