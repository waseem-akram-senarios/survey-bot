#!/usr/bin/env python3
"""
Perfect Transcript Viewer
Shows full conversation with actual question text for survey 1772217829012_871
"""

import requests
import json

BASE_URL = "http://54.86.65.150:8080"

def get_mk_survey_questions():
    """Get the actual questions from MK Survey template"""
    questions = {
        "0a4710ab-7bba-4fbe-9cf7-bfb062302dfa": "How would you rate your overall experience ?",
        "3a548716-76cb-48c8-88a6-8a541ec8459c": "How satisfied are you with the timeliness of your rides?",
        "29fa2e61-60ab-4b8a-a2cc-ed179c8f61a3": "How would you rate your experience with our drivers?",
        "fc004f7e-31dc-4ac6-aa0d-3ef1c9ede923": "How likely are you to recommend this service to a friend or family member?",
        "6182b958-0652-49e7-a982-ee12699ee500": "If you could change one thing about the service, what would it be?",
        "fa135d51-6211-45f8-97dd-92d3c0e4d5da": "Is there anything else about your experience you'd like to share?"
    }
    return questions

def show_perfect_transcript():
    """Show the perfect transcript with full questions"""
    print("🎭 PERFECT TRANSCRIPT VIEWER")
    print("=" * 60)
    print("Showing full conversation with readable question text")
    print()
    
    # Get question mapping
    question_map = get_mk_survey_questions()
    print(f"✅ Loaded {len(question_map)} MK Survey questions")
    print()
    
    # Get transcript
    try:
        response = requests.get(f"{BASE_URL}/pg/api/voice/transcript/1772217829012_871", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to get transcript: {response.status_code}")
            return
        
        transcript_data = response.json()
        full_transcript = transcript_data.get("full_transcript", "")
        
        print("📝 COMPLETE CONVERSATION TRANSCRIPT")
        print("=" * 50)
        print(f"Survey ID: {transcript_data.get('survey_id')}")
        print(f"Template: MK Survey")
        print(f"Duration: {transcript_data.get('call_duration_seconds')}s")
        print(f"Status: {transcript_data.get('call_status')}")
        print()
        
        # Process each line
        lines = full_transcript.split('\n')
        question_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a question answer
            if line.startswith('Q[') and ']: ' in line:
                try:
                    qid_end = line.find(']: ')
                    qid = line[2:qid_end]  # Extract question ID
                    answer = line[qid_end + 3:]  # Extract answer
                    
                    # Get actual question text
                    question_text = question_map.get(qid, f"Unknown Question ({qid})")
                    
                    print("❓" + "─" * 58)
                    print(f"❓ Question: {question_text}")
                    print(f"💬 Answer: {answer}")
                    print()
                    question_count += 1
                    
                except Exception as e:
                    print(f"⚠️  Error parsing line: {line}")
                    print(f"   Error: {e}")
                    print()
            else:
                # Skip other lines for cleaner output
                continue
        
        print("❓" + "─" * 58)
        print(f"📊 SUMMARY: {question_count} questions answered")
        print()
        
        # Show detailed breakdown
        print("📋 DETAILED QUESTION & ANSWER BREAKDOWN")
        print("=" * 50)
        
        survey_answers = transcript_data.get("survey_answers", [])
        for i, answer in enumerate(survey_answers, 1):
            qid = answer.get("question_id")
            answer_text = answer.get("answer")
            question_text = question_map.get(qid, f"Unknown Question ({qid})")
            
            print(f"🔹 Question {i}:")
            print(f"   📝 {question_text}")
            print(f"   💬 {answer_text}")
            print()
        
        print("=" * 60)
        print("✅ Perfect transcript completed!")
        print()
        print("🎯 KEY INSIGHTS:")
        print(f"   • Total Questions: {question_count}")
        print(f"   • Call Duration: {transcript_data.get('call_duration_seconds')}s")
        print(f"   • Survey Status: {transcript_data.get('call_status')}")
        print(f"   • Template Used: MK Survey")
        print()
        print("📊 RESPONSE ANALYSIS:")
        
        # Analyze responses
        responses = [answer.get("answer") for answer in survey_answers]
        if responses:
            print(f"   • Average response length: {sum(len(r) for r in responses) / len(responses):.1f} characters")
            print(f"   • Shortest response: {min(responses, key=len)}")
            print(f"   • Longest response: {max(responses, key=len)}")
        
        print()
        print("🎉 TRANSCRIPT SYSTEM: FULLY FUNCTIONAL!")
        
    except Exception as e:
        print(f"❌ Error processing transcript: {e}")

def show_comparison():
    """Show before/after comparison"""
    print("🔄 BEFORE vs AFTER COMPARISON")
    print("=" * 50)
    print()
    
    print("❌ BEFORE (Just IDs):")
    print("   Q[0a4710ab-7bba-4fbe-9cf7-bfb062302dfa]: 3")
    print("   Q[3a548716-76cb-48c8-88a6-8a541ec8459c]: 3")
    print("   Q[fc004f7e-31dc-4ac6-aa0d-3ef1c9ede923]: Extremely likely")
    print()
    
    print("✅ AFTER (Full Questions):")
    print("   ❓ Question: How would you rate your overall experience ?")
    print("   💬 Answer: 3")
    print()
    print("   ❓ Question: How satisfied are you with the timeliness of your rides?")
    print("   💬 Answer: 3")
    print()
    print("   ❓ Question: How likely are you to recommend this service to a friend or family member?")
    print("   💬 Answer: Extremely likely")
    print()

def main():
    """Main function"""
    print("🚀 PERFECT TRANSCRIPT VIEWER")
    print("=" * 50)
    print("Shows the EXACT questions with full readable text")
    print()
    
    # Show comparison
    show_comparison()
    
    # Show perfect transcript
    show_perfect_transcript()

if __name__ == "__main__":
    main()
