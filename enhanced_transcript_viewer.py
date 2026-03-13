#!/usr/bin/env python3
"""
Enhanced Transcript Viewer
Shows full conversation with actual question text instead of IDs
"""

import requests
import json

BASE_URL = "http://54.86.65.150:8080"

def get_question_mapping():
    """Get mapping of question IDs to actual question text"""
    try:
        response = requests.get(f"{BASE_URL}/pg/api/templates/getquestions", 
                              headers={'Content-Type': 'application/json'},
                              json={"TemplateName": "Trip Complete Survey"}, 
                              timeout=10)
        if response.status_code == 200:
            data = response.json()
            questions = data.get("Questions", [])
            return {q.get("id"): q.get("text") for q in questions}
        else:
            print(f"❌ Failed to get questions: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Error getting questions: {e}")
        return {}

def enhance_transcript(survey_id):
    """Get transcript with actual question text"""
    print(f"🎭 Enhanced Transcript Viewer for Survey: {survey_id}")
    print("=" * 60)
    
    # Get question mapping
    question_map = get_question_mapping()
    print(f"✅ Loaded {len(question_map)} question mappings")
    
    # Get transcript
    try:
        response = requests.get(f"{BASE_URL}/pg/api/voice/transcript/{survey_id}", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to get transcript: {response.status_code}")
            return
        
        transcript_data = response.json()
        full_transcript = transcript_data.get("full_transcript", "")
        
        print(f"\n📝 Enhanced Conversation Transcript:")
        print("=" * 40)
        print(f"Survey ID: {transcript_data.get('survey_id')}")
        print(f"Duration: {transcript_data.get('call_duration_seconds')}s")
        print(f"Status: {transcript_data.get('call_status')}")
        print()
        
        # Process each line
        lines = full_transcript.split('\n')
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
                    
                    print(f"❓ Question: {question_text}")
                    print(f"💬 Answer: {answer}")
                    print()
                    
                except Exception as e:
                    print(f"⚠️  Error parsing line: {line}")
                    print(f"   Error: {e}")
                    print()
            else:
                # Regular conversation line
                if line.startswith('[') and ('AGENT:' in line or 'CALLER:' in line):
                    print(f"💭 {line}")
                elif line and not line.startswith('---'):
                    print(f"📄 {line}")
        
        # Show survey answers summary
        print("=" * 40)
        print("📊 Survey Answers Summary:")
        
        survey_answers = transcript_data.get("survey_answers", [])
        for i, answer in enumerate(survey_answers, 1):
            qid = answer.get("question_id")
            answer_text = answer.get("answer")
            question_text = question_map.get(qid, f"Unknown Question ({qid})")
            
            print(f"  {i}. {question_text}")
            print(f"     💬 {answer_text}")
            print()
        
        print("=" * 60)
        print("✅ Enhanced transcript completed!")
        
    except Exception as e:
        print(f"❌ Error processing transcript: {e}")

def show_sample_conversation():
    """Show a sample of what the enhanced transcript looks like"""
    print("🎭 SAMPLE ENHANCED TRANSCRIPT")
    print("=" * 50)
    print("This is what your transcripts will look like with full questions:")
    print()
    
    sample = """
💭 [14:30:15.123] AGENT: Hello! This is your AI survey assistant. I'm calling to ask you a few questions about your recent trip experience.

💭 [14:30:18.456] CALLER: Hi! Yes, I can talk for a few minutes. What's this about?

💭 [14:30:20.789] AGENT: Great! I'm conducting a brief survey about your transportation experience. This will take about 2-3 minutes.

💭 [14:30:23.123] CALLER: Sure, that sounds fine. Let's do it.

❓ Question: How did your trip go today? Tell me about your experience.
💬 Answer: 4

❓ Question: How was the timing of your pickup? Did the vehicle arrive when you expected?
💬 Answer: Actually, they were about 5 minutes early, which was great.

❓ Question: Tell me about your driver today. How was your interaction with them?
💬 Answer: The driver was very professional. Friendly, helped with my bags, and knew the route perfectly.

❓ Question: What did you think of the vehicle? Was it comfortable for your trip?
💬 Answer: Very comfortable. Clean, good temperature, and plenty of space.

❓ Question: How did you feel during the ride? Did you feel safe and comfortable throughout?
💬 Answer: Yes, I felt completely safe. The driver was careful and followed all traffic rules.

❓ Question: How was the process of booking your trip? Was there anything confusing or difficult?
💬 Answer: No, the app was very easy to use. Straightforward booking process.

❓ Question: Would you tell a friend or family member about our service? Why or why not?
💬 Answer: Absolutely! I've already told a few coworkers about it. It's reliable and affordable.

💭 [14:31:17.789] AGENT: Perfect! Thank you so much for your time and valuable feedback. We really appreciate it!

💭 [14:31:20.123] CALLER: You're welcome! Have a great day!
"""
    
    print(sample)

def main():
    """Main function"""
    print("🚀 ENHANCED TRANSCRIPT VIEWER")
    print("=" * 50)
    print("Shows full conversation with readable question text")
    print()
    
    # Show sample first
    show_sample_conversation()
    
    print("\n" + "=" * 50)
    print("🎯 Now viewing actual transcript data:")
    print()
    
    # View actual transcript
    enhance_transcript("1772217829012_871")

if __name__ == "__main__":
    main()
