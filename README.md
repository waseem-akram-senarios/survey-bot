# Survey Voice Bot - Ride-sharing Feedback

A voice-based survey bot for conducting post-ride customer feedback surveys using LiveKit.

## Features

- **3-Question Survey Flow**:
  1. Rating question (1-5 scale)
  2. Multiple choice question (A/B/C/D options)
  3. Open flow question with branching logic (Yes/No → Follow-up)

- **Intelligent Response Mapping**: LLM automatically maps natural language responses to correct options
- **Availability Check**: Asks if customer is available before starting survey
- **Graceful Conclusion**: Thanks customer and ends call politely
- **Response Storage**: Saves all responses to JSON files with question tags
- **Call Logging**: Detailed logs for each survey call

## Project Structure

```
survey_bot/
├── agent.py              # Main survey agent
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your actual environment variables (create this)
├── survey_logs/         # Call logs (auto-created)
└── survey_responses/    # Survey responses (auto-created)
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd survey_bot
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
nano .env  # or use any text editor
```

**Required API Keys:**
- **LiveKit**: Get from your LiveKit Cloud dashboard or self-hosted server
- **Deepgram**: Sign up at https://deepgram.com (STT)
- **OpenAI**: Get from https://platform.openai.com (LLM)
- **ElevenLabs**: Get from https://elevenlabs.io (TTS)

### 4. Run the Agent

```bash
python agent.py start
```

The agent will start on **port 8083** and wait for incoming survey calls.

## Survey Questions

### Question 1: Rating (1-5)
"On a scale of 1 to 5, where 1 is very poor and 5 is excellent, how would you rate your overall ride experience today?"

**Accepted Responses:**
- "5"
- "I'd give it a 4"
- "Three out of five"
- "Five stars"

### Question 2: Multiple Choice (A/B/C/D)
"What was the primary reason for choosing our service today?"
- A) Competitive pricing
- B) Convenience and ease of booking
- C) Driver ratings and reviews
- D) Vehicle availability

**Accepted Responses:**
- "A"
- "Option B"
- "I chose it because of the price" → Maps to A
- "Convenience" → Maps to B

### Question 3: Open Flow (Branching)
"Would you recommend our service to friends or family?"

**If YES:**
- Follow-up: "That's wonderful! What did you like most about your experience?"

**If NO:**
- Follow-up: "We appreciate your honesty. What could we improve to serve you better?"

## Response Storage

Survey responses are saved to `survey_responses/` as JSON files:

```json
{
  "caller_number": "+1234567890",
  "timestamp": "2026-02-17T14:30:45",
  "call_duration_seconds": 125.5,
  "responses": {
    "q1_rating": 5,
    "q2_mcq": "B",
    "q3_recommend": "Yes",
    "q3_followup": "The driver was very professional and the app was easy to use",
    "completed": true
  }
}
```

## Call Logs

Detailed logs for each call are saved to `survey_logs/`:

```
survey_logs/survey_20260217_143045_1234567890_room-abc123.log
```

## Port Configuration

The survey bot runs on **port 8083** by default. If you need to change it:

1. Edit `agent.py` line with `port="8083"` 
2. Update your LiveKit server configuration to route survey calls to this port

## Testing the Bot

1. Make sure the agent is running (`python agent.py start`)
2. Configure your LiveKit server to route calls to this agent
3. Make a test call through your SIP provider or LiveKit room
4. The bot will:
   - Greet the caller
   - Ask about availability
   - Conduct the 3-question survey
   - Save responses to file
   - End call gracefully

## Customizing Questions

To modify the survey questions, edit the `survey_prompt` variable in `agent.py` (around line 150).

You can also:
- Change the number of questions
- Modify branching logic
- Add more MCQ options
- Adjust the LLM temperature for more/less creative responses

## Troubleshooting

**Agent won't start:**
- Check that all API keys are set in `.env`
- Verify port 8083 is not already in use
- Check logs for error messages

**No audio/responses:**
- Verify STT (Deepgram) API key is valid
- Check TTS (ElevenLabs) API key
- Ensure participant is connected to the room

**Responses not saved:**
- Check `survey_responses/` directory permissions
- Verify disk space is available
- Check logs for save errors

## Future Enhancements

- [ ] Fetch questions from database
- [ ] Multi-language support
- [ ] Database integration for response storage
- [ ] Analytics dashboard
- [ ] SMS/Email survey summaries
- [ ] Scheduling follow-up surveys

## Support

For issues or questions, check the logs in `survey_logs/` for detailed error information.

