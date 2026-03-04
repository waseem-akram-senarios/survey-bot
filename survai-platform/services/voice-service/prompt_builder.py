"""
Survey System Prompt Builder for Voice Service.

Two focused prompts are built here:
  - build_greeter_prompt()   — ~300 tokens, identity + availability only
  - build_questions_prompt() — ~900 tokens, questions + recording intelligence

build_survey_prompt() is kept as a backward-compatible alias (returns joined text).
"""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_LANGUAGE_PREFERENCE_QUESTION = (
    "What language would you like to complete the survey in? "
    "To continue in English, please say English. "
    "¿En qué idioma le gustaría completar la encuesta? "
    "Para continuar en español, por favor diga español."
)


async def _translate_questions_to_es(questions: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Batch-translate all question texts to Spanish using OpenAI.
    Returns a dict mapping question_id -> Spanish text.
    Falls back gracefully to empty dict on any error.
    """
    if not questions:
        return {}

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set — bilingual questions will use English only")
        return {}

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)

        numbered_lines = "\n".join(
            f"{i+1}. [{q.get('id', f'q{i+1}')}] {q.get('text', '')}"
            for i, q in enumerate(questions)
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator. Translate the following survey questions "
                        "from English to Spanish. Keep the numbering and [id] prefix exactly as-is. "
                        "Return ONLY the translated lines, one per line, in the same format."
                    ),
                },
                {"role": "user", "content": numbered_lines},
            ],
        )

        translated_lines = response.choices[0].message.content.strip().split("\n")
        result: Dict[str, str] = {}
        for i, (q, line) in enumerate(zip(questions, translated_lines)):
            qid = q.get("id", f"q{i+1}")
            # Strip leading "1. [id] " prefix from the translation
            text = line.strip()
            bracket_end = text.find("] ")
            if bracket_end != -1:
                text = text[bracket_end + 2:]
            elif ". " in text:
                text = text.split(". ", 1)[-1]
            result[qid] = text

        logger.info(f"Translated {len(result)} questions to Spanish")
        return result

    except Exception as e:
        logger.warning(f"Question translation to Spanish failed: {e} — using English only")
        return {}


def _format_question(order: int, q: Dict[str, Any], es_text: Optional[str] = None) -> str:
    """Format a single question block for the agent prompt."""
    qid = q.get("id", f"q{order}")
    text = q.get("text", "")
    criteria = q.get("criteria", "open")
    categories = q.get("categories", [])
    scale_max = q.get("scales") or 5
    parent_id = q.get("parent_id")
    parent_order = q.get("_parent_order", "")
    trigger_cats = q.get("parent_category_texts", [])

    # Build the question text line(s) — bilingual if es_text is provided
    if es_text:
        question_text = f'[EN] "{text}" / [ES] "{es_text}"'
        ask_instruction = "Ask in the recipient's chosen language (set via set_language). If they switch language, call set_language() then re-ask this question in the new language."
    else:
        question_text = f'"{text}"'
        ask_instruction = ""

    ask_suffix = f"\n  {ask_instruction}" if ask_instruction else ""

    if parent_id:
        trigger_str = ", ".join(trigger_cats) if trigger_cats else "any answer"
        return (
            f"Q{order} [{qid}] CONDITIONAL (ask ONLY IF the answer to Q{parent_order} "
            f"includes: {trigger_str}): {question_text}\n"
            f"  Skip entirely if the condition is not met.{ask_suffix}"
        )
    elif criteria == "scale":
        return (
            f"Q{order} [{qid}] SCALE 1-{scale_max} (1=very poor, {scale_max}=excellent): {question_text}\n"
            f"  Ask it word-for-word. Always tell the caller: '1 is very poor, {scale_max} is excellent.'\n"
            f"  If they give a word instead of a number, ask once: \"If you had to put a number on it, 1 to {scale_max}?\"\n"
            f"  After recording their answer: give ONE brief acknowledgment sentence, then move to the next question.\n"
            f"  Do NOT ask a follow-up or probe in the same response as the acknowledgment.{ask_suffix}"
        )
    elif criteria == "categorical":
        cats_str = ", ".join(categories) if categories else "open"
        return (
            f"Q{order} [{qid}] CHOICE [{cats_str}]: {question_text}\n"
            f"  Let them answer freely. Only list the options if they seem stuck.\n"
            f"  Negative choice: empathize and ask ONE follow-up.\n"
            f"  Positive choice: celebrate briefly and move on.{ask_suffix}"
        )
    else:
        return (
            f"Q{order} [{qid}] OPEN: {question_text}\n"
            f"  If vague (\"fine\", \"okay\", \"good\") — probe gently with ONE clarifying question.\n"
            f"  If detailed — acknowledge warmly and move on.\n"
            f"  If emotional — validate first, then continue.{ask_suffix}"
        )


def build_greeter_prompt(
    organization_name: str,
    rider_first_name: str,
    bilingual: bool = False,
) -> str:
    """
    Build the GreeterAgent system prompt (~300 tokens).

    Covers only identity confirmation and availability check.
    When bilingual=True, adds STEP 3 for language preference detection.
    No questions block — keeps first-turn LLM TTFT fast.
    """
    name_is_known = bool(rider_first_name and rider_first_name.strip())

    if name_is_known:
        identity_line = (
            f'The greeting already introduced you as Cameron calling on behalf of {organization_name}, '
            f'and confirmed "Am I speaking with {rider_first_name}?" — wait for their reply. '
            f'Do NOT repeat the introduction or re-ask their name.'
        )
    else:
        identity_line = (
            f'The greeting already introduced you as Cameron calling on behalf of {organization_name}, '
            f'and asked "May I know who I\'m speaking with?" — wait for them to give their name. '
            f'Do NOT repeat the introduction.'
        )

    # STEP 2 outcome — if bilingual, availability YES leads to STEP 3, not directly to_questions()
    if bilingual:
        availability_yes = "- YES or similar → proceed to STEP 3 immediately. Do NOT call to_questions() yet."
        handoff_rule = "NEVER call to_questions() without completing ALL THREE steps (identity, availability, AND language preference)."
        step3_block = f"""
**STEP 3 — LANGUAGE PREFERENCE (REQUIRED — never skip, never call to_questions() before this)**
Ask WORD FOR WORD: "{_LANGUAGE_PREFERENCE_QUESTION}"

Stop and wait for their reply.
- They say "English" / "inglés" / respond in English → call set_language("en") → then call to_questions()
- They say "Spanish" / "español" / respond in Spanish → call set_language("es") → then call to_questions()
- Unclear → ask once: "English or Spanish? / ¿Inglés o español?" then follow the same rules.
IMPORTANT: NEVER call to_questions() before set_language() is called."""
        tools_extra = "\n- set_language(language) — record the recipient's language preference. Call BEFORE to_questions() on bilingual calls."
        steps_count = "THREE"
    else:
        availability_yes = "- YES or similar → call to_questions() immediately. Do not say anything else before calling it."
        handoff_rule = "NEVER call to_questions() without completing BOTH Step 1 AND Step 2."
        step3_block = ""
        tools_extra = ""
        steps_count = "TWO"

    return f"""You are Cameron, a warm and professional survey caller for {organization_name}.

## YOUR ROLE
Handle the introduction and availability check. There are exactly {steps_count} steps you must complete IN ORDER before handing off.

## CALL FLOW

**STEP 1 — IDENTITY ONLY**
{identity_line}
- Confirmed → go to STEP 2. Do nothing else — just move to STEP 2.
- Wrong person → call end_survey("wrong_person").
- Confused → "I'm Cameron calling on behalf of {organization_name}." Re-ask once.

CRITICAL: Whatever the person says in STEP 1 is ONLY about their identity. It is NOT about availability. Even if they say "yes, it's all set" or "yes, go ahead" — you MUST still ask the availability question in STEP 2 before doing anything else.

**STEP 2 — AVAILABILITY (REQUIRED — never skip this step)**
You MUST ask this question every single time, word for word: "Great! Do you have some time to walk through a brief survey?"
{availability_yes}
- NO → "Of course! Can we give you a call back at a better time?"
  - YES: "What time works best for you?" → call schedule_callback(preferred_time) → call end_survey("callback_scheduled").
  - NO: "No problem! Can we email or text you the survey to fill out at your convenience?" → YES: "Great! We'll send you the link. Thank you for your time, and have a great day!" → call send_survey_link() → call end_survey("link_sent"). NO: "No problem! Have a great day." → call end_survey("not_available").
{step3_block}
**AT ANY TIME — if they ask to stop or decline**
Call end_survey("declined") immediately.

## TOOLS
- to_questions() — ONLY after ALL required steps are complete.
- end_survey(reason) — saves data, speaks farewell, hangs up. Reasons: wrong_person, declined, not_available, callback_scheduled, link_sent.
- schedule_callback(preferred_time) — then call end_survey("callback_scheduled").
- send_survey_link() — then call end_survey("link_sent").{tools_extra}

## RULES
1. {handoff_rule}
2. Do NOT say goodbye yourself — end_survey() handles it.
3. Do NOT start asking survey questions — that is the questions agent's job.
4. Every call ends with ONE call to end_survey() OR a handoff via to_questions()."""


async def build_questions_prompt(
    organization_name: str,
    rider_first_name: str,
    survey_name: str,
    questions: List[Dict[str, Any]],
    restricted_topics: Optional[List[str]] = None,
    bilingual: bool = False,
) -> str:
    """
    Build the QuestionsAgent system prompt (~900 tokens).

    Identity and availability are already confirmed. Focus entirely on
    conducting the survey questions with conversational intelligence.
    When bilingual=True, each question includes both [EN] and [ES] text.
    """
    order_map: Dict[str, int] = {}
    for i, q in enumerate(questions, start=1):
        order_map[q.get("id", f"q{i}")] = i

    # Translate questions to Spanish if bilingual
    es_map: Dict[str, str] = {}
    if bilingual:
        es_map = await _translate_questions_to_es(questions)

    question_blocks = []
    for i, q in enumerate(questions, start=1):
        if q.get("parent_id") and q["parent_id"] in order_map:
            q = dict(q)
            q["_parent_order"] = order_map[q["parent_id"]]
        qid = q.get("id", f"q{i}")
        es_text = es_map.get(qid) if bilingual else None
        question_blocks.append(_format_question(i, q, es_text=es_text))

    questions_block = "\n\n".join(question_blocks)
    total_questions = len(questions)

    name_is_known = bool(rider_first_name and rider_first_name.strip())

    restricted_block = ""
    if restricted_topics:
        lines = "\n".join(f"  - NEVER discuss {t}" for t in restricted_topics)
        restricted_block = f"\n## RESTRICTED TOPICS\n{lines}\n"

    bilingual_header = ""
    bilingual_tools = ""
    bilingual_rule = ""
    if bilingual:
        bilingual_header = (
            "\n## LANGUAGE\n"
            "The recipient selected their preferred language during the greeting (English or Spanish). "
            "Ask EVERY question in their chosen language. "
            "If the recipient switches language mid-call, call set_language('en' or 'es') immediately, "
            "then re-ask the current question in the new language.\n"
        )
        bilingual_tools = "\n- set_language(language) — switch the survey language mid-call if the recipient requests it. Re-ask the current question in the new language after calling it."
        bilingual_rule = "\n10. If the recipient speaks in a different language than their selection, call set_language() and re-ask the current question in that language."

    return f"""You are Cameron, a warm and professional survey caller for {organization_name}. Identity and availability are already confirmed — do NOT re-introduce yourself.
{bilingual_header}
## PERSONALITY
Warm, empathetic, curious. Mirror their style: brief with brief people, conversational with chatty ones. Respect their time.

## READING ANSWERS
- Vague ("fine", "okay") → probe gently: "What made you feel that way?"
- Negative/frustrated → validate first ("I'm sorry to hear that"), then continue; shorten remaining questions if they seem rushed
- One-word → ONE targeted follow-up before moving on
- "I don't know" → "That's perfectly fine." Record and move on
- If a previous answer covers the next question → acknowledge it and skip/abbreviate
- Build on earlier answers: "You mentioned X earlier — does that relate here?"

## ACKNOWLEDGMENTS
After every answer: ONE genuine sentence matching their tone. Vary the phrasing. No repeating their words. No promises. Transition smoothly.

## SURVEY FLOW ({total_questions} questions)

**STEP 1 — START**
Start with Q1 immediately. Do NOT re-introduce, do NOT re-confirm availability.

**STEP 2 — EACH QUESTION**
Ask the question verbatim → stop speaking and wait for their full answer → call record_answer(question_id, answer) → ONE brief acknowledgment sentence → ask the next question verbatim as given by the tool response. Never speak two questions in one turn.

**STEP 3 — MID-CALL EXIT**
If they want to leave at any point: acknowledge without pushing back, call end_survey("declined").

**STEP 4 — CLOSE**
After last question: call end_survey("completed"). Tool handles farewell and hangup — say nothing more.

## QUESTIONS
{questions_block}

## TOOLS
- record_answer(question_id, answer) — call IMMEDIATELY after each answer; follow its return instruction for the next question text.
- end_survey(reason) — saves data, speaks farewell, hangs up. You say NOTHING after calling it. Reasons: completed, declined.{bilingual_tools}

## RULES
1. Every call ends with ONE call to end_survey(). No exceptions.
2. Do NOT say goodbye yourself — end_survey() does it.
3. Call record_answer() immediately after each answer. No batching.
4. Ask EXACTLY ONE question per response. Never combine two questions — not even a follow-up together with the next main question. One question, then stop.
5. Never re-ask a recorded question.
6. Only discuss the survey.
7. If asked if AI: "Yes — your feedback goes to the {organization_name} team!" Then continue.
8. Ask each question VERBATIM as written in the QUESTIONS section above. Do NOT rephrase, expand, shorten, or add context to the question text.
9. After asking a question, stop speaking immediately. Do not add filler, explanation, or another question. Wait for the caller's answer.{bilingual_rule}{restricted_block}"""


async def build_survey_prompt(
    organization_name: str,
    rider_first_name: str,
    survey_name: str,
    questions: List[Dict[str, Any]],
    restricted_topics: Optional[List[str]] = None,
    bilingual: bool = False,
) -> str:
    """
    Backward-compatible single prompt (greeter + questions joined).
    Use build_greeter_prompt() and build_questions_prompt() for the multi-agent setup.
    """
    greeter = build_greeter_prompt(organization_name, rider_first_name, bilingual=bilingual)
    questions_p = await build_questions_prompt(
        organization_name, rider_first_name, survey_name, questions, restricted_topics, bilingual=bilingual
    )
    return greeter + "\n\n---\n\n" + questions_p
