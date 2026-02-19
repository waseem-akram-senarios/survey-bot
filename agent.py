"""
Survey Voice Bot - Ride-sharing Customer Feedback Survey
Conducts post-ride surveys with customers via voice calls.
"""

import logging
import os
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    AutoSubscribe,
    function_tool,
    RunContext,
)
from livekit.agents.voice import AgentSession, Agent
from livekit.plugins import deepgram, openai, silero, elevenlabs

logger = logging.getLogger("survey-agent")
logger.setLevel(logging.INFO)

load_dotenv()


# ==================== RIDER DUMMY DATA ====================
# Fictional riders for testing purposes
RIDER_DATA = {
    "1234567890": {
        "first_name": "Jason",
        "last_name": "Smith",
        "phone": "123-456-7890",
        "mobility_needs": "None",
        "user_since": "2024"
    },
    "3216540987": {
        "first_name": "Erika",
        "last_name": "Sampson",
        "phone": "321-654-0987",
        "mobility_needs": "Wheelchair user",
        "user_since": "2021"
    },
    "7894561230": {
        "first_name": "Samantha",
        "last_name": "Ferguson",
        "phone": "789-456-1230",
        "mobility_needs": "Blind",
        "user_since": "2025"
    }
}

# Organization name (can be loaded from env or DB later)
ORGANIZATION_NAME = os.getenv("ORGANIZATION_NAME", "IT Curves")


def get_rider_info(phone_number: str) -> dict:
    """Get rider information from dummy data."""
    # Clean phone number
    clean_phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")[-10:]
    
    if clean_phone in RIDER_DATA:
        return RIDER_DATA[clean_phone]
    
    # Return default if not found
    return {
        "first_name": "Jason",
        "last_name": "Smith",
        "phone": phone_number,
        "mobility_needs": "Unknown",
        "user_since": "2024"
    }


def setup_survey_logging(room_name: str, caller_number: str):
    """Set up a separate log file for this survey call."""
    log_dir = "survey_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caller_clean = caller_number.replace("+", "").replace("-", "")
    log_filename = f"{log_dir}/survey_{timestamp}_{caller_clean}_{room_name}.log"
    
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    log = logging.getLogger("survey-agent")
    log.addHandler(file_handler)
    
    logger.info(f"📝 SURVEY LOG FILE CREATED: {log_filename}")
    return log_filename, file_handler


def cleanup_survey_logging(handler):
    """Remove the survey-specific handler after the call ends."""
    log = logging.getLogger("survey-agent")
    log.removeHandler(handler)
    handler.close()


