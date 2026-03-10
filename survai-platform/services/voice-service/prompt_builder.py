# -*- coding: utf-8 -*-
"""
Survey System Prompt Builder for Voice Service.

Two focused prompts are built here:
  - build_greeter_prompt()   — ~300 tokens, language-specific greeter instructions
  - build_questions_prompt() — ~900 tokens, questions + recording intelligence

Language is always a single, fixed value per call: "en" or "es".
No bilingual mode.

build_survey_prompt() is kept as a backward-compatible alias (returns joined text).
"""

import hashlib
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
_ES_TRANSLATION_CACHE: Dict[str, Dict[str, str]] = {}


def _translation_cache_key(questions: List[Dict[str, Any]]) -> str:
    payload = "\n".join(
        f"{q.get('id', '')}|{q.get('text', '')}"
        for q in questions
        if isinstance(q, dict)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


async def _translate_questions_to_es(questions: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Batch-translate all question texts to Spanish using OpenAI.
    Returns a dict mapping question_id -> Spanish text.
    Falls back gracefully to empty dict on any error.
    """
    if not questions:
        return {}

    cache_key = _translation_cache_key(questions)
    cached = _ES_TRANSLATION_CACHE.get(cache_key)
    if cached:
        logger.info(f"Using cached Spanish translation for {len(cached)} questions")
        return cached

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set — Spanish questions will use English text")
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
            text = line.strip()
            bracket_end = text.find("] ")
            if bracket_end != -1:
                text = text[bracket_end + 2:]
            elif ". " in text:
                text = text.split(". ", 1)[-1]
            result[qid] = text

        _ES_TRANSLATION_CACHE[cache_key] = result
        logger.info(f"Translated {len(result)} questions to Spanish")
        return result

    except Exception as e:
        logger.warning(f"Question translation to Spanish failed: {e} — using English text")
        return {}


def _format_question_en(order: int, q: Dict[str, Any]) -> str:
    """Format a single question block for the English-only agent prompt."""
    qid = q.get("id", f"q{order}")
    text = q.get("text", "")
    criteria = q.get("criteria", "open")
    categories = q.get("categories", [])
    scale_max = q.get("scales") or 5
    parent_id = q.get("parent_id")
    parent_order = q.get("_parent_order", "")
    trigger_cats = q.get("parent_category_texts", [])

    question_text = f'"{text}"'

    if parent_id:
        trigger_str = ", ".join(trigger_cats) if trigger_cats else "any answer"
        return (
            f"Q{order} [{qid}] CONDITIONAL (ask ONLY IF the answer to Q{parent_order} "
            f"includes: {trigger_str}): {question_text}\n"
            f"  Skip entirely if the condition is not met."
        )
    elif criteria == "scale":
        return (
            f"Q{order} [{qid}] SCALE 1-{scale_max} (1=very poor, {scale_max}=excellent): {question_text}\n"
            f"  Ask it word-for-word. Always tell the caller: '1 is very poor, {scale_max} is excellent.'\n"
            f"  If they give a word instead of a number, ask once: \"If you had to put a number on it — where 1 is very poor and {scale_max} is excellent — what number between 1 and {scale_max} would you give?\"\n"
            f"  After recording their answer: give ONE brief acknowledgment sentence, then move to the next question.\n"
            f"  Do NOT ask a follow-up or probe in the same response as the acknowledgment."
        )
    elif criteria == "categorical":
        cats_str = ", ".join(categories) if categories else "open"
        return (
            f"Q{order} [{qid}] CHOICE [{cats_str}]: {question_text}\n"
            f"  Let them answer freely. Only list the options if they seem stuck.\n"
            f"  Negative choice: empathize and ask ONE follow-up.\n"
            f"  Positive choice: celebrate briefly and move on."
        )
    else:
        return (
            f"Q{order} [{qid}] OPEN: {question_text}\n"
            f"  If vague (\"fine\", \"okay\", \"good\") — probe gently with ONE clarifying question.\n"
            f"  If detailed — acknowledge warmly and move on.\n"
            f"  If emotional — validate first, then continue."
        )


def _format_question_es(order: int, q: Dict[str, Any], es_text: str) -> str:
    """Format a single question block for the Spanish-only agent prompt."""
    qid = q.get("id", f"q{order}")
    criteria = q.get("criteria", "open")
    categories = q.get("categories", [])
    scale_max = q.get("scales") or 5
    parent_id = q.get("parent_id")
    parent_order = q.get("_parent_order", "")
    trigger_cats = q.get("parent_category_texts", [])

    question_text = f'"{es_text}"'

    if parent_id:
        trigger_str = ", ".join(trigger_cats) if trigger_cats else "cualquier respuesta"
        return (
            f"P{order} [{qid}] CONDICIONAL (preguntar SOLO SI la respuesta a P{parent_order} "
            f"incluye: {trigger_str}): {question_text}\n"
            f"  Omitir completamente si no se cumple la condición."
        )
    elif criteria == "scale":
        return (
            f"P{order} [{qid}] ESCALA 1-{scale_max} (1=muy malo, {scale_max}=excelente): {question_text}\n"
            f"  Pregunta tal cual. Siempre indica: '1 es muy malo, {scale_max} es excelente.'\n"
            f"  Si dan una palabra en vez de número, pregunta una vez: \"¿Si tuviera que darle un número, donde 1 es muy malo y {scale_max} es excelente, qué número entre 1 y {scale_max} le daría?\"\n"
            f"  Después de registrar su respuesta: una breve frase de reconocimiento y pasa a la siguiente pregunta.\n"
            f"  NO hagas una pregunta de seguimiento en la misma respuesta que el reconocimiento."
        )
    elif criteria == "categorical":
        cats_str = ", ".join(categories) if categories else "abierto"
        return (
            f"P{order} [{qid}] OPCIÓN [{cats_str}]: {question_text}\n"
            f"  Deja que respondan libremente. Solo menciona las opciones si parecen perdidos.\n"
            f"  Respuesta negativa: empatiza y haz UNA pregunta de seguimiento.\n"
            f"  Respuesta positiva: celebra brevemente y avanza."
        )
    else:
        return (
            f"P{order} [{qid}] ABIERTA: {question_text}\n"
            f"  Si es vaga (\"bien\", \"regular\") — indaga gentilmente con UNA pregunta aclaratoria.\n"
            f"  Si es detallada — agradece y avanza.\n"
            f"  Si es emocional — valida primero, luego continúa."
        )


def build_greeter_prompt(
    organization_name: str,
    rider_first_name: str,
    language: str = "en",
) -> str:
    """
    Build the greeter agent system prompt (~300 tokens).

    language="en": English greeter with lang-pref detection step.
    language="es": Spanish greeter — identity + availability only, no lang-pref.
    """
    name_is_known = bool(rider_first_name and rider_first_name.strip())

    if language == "es":
        # ── Spanish Greeter (instructions in English; agent speaks Spanish to caller) ──
        if name_is_known:
            identity_line = (
                f'The greeting already introduced you as Cameron calling on behalf of {organization_name} '
                f'and asked "¿Estoy hablando con {rider_first_name}?" — wait for their response. '
                f'Do NOT repeat the introduction or ask their name again.'
            )
        else:
            identity_line = (
                f'The greeting already introduced you as Cameron calling on behalf of {organization_name} '
                f'and asked "¿Con quién tengo el gusto de hablar?" — wait for them to give their name. '
                f'Do NOT repeat the introduction.'
            )

        return f"""You are Cameron, a warm and professional survey caller for {organization_name}.

CRITICAL: You must SPEAK to the caller ONLY in Spanish. All your spoken output must be in Spanish. These instructions are in English for the operator; follow them but respond to the caller in Spanish.

## YOUR ROLE
Handle the introduction and verify availability. There are exactly TWO steps you must complete IN ORDER before handing off.

## CALL FLOW

**STEP 1 — IDENTITY ONLY**
{identity_line}
- Confirmed → go to STEP 2. Do nothing else — just proceed to STEP 2.
- Wrong person → call end_survey("wrong_person").
- Confused → say "Soy Cameron llamando de parte de {organization_name}." Ask once more.

CRITICAL: What the person says in STEP 1 is ONLY about their identity. It is NOT about availability.

**STEP 2 — AVAILABILITY (MANDATORY — do not skip)**
You MUST ask this question exactly: "¡Perfecto! ¿Tiene unos minutos para responder una breve encuesta?"
- YES → call to_questions() immediately. Say nothing else before calling it.
- NO → say "¡Claro! ¿Podemos llamarle en otro momento?"
  - YES: "¿Qué hora le vendría bien?" → call schedule_callback(preferred_time) → call end_survey("callback_scheduled").
  - NO: "¡No hay problema! ¿Le enviamos la encuesta por correo para que la complete cuando pueda?" → YES: call send_survey_link() → call end_survey("link_sent"). NO: say "¡Sin problema! Que tenga un buen día." → call end_survey("not_available").

**AT ANY TIME — if they ask to stop or decline**
Call end_survey("declined") immediately.

## TOOLS
- to_questions() — ONLY after BOTH steps are complete.
- end_survey(reason) — saves data, speaks farewell, hangs up. Reasons: wrong_person, declined, not_available, callback_scheduled, link_sent.
- schedule_callback(preferred_time) — then call end_survey("callback_scheduled").
- send_survey_link() — then call end_survey("link_sent").

## RULES
1. NEVER call to_questions() without completing BOTH steps (identity AND availability).
2. Do NOT say goodbye yourself — end_survey() does it.
3. Do NOT start asking survey questions — that is the questions agent's job.
4. Every call ends with ONE call to end_survey() OR a handoff via to_questions().
5. SPEAK to the caller ALWAYS and ONLY in Spanish. NEVER use English when talking to the caller."""

    # ── English Greeter ────────────────────────────────────────────────────────
    if name_is_known:
        identity_after_langpref = (
            f'After language is detected, ask for identity in the chosen language. '
            f'In English: "Am I speaking with {rider_first_name}?" '
            f'In Spanish: "¿Estoy hablando con {rider_first_name}?"'
        )
    else:
        identity_after_langpref = (
            f'After language is detected, ask for identity in the chosen language. '
            f'In English: "May I know who I\'m speaking with?" '
            f'In Spanish: "¿Con quién tengo el gusto de hablar?"'
        )

    return f"""You are Cameron, a warm and professional survey caller for {organization_name}.

## YOUR ROLE
Handle language detection, identity, and availability. There are exactly THREE steps you must complete IN ORDER before handing off.

NOTE: The opening line already introduced the survey and asked for language preference. It did NOT fully confirm identity, and it does NOT by itself confirm availability unless the caller explicitly volunteered that they have time.

## CALL FLOW

**STEP 1 — LANGUAGE PREFERENCE**
Wait for the recipient's reply to the opening line.
- They explicitly say "English" OR clearly answer in English → call set_language("en").
- They explicitly say "Spanish" / "español" OR clearly answer in Spanish → call set_language("es").
- A bare "yes", "hello", "speaking", "okay", or other short ambiguous reply is NOT enough to infer language. In that case ask once: "English or Spanish? / ¿Inglés o español?"
- If they explicitly say both language and availability (e.g. "English, yes I have time"), you may remember availability for STEP 3.
- They decline immediately → call end_survey("declined").
- Unclear → ask once: "English or Spanish? / ¿Inglés o español?" then follow the same rules.
IMPORTANT: Call set_language() as soon as the language is clear.

**STEP 2 — IDENTITY (in the chosen language)**
{identity_after_langpref}
- Treat identity as CONFIRMED if they clearly say yes ("yes", "yeah", "speaking", "this is he", "this is she", "soy yo", "sí") or give the expected name.
- If the reply is silence, unclear audio, background noise, a greeting only, or otherwise ambiguous, repeat the identity question once in the same language. Do NOT end the call on ambiguous audio.
- Call end_survey("wrong_person") ONLY if they explicitly say they are NOT the person (for example: "no", "wrong number", "that's not me", "you have the wrong person", "no soy esa persona").
- Treat close spelling/pronunciation variants of the same name (for example Alan/Allen, Jon/John, Steve/Steven) as likely confirmed, not wrong person.

**STEP 3 — VERIFY AVAILABILITY**
- If they already explicitly confirmed they have time earlier, call to_questions() immediately after STEP 2 is done.
- Otherwise ask availability now:
  In English: "Great! Do you have some time to walk through a brief survey?"
  In Spanish: "¡Perfecto! ¿Tiene unos minutos para responder una breve encuesta?"
  - YES → call to_questions() immediately.
  - NO → offer callback or link, then end accordingly.

**AT ANY TIME — if they ask to stop or decline**
Call end_survey("declined") immediately.

## TOOLS
- set_language(language) — call as soon as language preference is detected. MUST be called before to_questions().
- to_questions() — ONLY after ALL THREE steps are complete.
- end_survey(reason) — saves data, speaks farewell, hangs up. Reasons: wrong_person, declined, not_available, callback_scheduled, link_sent.
- schedule_callback(preferred_time) — then call end_survey("callback_scheduled").
- send_survey_link() — then call end_survey("link_sent").

## RULES
1. NEVER call to_questions() without completing ALL THREE steps.
2. Do NOT say goodbye yourself — end_survey() handles it.
3. Do NOT start asking survey questions — that is the questions agent's job.
4. Every call ends with ONE call to end_survey() OR a handoff via to_questions().
5. After set_language() is called, speak ONLY in that language. NEVER mix languages.
6. When set_language() returns, say ONLY the identity question given in the return value. Do NOT repeat or paraphrase any other part of the return value aloud.
7. NEVER call end_survey("wrong_person") on an uncertain, empty, or low-confidence reply. Only do it after an explicit negative identity response."""


async def build_questions_prompt(
    organization_name: str,
    rider_first_name: str,
    survey_name: str,
    questions: List[Dict[str, Any]],
    restricted_topics: Optional[List[str]] = None,
    language: str = "en",
) -> Any:  # Returns (prompt_text, translated_map)
    """
    Build the QuestionsAgent system prompt (~900 tokens).

    Returns:
        tuple: (prompt_text: str, questions_map: dict)
    """
    order_map: Dict[str, int] = {}
    for i, q in enumerate(questions, start=1):
        order_map[q.get("id", f"q{i}")] = i

    # Translate questions to Spanish if needed
    es_map: Dict[str, str] = {}
    if language == "es":
        es_map = await _translate_questions_to_es(questions)

    question_blocks = []
    for i, q in enumerate(questions, start=1):
        if q.get("parent_id") and q["parent_id"] in order_map:
            q = dict(q)
            q["_parent_order"] = order_map[q["parent_id"]]
        qid = q.get("id", f"q{i}")
        if language == "es":
            es_text = es_map.get(qid) or q.get("text", "")
            question_blocks.append(_format_question_es(i, q, es_text))
        else:
            question_blocks.append(_format_question_en(i, q))

    questions_block = "\n\n".join(question_blocks)
    total_questions = len(questions)

    restricted_block = ""
    if restricted_topics:
        lines = "\n".join(f"  - NEVER discuss {t}" for t in restricted_topics)
        restricted_block = f"\n## RESTRICTED TOPICS\n{lines}\n"

    if language == "es":
        prompt = f"""You are Cameron, a warm and professional survey caller for {organization_name}. Identity and availability are already confirmed — do NOT re-introduce yourself.

CRITICAL: You must SPEAK to the caller ONLY in Spanish. All your spoken output must be in Spanish. These instructions are in English for the operator; follow them but respond to the caller in Spanish.

## PERSONALITY
Warm, empathetic, curious. Adapt your style: brief with concise people, conversational with chatty ones.

## READING ANSWERS
- Vague ("bien", "más o menos") → probe: "¿Qué te hizo sentir así?"
- Negative/frustrated → validate first ("Lamento escuchar eso"), then continue
- One-word → ONE follow-up question before moving on
- "No sé" → say "Está perfectamente bien." Record and move on

## ACKNOWLEDGMENTS
After every answer: One VERY brief, genuine response (max 5-7 words, in Spanish). Do not repeat their words. Immediate transition.

## SKIPPING QUESTIONS — SILENTLY
If a previous answer already covered a future question: SKIP IT silently. NEVER mention that you are skipping a question or explain why. Simply move to the next available question.

## SURVEY FLOW ({total_questions} questions)

**STEP 1 — START**
Begin with P1 immediately. Do NOT re-introduce or confirm availability again.

**STEP 2 — EACH QUESTION**
Ask the question verbatim (in Spanish, as given in PREGUNTAS below) → wait for their full answer → call record_answer(question_id, answer) → ONE brief acknowledgment (in Spanish) → ask the next question verbatim. Never ask two questions in one turn.

**STEP 3 — MID-CALL EXIT**
If they want to leave: acknowledge without pushing back, call end_survey("declined").

**STEP 4 — CLOSE**
After the last question: call end_survey("completed"). The tool handles farewell and hangup — say nothing more.

## PREGUNTAS (ask these in Spanish, word-for-word as written)
{questions_block}

## TOOLS
- record_answer(question_id, answer) — call IMMEDIATELY after each answer; follow its return instruction for the next question text.
- end_survey(reason) — saves data, speaks farewell, hangs up. Say NOTHING after calling it. Reasons: completed, declined.

## RULES
1. Every call ends with ONE call to end_survey(). No exceptions.
2. Do NOT say goodbye yourself — end_survey() does it.
3. Call record_answer() immediately after each answer. No batching.
4. Ask EXACTLY ONE question per response. Never combine two questions.
5. NEVER re-ask a question you already asked, even if the caller gives a short or unclear answer. Record what they said and move to the next question.
6. Only discuss the survey.
7. If asked if you are AI: say "¡Sí! Tu opinión va directamente al equipo de {organization_name}." Then continue.
8. After asking a question, stop speaking immediately. Do not add filler or another question. Wait for the caller's answer.
9. NEVER explain your internal reasoning or mention what the tool told you. Speak only as Cameron.
10. NEVER say things like "ya que respondiste X, saltaremos Y". Just ask the next question.
11. If the caller says "hello?", "are you there?", or seems to be waiting for you, respond immediately. If you were waiting for their answer, gently repeat the current question ONCE.
12. NEVER ask the same question more than once. If record_answer returns "Already recorded", move to the next question immediately without commenting.{restricted_block}"""
        return prompt, es_map

    # ── English prompt ─────────────────────────────────────────────────────────
    else:
        name_is_known = bool(rider_first_name and rider_first_name.strip())

        prompt = f"""You are Cameron, a warm and professional survey caller for {organization_name}. Identity and availability are already confirmed — do NOT re-introduce yourself.

## LANGUAGE — CRITICAL
You MUST speak ONLY in English for the ENTIRE survey. NEVER use Spanish.

## PERSONALITY
Warm, empathetic, curious. Mirror their style: brief with brief people, conversational with chatty ones. Respect their time.

## READING ANSWERS
- If a previous answer covers the next question → SKIP IT silently. NEVER mention that you are skipping a question or explain why. Simply move to the next available question.
- Vague ("fine", "okay") → probe only if the question is critical.
- Negative/frustrated → Brief validation, then continue.
- Do NOT explain your internal reasoning or why you are skipping questions.
## ACKNOWLEDGMENTS
After every answer: One VERY brief, genuine sentence (max 5-7 words). Do not repeat their words. Transition immediately.

## SKIPPING QUESTIONS — SILENTLY
If a previous answer covers the next question: SKIP IT silently. NEVER mention that you are skipping a question or explain why. Simply move to the next available question.

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
- end_survey(reason) — saves data, speaks farewell, hangs up. You say NOTHING after calling it. Reasons: completed, declined.

## RULES
1. Every call ends with ONE call to end_survey(). No exceptions.
2. Do NOT say goodbye yourself — end_survey() does it.
3. Call record_answer() immediately after each answer. No batching.
4. Ask EXACTLY ONE question per response. Never combine two questions.
5. NEVER re-ask a question you already asked, even if the caller gives a short or unclear answer. Record what they said and move to the next question.
6. Only discuss the survey.
7. If asked if AI: "Yes — your feedback goes to the {organization_name} team!" Then continue.
8. Ask each question VERBATIM as written in the QUESTIONS section above. Do NOT rephrase, expand, shorten, or add context to the question text.
9. After asking a question, stop speaking immediately. Do not add filler, explanation, or another question. Wait for the caller's answer.
10. NEVER explain your internal reasoning or mention that you are skipping a question based on a previous answer.
11. NEVER say things like "since you already answered X, I'll move to Y". Just ask Y.
12. If the caller says "hello?", "are you there?", or seems to be waiting for you, respond immediately. If you were waiting for their answer, gently repeat the current question ONCE.
13. NEVER ask the same question more than once. If record_answer returns "Already recorded", move to the next question immediately without commenting.{restricted_block}"""

    return prompt, es_map if language == "es" else {}


async def build_survey_prompt(
    organization_name: str,
    rider_first_name: str,
    survey_name: str,
    questions: List[Dict[str, Any]],
    restricted_topics: Optional[List[str]] = None,
    language: str = "en",
) -> str:
    """
    Backward-compatible single prompt (greeter + questions joined).
    Use build_greeter_prompt() and build_questions_prompt() for the multi-agent setup.
    """
    greeter = build_greeter_prompt(organization_name, rider_first_name, language=language)
    questions_p, _ = await build_questions_prompt(
        organization_name, rider_first_name, survey_name, questions, restricted_topics, language=language
    )
    return greeter + "\n\n---\n\n" + questions_p
