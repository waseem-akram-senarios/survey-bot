"""
LiveKit Survey Agent

A voice AI agent that conducts phone surveys using LiveKit's Agents Framework.
Runs as a standalone worker process alongside the FastAPI backend.
Uses STT (Deepgram) -> LLM (OpenAI) -> TTS (OpenAI) pipeline.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

import requests
from dotenv import load_dotenv
from livekit import api, rtc
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
    get_job_context,
    RoomInputOptions,
)
from livekit.plugins import deepgram, openai, silero

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("livekit-survey-agent")
logger.setLevel(logging.INFO)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8081/pg")
outbound_trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID", "")


def fetch_survey_data(survey_id: str) -> dict | None:
    """Fetch survey questions from the backend API."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/surveys/{survey_id}/questions")
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"Failed to fetch survey data: {resp.status_code} {resp.text}")
        return None
    except Exception as e:
        logger.error(f"Error fetching survey data: {e}")
        return None


def fetch_survey_recipient(survey_id: str) -> dict | None:
    """Fetch recipient info from the backend."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/surveys/{survey_id}/recipient_info")
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"Failed to fetch recipient: {resp.status_code}")
        return None
    except Exception as e:
        logger.error(f"Error fetching recipient: {e}")
        return None


def submit_survey_answers(survey_id: str, answers: dict) -> bool:
    """Submit collected answers back to the backend."""
    try:
        payload = {"SurveyId": survey_id, **answers}
        resp = requests.post(
            f"{BACKEND_URL}/api/surveys/{survey_id}/update_survey_qna_phone",
            json=payload,
        )
        logger.info(f"Submitted answers for {survey_id}: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Error submitting answers: {e}")
        return False


class SurveyAgent(Agent):
    """Voice AI agent that conducts a survey over the phone."""

    def __init__(
        self,
        *,
        survey_id: str,
        questions: list[dict],
        recipient_name: str,
        ride_id: str,
        survey_name: str,
    ):
        self.survey_id = survey_id
        self.questions = questions
        self.recipient_name = recipient_name
        self.ride_id = ride_id
        self.survey_name = survey_name
        self.current_question_idx = 0
        self.answers: dict[str, str] = {}
        self.declined = False
        self.participant: rtc.RemoteParticipant | None = None

        # Build the system instructions with all questions embedded
        instructions = self._build_instructions()
        super().__init__(instructions=instructions)

    def _build_instructions(self) -> str:
        """Build the agent's system prompt with survey context."""

        questions_text = ""
        for i, q in enumerate(self.questions, 1):
            q_text = q.get("question_text", q.get("text", ""))
            criteria = q.get("criteria", "open")
            categories = q.get("categories", [])
            scales = q.get("scale", q.get("scales"))

            questions_text += f"\nQuestion {i} (ID: {q.get('id', '')}):\n"
            questions_text += f"  Text: {q_text}\n"
            questions_text += f"  Type: {criteria}\n"

            if criteria == "categorical" and categories:
                questions_text += f"  Categories: {', '.join(categories)}\n"
            elif criteria == "scale" and scales:
                questions_text += f"  Scale: 1 to {scales}\n"

        return f"""You are an intelligent, conversational AI survey conductor with a warm, friendly personality.

You're calling {self.recipient_name} to have a natural conversation about their experience with {self.survey_name}.
Survey ID: {self.survey_id}, Ride ID: {self.ride_id}.

YOUR PERSONALITY:
- Conversational and friendly, not robotic
- Adaptive - change questions based on responses
- Empathetic - understand emotions and context
- Intelligent - ask follow-up questions that matter
- Natural - use everyday language, not survey jargon
- Flexible - skip irrelevant questions, explore interesting topics

CONVERSATION APPROACH:
- Start with a warm, personal greeting
- Ask questions naturally based on context
- Listen to emotions and respond appropriately
- Explore interesting topics that arise
- Reference previous answers naturally
- End when conversation feels complete naturally

SURVEY QUESTIONS TO COVER (ask naturally, not in order):
{questions_text}

INTELLIGENT QUESTIONING EXAMPLES:
- Instead of: "Rate your satisfaction 1-5"
- Use: "How did you feel about the whole experience?"

- Instead of: "Was it easy to use?"
- Use: "How smooth was everything for you?"

- Instead of: "Any additional comments?"
- Use: "Is there anything else you'd like to share about your experience?"

ADAPTIVE BEHAVIOR:
- If they're enthusiastic: explore what they loved
- If they're frustrated: understand what went wrong
- If they mention specific people: ask about those interactions
- If they mention timing: explore scheduling or pacing issues
- If they seem rushed: be brief and respectful

EMOTIONAL INTELLIGENCE:
- Detect emotions in voice and words
- Respond with empathy: "That sounds frustrating" or "That must have been exciting!"
- Validate their feelings appropriately
- Adjust your tone based on their emotional state

CONVERSATION FLOW:
1. Warm greeting: "Hi {self.recipient_name}! I'm here to chat about your experience. I'm genuinely interested in hearing how things went for you. Do you have a few minutes to share your story?"
2. If they agree: "Great! I'd love to hear about your experience with {self.survey_name}. Let's start with how you're feeling about it overall."
3. Ask questions naturally based on their responses
4. Explore interesting topics that come up
5. Show you're listening by referencing their answers
6. End naturally when conversation feels complete

IMPORTANT RULES:
- Have a genuine conversation, don't conduct an interview
- Ask one question at a time and really listen to the answer
- Be curious and responsive to what they share
- If they want to end the call, respect their wish
- Use record_answer to save important information
- End warmly: "Thank you so much for sharing your experience with me!"

Remember: You're having a conversation, not collecting data. Show you care about their experience and feelings."""

    def set_participant(self, participant: rtc.RemoteParticipant):
        self.participant = participant

    async def hangup(self):
        """Hang up the call by deleting the room."""
        job_ctx = get_job_context()
        await job_ctx.api.room.delete_room(
            api.DeleteRoomRequest(room=job_ctx.room.name)
        )

    @function_tool()
    async def record_answer(
        self,
        ctx: RunContext,
        question_id: str,
        answer: str,
    ):
        """Record the user's answer to a survey question.

        Args:
            question_id: The ID of the question being answered
            answer: The user's answer (category name, rating number, or free text)
        """
        self.answers[question_id] = answer
        logger.info(f"Recorded answer for {question_id}: {answer}")
        return f"Answer recorded for question {question_id}. Proceed to the next question."

    @function_tool()
    async def submit_and_end(self, ctx: RunContext):
        """Submit all collected survey answers and end the call. Call this after the last question."""
        logger.info(f"Submitting {len(self.answers)} answers for survey {self.survey_id}")

        submit_survey_answers(self.survey_id, self.answers)

        # Update survey call info
        try:
            job_ctx = get_job_context()
            room_name = job_ctx.room.name
            requests.patch(
                f"{BACKEND_URL}/api/surveys/{self.survey_id}/status",
                json={"Status": "Completed"},
            )
        except Exception as e:
            logger.error(f"Error updating survey status: {e}")

        current_speech = ctx.session.current_speech
        if current_speech:
            await current_speech.wait_for_playout()

        await self.hangup()
        return "Survey submitted and call ended."

    @function_tool()
    async def end_call(self, ctx: RunContext):
        """End the call when the user declines or wants to stop."""
        logger.info(f"Ending call for survey {self.survey_id}")

        current_speech = ctx.session.current_speech
        if current_speech:
            await current_speech.wait_for_playout()

        await self.hangup()
        return "Call ended."

    @function_tool()
    async def detected_answering_machine(self, ctx: RunContext):
        """Called when the call reaches voicemail. Use this after you hear the voicemail greeting."""
        logger.info(f"Voicemail detected for survey {self.survey_id}")
        await self.hangup()
        return "Voicemail detected, call ended."


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the LiveKit agent worker."""
    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect()

    # Parse metadata passed when dispatching the agent
    metadata = json.loads(ctx.job.metadata)
    phone_number = metadata["phone_number"]
    survey_id = metadata["survey_id"]
    participant_identity = f"sip_{phone_number}"

    logger.info(f"Starting survey call: survey={survey_id}, phone={phone_number}")

    # Fetch survey data from backend
    survey_data = fetch_survey_data(survey_id)
    if not survey_data:
        logger.error(f"Could not fetch survey data for {survey_id}")
        ctx.shutdown()
        return

    # Fetch recipient info
    recipient_info = fetch_survey_recipient(survey_id)
    recipient_name = recipient_info.get("Recipient", "Customer") if recipient_info else "Customer"
    ride_id = recipient_info.get("RideID", "N/A") if recipient_info else "N/A"
    survey_name = recipient_info.get("Name", "Survey") if recipient_info else "Survey"

    questions = survey_data.get("Questions", [])
    if not questions:
        logger.error(f"No questions found for survey {survey_id}")
        ctx.shutdown()
        return

    # Create the survey agent
    agent = SurveyAgent(
        survey_id=survey_id,
        questions=questions,
        recipient_name=recipient_name,
        ride_id=ride_id,
        survey_name=survey_name,
    )

    # Create the voice pipeline session
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        tts=openai.TTS(voice="nova"),
        llm=openai.LLM(model="gpt-4o"),
    )

    # Start the agent session before dialing
    session_started = asyncio.create_task(
        session.start(
            agent=agent,
            room=ctx.room,
        )
    )

    # Dial the phone number via SIP
    try:
        sip_participant = await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=outbound_trunk_id,
                sip_call_to=phone_number,
                participant_identity=participant_identity,
                participant_name=recipient_name,
                krisp_enabled=True,
                wait_until_answered=True,
            )
        )

        # Wait for session start and participant join
        await session_started
        participant = await ctx.wait_for_participant(identity=participant_identity)
        logger.info(f"Participant joined: {participant.identity}")
        agent.set_participant(participant)

        # Store the LiveKit room name as the call_id in the database
        try:
            from utils import sql_execute
            sql_execute(
                "UPDATE surveys SET call_id = :call_id WHERE id = :survey_id",
                {"call_id": ctx.room.name, "survey_id": survey_id},
            )
            logger.info(f"Stored room name {ctx.room.name} as call_id for survey {survey_id}")
        except Exception as e:
            logger.warning(f"Could not update call_id: {e}")

    except Exception as e:
        logger.error(
            f"Error creating SIP participant: {e}"
        )
        ctx.shutdown()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="survey-caller",
        )
    )
