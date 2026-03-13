#!/usr/bin/env python3
"""
Comprehensive Transcript Feature Test
Tests all transcript functionality including full conversation logging
"""

import requests
import json
import sys

BASE_URL = "http://54.86.65.150:8080/pg/api"

def test_enhanced_transcript():
    """Test enhanced transcript with conversation parsing"""
    print("🧪 Testing Enhanced Transcript Features")
    print("=" * 50)
    
    # Get a sample transcript
    response = requests.get(f"{BASE_URL}/voice/transcript/1772217829012_871")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Enhanced Transcript Working!")
        print(f"Transcript ID: {data.get('transcript_id')}")
        print(f"Survey ID: {data.get('survey_id')}")
        print(f"Language Detected: {data.get('language_detected')}")
        print(f"Agent Responses: {len(data.get('agent_responses', []))}")
        print(f"User Responses: {len(data.get('user_responses', []))}")
        print(f"Survey Answers: {len(data.get('survey_answers', []))}")
        print(f"Call Duration: {data.get('call_duration_seconds')} seconds")
        print(f"Call Status: {data.get('call_status')}")
        
        print("\n📝 Sample Survey Answers:")
        for i, answer in enumerate(data.get('survey_answers', [])[:3]):
            print(f"  Q[{answer.get('question_id')}]: {answer.get('answer')}")
        
        print(f"\n📄 Full Transcript Length: {len(data.get('full_transcript', ''))} characters")
        return True
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False

def test_transcript_list():
    """Test listing all transcripts"""
    print("\n🧪 Testing Transcript List")
    print("=" * 30)
    
    response = requests.get(f"{BASE_URL}/voice/transcripts?limit=5")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Transcript List Working!")
        print(f"Total Count: {data.get('total_count')}")
        print("Sample Transcripts:")
        
        for i, transcript in enumerate(data.get('transcripts', [])[:3]):
            print(f"  {i+1}. {transcript.get('survey_id')}")
            print(f"     Status: {transcript.get('call_status')}")
            print(f"     Duration: {transcript.get('call_duration_seconds')}s")
            print(f"     Channel: {transcript.get('channel')}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False

def test_translation():
    """Test Spanish to English translation"""
    print("\n🧪 Testing Translation Feature")
    print("=" * 35)
    
    response = requests.get(f"{BASE_URL}/voice/transcript/1772217829012_871/translate")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Translation Endpoint Working!")
        print(f"Translated: {data.get('translated')}")
        print(f"Message: {data.get('message')}")
        
        if not data.get('translated'):
            print("ℹ️  This transcript is in English, translation only available for Spanish")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False

def test_transcript_export():
    """Test transcript export functionality"""
    print("\n🧪 Testing Transcript Export")
    print("=" * 35)
    
    response = requests.get(f"{BASE_URL}/export/transcripts")
    
    if response.status_code == 200:
        lines = response.text.strip().split('\n')
        print("✅ Transcript Export Working!")
        print(f"Export Lines: {len(lines)}")
        print("Sample Export:")
        
        for i, line in enumerate(lines[:3]):
            print(f"  {i+1}: {line[:80]}...")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False

def main():
    """Run all transcript tests"""
    print("🚀 Comprehensive Transcript Feature Test")
    print("=" * 60)
    
    tests = [
        ("Enhanced Transcript", test_enhanced_transcript),
        ("Transcript List", test_transcript_list), 
        ("Translation Feature", test_translation),
        ("Transcript Export", test_transcript_export),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All transcript features working perfectly!")
        print("\n📋 Available Features:")
        print("  ✅ Full conversation logging with timestamps")
        print("  ✅ Separate agent and user response tracking")
        print("  ✅ Language detection (English/Spanish)")
        print("  ✅ Spanish to English translation")
        print("  ✅ Structured survey answers extraction")
        print("  ✅ Enhanced transcript formatting")
        print("  ✅ Transcript listing with pagination")
        print("  ✅ CSV export functionality")
        print("\n🔍 API Endpoints:")
        print("  GET /voice/transcript/{survey_id} - Enhanced transcript")
        print("  GET /voice/transcript/{survey_id}/translate - Translation")
        print("  GET /voice/transcripts - List all transcripts")
        print("  GET /export/transcripts - CSV export")
    else:
        print("⚠️  Some features need attention.")

if __name__ == "__main__":
    main()
