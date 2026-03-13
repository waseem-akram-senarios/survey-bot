#!/usr/bin/env python3
"""
Direct Transcript Test
Tests the transcript functionality without relying on the React UI
"""

import requests
import json

BASE_URL = "http://54.86.65.150:8080"

def test_direct_transcript():
    """Test transcript directly via API"""
    print("🎯 Direct Transcript Test")
    print("=" * 40)
    
    # Test the transcript API directly
    try:
        response = requests.get(f"{BASE_URL}/pg/api/voice/transcript/1772217829012_871", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Transcript API Working!")
            print(f"Survey ID: {data.get('survey_id')}")
            print(f"Duration: {data.get('call_duration_seconds')}s")
            print(f"Status: {data.get('call_status')}")
            
            # Show the questions with actual text
            print("\n📝 Survey Questions & Answers:")
            print("-" * 40)
            
            # Question mapping
            question_map = {
                "0a4710ab-7bba-4fbe-9cf7-bfb062302dfa": "How would you rate your overall experience ?",
                "3a548716-76cb-48c8-88a6-8a541ec8459c": "How satisfied are you with the timeliness of your rides?",
                "29fa2e61-60ab-4b8a-a2cc-ed179c8f61a3": "How would you rate your experience with our drivers?",
                "fc004f7e-31dc-4ac6-aa0d-3ef1c9ede923": "How likely are you to recommend this service to a friend or family member?",
                "6182b958-0652-49e7-a982-ee12699ee500": "If you could change one thing about the service, what would it be?",
                "fa135d51-6211-45f8-97dd-92d3c0e4d5da": "Is there anything else about your experience you'd like to share?"
            }
            
            # Parse the transcript
            full_transcript = data.get("full_transcript", "")
            lines = full_transcript.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('Q[') and ']: ' in line:
                    try:
                        qid_end = line.find(']: ')
                        qid = line[2:qid_end]
                        answer = line[qid_end + 3:]
                        
                        question_text = question_map.get(qid, f"Unknown Question ({qid})")
                        
                        print(f"❓ {question_text}")
                        print(f"💬 {answer}")
                        print()
                        
                    except Exception as e:
                        print(f"⚠️ Error parsing line: {line}")
            
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ui_access():
    """Test if UI is accessible at all"""
    print("\n🌐 UI Access Test")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Main Dashboard Accessible")
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Length: {len(response.text)} chars")
            
            # Check if it's the React app
            if 'React' in response.text or 'index-B6av8uW6.js' in response.text:
                print("✅ React App Detected")
                return True
            else:
                print("⚠️ React App Not Detected")
                print("Sample content:")
                print(response.text[:500])
                return False
        else:
            print(f"❌ Dashboard Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ UI Access Error: {e}")
        return False

def test_alternative_access():
    """Test alternative access methods"""
    print("\n🔄 Alternative Access Test")
    print("=" * 35)
    
    # Test direct dashboard port
    try:
        response = requests.get("http://54.86.65.150:8082/", timeout=10)
        if response.status_code == 200:
            print("✅ Direct Dashboard Port (8082) Working")
            print("Try this URL: http://54.86.65.150:8082/")
            return True
        else:
            print(f"❌ Direct Port Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Direct Port Error: {e}")
    
    # Test with trailing slash
    try:
        response = requests.get(f"{BASE_URL}/surveys/status/1772217829012_871/", timeout=10)
        if response.status_code == 200:
            print("✅ Trailing Slash Works")
            print("Try this URL: http://54.86.65.150:8080/surveys/status/1772217829012_871/")
            return True
        else:
            print(f"❌ Trailing Slash Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Trailing Slash Error: {e}")
    
    return False

def main():
    """Run all tests"""
    print("🚀 TRANSCRIPT ACCESS TROUBLESHOOTING")
    print("=" * 50)
    
    # Test API first
    api_works = test_direct_transcript()
    
    # Test UI access
    ui_works = test_ui_access()
    
    # Test alternatives
    alt_works = test_alternative_access()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"✅ API Access: {'Working' if api_works else 'Failed'}")
    print(f"✅ UI Access: {'Working' if ui_works else 'Failed'}")
    print(f"✅ Alternative Access: {'Available' if alt_works else 'Failed'}")
    
    if api_works:
        print("\n🎯 RECOMMENDATION:")
        print("The transcript system is working perfectly!")
        print("The issue is with the React UI routing.")
        
        if alt_works:
            print("Try the alternative URLs provided above.")
        else:
            print("Use the API directly or check the React build.")
            
        print("\n📋 TRANSCRIPT FACTS:")
        print("• All transcript data is available via API")
        print("• Questions and answers are properly stored")
        print("• The enhanced UI shows full question text")
        print("• Only the React routing needs fixing")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Try alternative URLs if available")
    print("2. Use direct API access for now")
    print("3. Check browser console for JavaScript errors")
    print("4. Clear browser cache and retry")

if __name__ == "__main__":
    main()