def save_survey_responses(caller_number: str, responses: dict, call_duration: float):
    """Save survey responses to a JSON file with question tags."""
    os.makedirs("survey_responses", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caller_clean = caller_number.replace("+", "").replace("-", "")
    filename = f"survey_responses/survey_{timestamp}_{caller_clean}.json"
    
    survey_data = {
        "caller_number": caller_number,
        "timestamp": datetime.now().isoformat(),
        "call_duration_seconds": round(call_duration, 2),
        "responses": responses,
        "completed": responses.get("completed", False)
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(survey_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Survey responses saved to: {filename}")
    return filename


async def entrypoint(ctx: JobContext):
    """Main entry point for survey calls."""
    
    # Connect to the room
    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Wait for participant
    participant = await ctx.wait_for_participant()
    logger.info(f"Starting survey for participant {participant.identity}")
    
    # Extract caller number
    caller_number = participant.attributes.get('sip.phoneNumber', 'unknown')
    
    # Set up call logging
    log_filename, log_handler = setup_survey_logging(ctx.room.name, caller_number)
    
    # Track call start time
    call_start_time = datetime.now()
    
    # Get rider information
    rider_info = get_rider_info(caller_number)
    rider_first_name = rider_info["first_name"]
    
    logger.info(f"📋 Rider Info: {rider_first_name} - Phone: {caller_number}")
    
    # Survey responses storage
    survey_responses = {
        "rider_name": rider_first_name,
        "rider_phone": caller_number,
        "name_confirmed": None,
        "availability_status": None,  # available, callback, email, declined
        "callback_time": None,
        "q1_overall_rating": None,  # 1-5 scale
        "q2_would_recommend": None,  # Yes/No
        "q3_timeliness_satisfaction": None,  # Very negative to Very positive
        "q3_followup": None,  # Follow-up based on Q3 answer
        "q4_daily_life_impact": None,  # Open response
        "q5_challenges_faced": None,  # Open response
        "q6_improvements_desired": None,  # Open response
        "q7_additional_comments": None,  # Open response
        "completed": False
    }
    
    # Load survey prompt
    survey_prompt = f"""You are Jane (or John), a friendly and professional survey assistant for {ORGANIZATION_NAME}. 

# ============================================
# CRITICAL: YOU MUST SPEAK FIRST!
# ============================================
When the call connects, immediately start with the greeting below. Do NOT wait for the participant to speak first.

# ============================================
# RIDER INFORMATION (use in conversation):
# ============================================
- Rider First Name: {rider_first_name}
- Organization: {ORGANIZATION_NAME}

# ============================================
# SURVEY FLOW - Follow this EXACT structure:
# ============================================

## STEP 1: GREETING & NAME CONFIRMATION
Immediately say: "Hi, this is Jane with {ORGANIZATION_NAME}. Am I speaking to {rider_first_name}?"

**If they say YES:**
- Use tool: confirm_name_and_availability(confirmed=True)
- Continue to STEP 2

**If they say NO or WRONG NAME:**
- Apologize politely: "I apologize for the inconvenience. Have a great day!"
- Use tool: end_survey(reason="wrong_person")
- End call

## STEP 2: AVAILABILITY CHECK
Say: "Great! Do you have some time to walk through a brief survey?"

**If they say YES (or "Perfect" / "Sure"):**
- Use tool: confirm_name_and_availability(confirmed=True, available=True)
- Move directly to QUESTION 1

**If they say NO or NOT NOW:**
- Ask: "Good to know, can we give you a call back at a later time?"
  
  **If YES to callback:**
  - Ask: "What time works best for you?"
  - Use tool: schedule_callback(callback_time=<their answer>)
  - Say: "Fantastic, we will follow up with you then. Thank you for your time!"
  - Use tool: end_survey(reason="callback_scheduled")
  
  **If NO to callback:**
  - Ask: "Can we email or text you the survey to fill out at your convenience?"
    
    **If YES to email:**
    - Use tool: offer_alternative_survey(method="email_text")
    - Say: "Great! We will send you the link. Thank you for your time and have a good rest of your day."
    - Use tool: end_survey(reason="email_requested")
    
    **If NO to email:**
    - Say: "No problem! Have a great day."
    - Use tool: end_survey(reason="declined")

## QUESTION 1: Overall Experience Rating (1-5 Scale)
Ask: "How would you rate your overall experience with {ORGANIZATION_NAME}?"

**Expected Response:** Number from 1 to 5 (or variations like "I'd give it a 4", "five stars")
**Use tool:** store_q1_rating(rating=<1-5>)
**After storing:** Acknowledge with "Thank you!" and move to Question 2

## QUESTION 2: Would You Recommend? (Yes/No)
Ask: "Would you recommend our services to someone you know?"

**Expected Response:** Yes or No (or variations)
**Use tool:** store_q2_recommendation(would_recommend=<True/False>)
**After storing:** Acknowledge and move to Question 3

## QUESTION 3: Timeliness Satisfaction (Range Scale)
Ask: "How satisfied are you with the timeliness of the service?"

**Expected Response:** Range from "Very negative" to "Very positive" (or numerical scale 1-5, or descriptive like "pretty good")
**Use tool:** store_q3_timeliness(satisfaction_level="<their answer>")

**CRITICAL - FOLLOW-UP BASED ON ANSWER:**
- If answer is NEGATIVE (1-2, "negative", "poor", "disappointed"): 
  Ask: "I'm sorry to hear that. Can you tell me more about what happened with the timing?"
- If answer is POSITIVE (4-5, "positive", "excellent", "great"):
  Ask: "That's wonderful to hear! What specifically worked well for you timing-wise?"
- If answer is NEUTRAL (3, "okay", "average"):
  Ask: "What could we do better to improve the timeliness?"

**Use tool:** store_q3_followup(followup_answer="<their detailed response>")
**After storing:** Acknowledge and move to Question 4

## QUESTION 4: Impact on Daily Life (Open Response)
Ask: "How has {ORGANIZATION_NAME} impacted your daily life or routine?"

**Expected Response:** Open-ended detailed answer
**Use tool:** store_q4_daily_impact(impact="<their answer>")
**After storing:** Acknowledge with "Thank you for sharing that" and move to Question 5

## QUESTION 5: Challenges Faced (Open Response)
Ask: "What challenges, if any, have you faced while using the service?"

**Expected Response:** Open-ended (they might say "none" or describe issues)
**Use tool:** store_q5_challenges(challenges="<their answer>")
**After storing:** Acknowledge and move to Question 6

## QUESTION 6: Desired Improvements (Open Response)
Ask: "What specific improvements would you like to see in the service?"

**Expected Response:** Open-ended suggestions
**Use tool:** store_q6_improvements(improvements="<their answer>")
**After storing:** Acknowledge and move to Question 7

## QUESTION 7: FINAL - Additional Comments (Open Response)
Ask: "Thank you for your input. Is there anything else about your experience that we didn't ask about but you'd like to mention?"

**Expected Response:** Open-ended or "No, that's all"
**Use tool:** store_q7_additional(additional_comments="<their answer or 'None'>")

## STEP 3: CONCLUDING STATEMENT
After Question 7, immediately say: 
"Thanks so much for sharing your thoughts, {rider_first_name}. I really appreciate your time, and I hope you have a great rest of your day."

**Use tool:** complete_survey()

# ============================================
# IMPORTANT INSTRUCTIONS:
# ============================================
1. **SPEAK FIRST** - Start with the greeting immediately when call connects
2. **Follow the EXACT flow** - Don't skip steps or reorder questions
3. **Use ALL the provided tools** - Call the appropriate tool after each response
4. **Be natural and conversational** - Don't sound robotic
5. **Handle interruptions gracefully** - If they want to end early, be polite
6. **ONE QUESTION AT A TIME** - Wait for response before moving to next
7. **Acknowledge every answer** - Say "Thank you", "I appreciate that", "Got it", etc.
8. **Use the rider's name** - Use "{rider_first_name}" in the greeting and conclusion

Current time: {datetime.now().strftime('%I:%M %p')}
"""
    
    # Create survey agent class with tools
    class SurveyAgent(Agent):
        """Agent that conducts customer surveys with function tools."""
        
        async def on_enter(self):
            """Called when agent enters - AI speaks first."""
            # With Realtime Model, use generate_reply to initiate conversation
            await self.session.generate_reply(
                instructions=f"Immediately greet the participant with: 'Hi, this is Jane with {ORGANIZATION_NAME}. Am I speaking to {rider_first_name}?' Wait for their response."
            )
        
        @function_tool()
        async def confirm_name_and_availability(
            self, 
            context: RunContext, 
            confirmed: bool, 
            available: bool = None
        ):
            """
            Confirm rider's name and check availability for survey.
            
            Args:
                confirmed: True if name is confirmed, False if wrong person
                available: True if available now, False if not available (only needed if confirmed=True)
            """
            if not confirmed:
                survey_responses["name_confirmed"] = False
                logger.info("❌ Name not confirmed - ending survey")
                return "Name not confirmed. End the call politely."
            
            survey_responses["name_confirmed"] = True
            logger.info(f"✅ Name confirmed: {rider_first_name}")
            
            if available is not None:
                survey_responses["availability_status"] = "available" if available else "not_available"
                logger.info(f"✅ Availability: {'Available' if available else 'Not available'}")
                if available:
                    return "Great! Now proceed to Question 1: Ask about their overall experience rating."
                else:
                    return "Not available now. Ask about callback or alternative survey method."
            
            return "Name confirmed. Now ask about availability for the survey."
        
        @function_tool()
        async def schedule_callback(self, context: RunContext, callback_time: str):
            """
            Schedule a callback time for the survey.
            
            Args:
                callback_time: The time/date when user wants callback
            """
            survey_responses["availability_status"] = "callback"
            survey_responses["callback_time"] = callback_time
            logger.info(f"📅 Callback scheduled for: {callback_time}")
            return "Callback scheduled. Now say: 'Fantastic, we will follow up with you then. Thank you for your time!' Then use end_survey tool with reason='callback_scheduled'."
        
        @function_tool()
        async def offer_alternative_survey(self, context: RunContext, method: str):
            """
            User prefers email/text survey instead of phone.
            
            Args:
                method: "email_text" for alternative delivery method
            """
            survey_responses["availability_status"] = "email_requested"
            logger.info(f"📧 Alternative survey method requested: {method}")
            return "Email method accepted. Now say: 'Great! We will send you the link. Thank you for your time and have a good rest of your day.' Then use end_survey tool with reason='email_requested'."
        
        @function_tool()
        async def store_q1_rating(self, context: RunContext, rating: int):
            """
            Store overall experience rating (Question 1).
            
            Args:
                rating: Rating from 1 to 5 (1=very poor, 5=excellent)
            """
            if 1 <= rating <= 5:
                survey_responses["q1_overall_rating"] = rating
                logger.info(f"✅ Q1 - Overall Rating: {rating}/5")
                return "Rating recorded. Acknowledge with 'Thank you!' and proceed to Question 2: Would you recommend our services to someone you know?"
            else:
                return "Invalid rating. Ask them to provide a rating between 1 and 5."
        
        @function_tool()
        async def store_q2_recommendation(self, context: RunContext, would_recommend: bool):
            """
            Store recommendation response (Question 2).
            
            Args:
                would_recommend: True if would recommend, False otherwise
            """
            survey_responses["q2_would_recommend"] = "Yes" if would_recommend else "No"
            logger.info(f"✅ Q2 - Would Recommend: {survey_responses['q2_would_recommend']}")
            return "Recommendation recorded. Acknowledge and proceed to Question 3: How satisfied are you with the timeliness of the service?"
        
        @function_tool()
        async def store_q3_timeliness(self, context: RunContext, satisfaction_level: str):
            """
            Store timeliness satisfaction (Question 3).
            
            Args:
                satisfaction_level: Range from "Very negative" to "Very positive" or numeric/descriptive
            """
            survey_responses["q3_timeliness_satisfaction"] = satisfaction_level
            logger.info(f"✅ Q3 - Timeliness Satisfaction: {satisfaction_level}")
            
            # Determine sentiment for follow-up
            level_lower = satisfaction_level.lower()
            if any(word in level_lower for word in ["negative", "poor", "disappointed", "bad"]) or (satisfaction_level.isdigit() and int(satisfaction_level) <= 2):
                return "Timeliness recorded as NEGATIVE. Ask follow-up: 'I'm sorry to hear that. Can you tell me more about what happened with the timing?'"
            elif any(word in level_lower for word in ["positive", "excellent", "great", "wonderful"]) or (satisfaction_level.isdigit() and int(satisfaction_level) >= 4):
                return "Timeliness recorded as POSITIVE. Ask follow-up: 'That's wonderful to hear! What specifically worked well for you timing-wise?'"
            else:
                return "Timeliness recorded as NEUTRAL. Ask follow-up: 'What could we do better to improve the timeliness?'"
        
        @function_tool()
        async def store_q3_followup(self, context: RunContext, followup_answer: str):
            """
            Store follow-up answer for Question 3 (based on their satisfaction level).
            
            Args:
                followup_answer: Detailed response about timing experience
            """
            survey_responses["q3_followup"] = followup_answer
            logger.info(f"✅ Q3 Follow-up: {followup_answer[:100]}...")
            return "Follow-up recorded. Acknowledge with 'Thank you for sharing that' and proceed to Question 4: How has RideShare Connect impacted your daily life or routine?"
        
        @function_tool()
        async def store_q4_daily_impact(self, context: RunContext, impact: str):
            """
            Store how service impacted daily life (Question 4).
            
            Args:
                impact: Open-ended response about daily life impact
            """
            survey_responses["q4_daily_life_impact"] = impact
            logger.info(f"✅ Q4 - Daily Impact: {impact[:100]}...")
            return "Daily impact recorded. Acknowledge and proceed to Question 5: What challenges, if any, have you faced while using the service?"
        
        @function_tool()
        async def store_q5_challenges(self, context: RunContext, challenges: str):
            """
            Store challenges faced while using service (Question 5).
            
            Args:
                challenges: Open-ended response about challenges (or "None")
            """
            survey_responses["q5_challenges_faced"] = challenges
            logger.info(f"✅ Q5 - Challenges: {challenges[:100]}...")
            return "Challenges recorded. Acknowledge and proceed to Question 6: What specific improvements would you like to see in the service?"
        
        @function_tool()
        async def store_q6_improvements(self, context: RunContext, improvements: str):
            """
            Store desired improvements (Question 6).
            
            Args:
                improvements: Open-ended suggestions for improvement
            """
            survey_responses["q6_improvements_desired"] = improvements
            logger.info(f"✅ Q6 - Improvements: {improvements[:100]}...")
            return "Improvements recorded. Acknowledge and proceed to Question 7 (FINAL): Thank you for your input. Is there anything else about your experience that we didn't ask about but you'd like to mention?"
        
        @function_tool()
        async def store_q7_additional(self, context: RunContext, additional_comments: str):
            """
            Store any additional comments (Question 7 - Final question).
            
            Args:
                additional_comments: Any additional feedback or "None"
            """
            survey_responses["q7_additional_comments"] = additional_comments
            logger.info(f"✅ Q7 - Additional: {additional_comments[:100]}...")
            return "Final answer recorded. Now give the concluding statement and use the complete_survey tool."
        
        @function_tool()
        async def complete_survey(self, context: RunContext):
            """
            Mark survey as completed and prepare to end call.
            Called after concluding statement.
            """
            survey_responses["completed"] = True
            logger.info("✅ Survey completed successfully!")
            
            # Calculate call duration
            call_duration = (datetime.now() - call_start_time).total_seconds()
            
            # Save responses
            save_survey_responses(caller_number, survey_responses, call_duration)
            
            # Cleanup logging
            cleanup_survey_logging(log_handler)
            
            return "Survey completed and saved. The call will end naturally now. Wait for participant to hang up or conversation to end."
        
        @function_tool()
        async def end_survey(self, context: RunContext, reason: str = "completed"):
            """
            End the survey call immediately.
            
            Args:
                reason: Reason for ending (wrong_person, declined, callback_scheduled, email_requested, completed)
            """
            logger.info(f"📞 Survey ending: {reason}")
            
            survey_responses["availability_status"] = reason
            
            # Calculate call duration
            call_duration = (datetime.now() - call_start_time).total_seconds()
            
            # Save responses if any were collected
            if any(v is not None for k, v in survey_responses.items() if k not in ["completed", "rider_name", "rider_phone"]):
                save_survey_responses(caller_number, survey_responses, call_duration)
            
            # Cleanup logging
            cleanup_survey_logging(log_handler)
            
            # Disconnect will happen automatically when agent ends
            return "Survey ended. The call will disconnect automatically."
    
    # Create the agent instance
    survey_agent = SurveyAgent(
        instructions=survey_prompt
    )
    
    # Create session with survey tools
    # Use OpenAI Realtime Model (has built-in STT and TTS)
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="ash",  # ash, ballad, coral, sage, verse
            temperature=0.7,
        ),
        vad=silero.VAD.load(),  # Still use VAD for turn detection
    )
    
    # Start the session with the agent
    await session.start(room=ctx.room, agent=survey_agent)
    
    # Connect to the room (this binds the room after session startup)
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            initialize_process_timeout=120.0,
            # port="8083",
            # agent_name="survey-agent",
            job_memory_warn_mb=1000,
            job_memory_limit_mb=1500,
        ),
    )

