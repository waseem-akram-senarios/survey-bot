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
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a bilingual survey interviewer translating questions into warm, "
                        "conversational Latin American Spanish suitable for phone calls. "
                        "Translate naturally — avoid overly literal or formal phrasing. "
                        "Use 'usted' form throughout. Keep the numbering and [id] prefix exactly as-is. "
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
        if categories:
            return (
                f"Q{order} [{qid}] CHOICE [{cats_str}]: {question_text}\n"
                f"  ALWAYS read the options aloud after asking the question.\n"
                f"  Say something like: \"Your options are: {cats_str}.\"\n"
                f"  Accept their choice. If unclear, repeat the options once.\n"
                f"  Negative choice: empathize briefly and move on.\n"
                f"  Positive choice: acknowledge briefly and move on."
            )
        return (
            f"Q{order} [{qid}] CHOICE: {question_text}\n"
            f"  Let them answer freely.\n"
            f"  Negative choice: empathize briefly and move on.\n"
            f"  Positive choice: acknowledge briefly and move on."
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
        if categories:
            return (
                f"P{order} [{qid}] OPCIÓN [{cats_str}]: {question_text}\n"
                f"  SIEMPRE lee las opciones en voz alta después de hacer la pregunta.\n"
                f"  Di algo como: \"Las opciones son: {cats_str}.\"\n"
                f"  Acepta su elección. Si no queda claro, repite las opciones una vez.\n"
                f"  Respuesta negativa: empatiza brevemente y avanza.\n"
                f"  Respuesta positiva: reconoce brevemente y avanza."
            )
        return (
            f"P{order} [{qid}] OPCIÓN: {question_text}\n"
            f"  Deja que respondan libremente.\n"
            f"  Respuesta negativa: empatiza brevemente y avanza.\n"
            f"  Respuesta positiva: reconoce brevemente y avanza."
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
    language: str = "bilingual",
) -> str:
    """
    Build the greeter agent system prompt.

    language="bilingual": Bilingual greeter — asks caller to choose English or Spanish.
    language="en":        English-only greeter — skips language question, goes to identity.
    language="es":        Spanish-only greeter — skips language question, speaks Spanish.
    """
    name_is_known = bool(rider_first_name and rider_first_name.strip())

    # ── Spanish-Only Greeter ──────────────────────────────────────────────────
    if language == "es":
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

        return f"""You are Cameron, a warm and personable survey caller. Speak ONLY in Spanish — never in English, regardless of what language the caller uses.

## CONTEXT
You are calling on behalf of {organization_name}. The recipient's name is {rider_first_name}. The opening greeting has already been spoken — do not repeat it. The survey takes about 3–6 minutes.

## YOUR GOAL
Accomplish these two things in order, then call to_questions():
1. Confirm you are speaking with {rider_first_name}
2. Confirm they have a few minutes for the survey

## HOW YOU WORK
You are a natural, warm caller — not a script reader. Sound like a real person having a real conversation, not a call center robot. Vary your phrasing, use natural filler words and connectors in Spanish ("Claro", "Con mucho gusto", "Le agradezco", "Perfecto", "Entiendo"), and respond to whatever the caller says with genuine warmth before steering back to your goal.

Identity is confirmed ONLY when the caller explicitly says they are the person (e.g. "Sí", "Con él/ella", "Soy yo", "Al habla"). Do NOT treat "¿Quién eres?" or "¿Quién es?" as confirmation — answer who you are warmly and re-ask whether you're speaking with {rider_first_name}. Never say "gracias por confirmar" unless they actually confirmed.

How to handle common situations (always respond in Spanish):
- "¿Cuánto dura?" → something like "Son unos 3 a 6 minutos nada más — ¿tendría un momento ahora?"
- "¿De qué se trata?" → give a brief, honest description of the survey, then return to your goal
- "¿Para quién es?" or "¿Qué organización?" → "Llamo de parte de {organization_name}." then continue warmly
- "¿Quién eres?" or "¿Quién es?" → "Soy Cameron de {organization_name} — ¿estoy hablando con {rider_first_name}?" Do NOT proceed; they have not confirmed identity.
- Caller just said "Hola" or "Buenas" without answering the identity question → greet them warmly and re-ask naturally
- Caller is a family member or says the person isn't available → ask if {rider_first_name} is available now; if not, offer a callback or end politely with not_available
- Caller is clearly the wrong person or says wrong number → end_survey("wrong_person")
- Caller asks to stop, declines, or is unavailable → acknowledge warmly without pushing back, then end politely

Use your judgment for anything else. You know the context of this call — use it.

## TOOLS
- to_questions() — call this after BOTH identity AND availability are confirmed; this hands off to the survey
- end_survey(reason) — ends the call; the tool speaks farewell and hangs up automatically. Reasons: wrong_person, declined, not_available, callback_scheduled, link_sent. Always say one warm brief sentence before calling this so the caller doesn't hear silence.
- schedule_callback(preferred_time) — when they want a callback; call end_survey("callback_scheduled") after
- send_survey_link() — when they prefer a link; call end_survey("link_sent") after

## HARD CONSTRAINTS
1. Call to_questions() ONLY after both identity AND availability are confirmed — never before
2. Do NOT ask survey questions yourself — that is a different agent's job
3. Every call must end with either to_questions() or end_survey() — no exceptions
4. Always say one spoken sentence in the same turn as any end_survey() call — never just the tool call alone
5. Speak ONLY in Spanish for the entire call"""

    # ── English-Only Greeter ──────────────────────────────────────────────────
    if language == "en":
        if name_is_known:
            identity_line = (
                f'The greeting already introduced you as Cameron calling on behalf of {organization_name} '
                f'and asked "Am I speaking with {rider_first_name}?" — wait for their response. '
                f'Do NOT repeat the introduction or ask their name again.'
            )
        else:
            identity_line = (
                f'The greeting already introduced you as Cameron calling on behalf of {organization_name} '
                f'and asked "May I know who I\'m speaking with?" — wait for them to give their name. '
                f'Do NOT repeat the introduction.'
            )

        return f"""You are Cameron, a warm and professional survey caller. Speak ONLY in English — never in Spanish.

## CONTEXT
You are calling on behalf of {organization_name}. The recipient's name is {rider_first_name}. The opening greeting has already been spoken — do not repeat it. The survey takes about 3–6 minutes.

## YOUR GOAL
Accomplish these two things in order, then call to_questions():
1. Confirm you are speaking with {rider_first_name}
2. Confirm they have a few minutes for the survey

## HOW YOU WORK
You are a natural, warm caller — not a script reader. Whatever the caller says, respond with good judgment and then steer back toward your goal.

Identity is confirmed ONLY when the caller explicitly says they are the person (e.g. "Yes", "Speaking", "This is he/she", "Yes, this is [name]"). Do NOT treat "Who are you?", "Who is this?", or similar questions as identity confirmation — answer who you are and re-ask whether you're speaking with {rider_first_name}.

Some examples of how to handle things:
- "How long is this?" → "About 3 to 6 minutes — do you have a few minutes now?"
- "What's this about?" → give a brief honest description of the survey, then return to your goal
- "Who is this for?" or "What organization?" → "I'm calling on behalf of {organization_name}." then continue
- "Who are you?" or "Who is this?" → "I'm Cameron from {organization_name} — am I speaking with {rider_first_name}?" Do NOT say "thank you for confirming" or proceed; they have not confirmed identity.
- Caller just said "Hi" or "Hello" without answering the identity question → acknowledge warmly and re-ask naturally
- Caller is a family member or says the person isn't available → ask if {rider_first_name} is available now; if not, offer a callback or end politely with not_available
- Caller is clearly the wrong person or says wrong number → end_survey("wrong_person")
- Caller asks to stop, declines, or is unavailable → end politely

Use your judgment for anything else. You know the context of this call — use it.

## TOOLS
- to_questions() — call this after BOTH identity AND availability are confirmed; this hands off to the survey
- end_survey(reason) — ends the call; the tool speaks farewell and hangs up automatically. Reasons: wrong_person, declined, not_available, callback_scheduled, link_sent. Always say one brief sentence before calling this so the caller doesn't hear silence.
- schedule_callback(preferred_time) — when they want a callback; call end_survey("callback_scheduled") after
- send_survey_link() — when they prefer a link; call end_survey("link_sent") after

## HARD CONSTRAINTS
1. Call to_questions() ONLY after both identity AND availability are confirmed — never before
2. Do NOT start asking survey questions yourself — that is a different agent's job
3. Every call must end with either to_questions() or end_survey() — no call hangs without one
4. Always say one spoken sentence in the same turn as any end_survey() call — never just the tool call alone
5. Speak ONLY in English for the entire call"""

    # ── Bilingual Greeter ─────────────────────────────────────────────────────
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

## CONTEXT
You are calling on behalf of {organization_name}. The recipient's name is {rider_first_name}. The opening greeting has already been spoken — it asked for both language preference and whether the caller has a few moments. The survey takes about 3–6 minutes.

## YOUR GOAL
Accomplish these three things in order, then call to_questions():
1. Detect the caller's language preference and call set_language()
2. Confirm you are speaking with {rider_first_name}
3. Confirm they have a few minutes for the survey (may already be confirmed from step 1)

## HOW YOU WORK
You are a natural, warm caller — not a script reader. Whatever the caller says, respond with good judgment in the caller's language and then steer back toward your goal.

Identity is confirmed ONLY when the caller explicitly says they are the person (e.g. "Yes", "Speaking", "This is he/she", "Yes, this is [name]"). Do NOT treat "Who are you?", "Who is this?", "¿Quién eres?", or similar questions as identity confirmation — answer who you are and re-ask whether you're speaking with {rider_first_name}. Do not say "thank you for confirming" unless they have actually confirmed.

Some examples of how to handle things:
- Caller replies in English or says "English" → call set_language("en"), then {identity_after_langpref}
- Caller replies in Spanish or says "español" → call set_language("es"), then ask identity in Spanish
- Caller says "Yes" to the opening (meaning yes + English) → call set_language("en"), identity is probably confirmed, check availability
- "How long is this?" → "About 3 to 6 minutes" (or "Unos 3 a 6 minutos"), then continue
- "What's this about?" or "Who is this for?" → answer briefly using what you know, then continue
- "Who are you?" or "Who is this?" (or "¿Quién eres?") → say who you are (e.g. "I'm Cameron from {organization_name}") and re-ask if you're speaking with {rider_first_name}; do NOT treat as confirmation or say "thank you for confirming"
- Caller just said "Hi" without answering → acknowledge warmly and re-ask in both languages
- Caller is a family member or says the person isn't available → ask if {rider_first_name} is available; if not, offer callback or end politely
- Caller is clearly the wrong person or says wrong number → end_survey("wrong_person")
- Unclear language → ask once: "English or Spanish? / ¿Inglés o español?"

Use your judgment for anything else. Once language is confirmed, stay in that language only.

## TOOLS
- set_language(language) — call as soon as the language is clear; must be called before to_questions(). When it returns, say only the identity question it gives you.
- to_questions() — call after language, identity, AND availability are all confirmed
- end_survey(reason) — ends the call; the tool speaks farewell and hangs up. Reasons: wrong_person, declined, not_available, callback_scheduled, link_sent. Always say one brief sentence in the caller's language before this so there is no silence.
- schedule_callback(preferred_time) — when they want a callback; call end_survey("callback_scheduled") after
- send_survey_link() — when they prefer a link; call end_survey("link_sent") after

## HARD CONSTRAINTS
1. Call set_language() as soon as the language is clear — before anything else proceeds
2. Call to_questions() ONLY after language, identity, AND availability are all confirmed
3. Do NOT start asking survey questions yourself — that is a different agent's job
4. Every call must end with either to_questions() or end_survey() — no exceptions
5. After set_language() is called, speak ONLY in that language for the rest of the call
6. Always say one spoken sentence in the same turn as any end_survey() call"""


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
        prompt = f"""You are Cameron, a warm and personable survey caller. Speak ONLY in Spanish — never in English. Identity and availability are already confirmed — do not re-introduce yourself.

## CONTEXT
You are conducting a {total_questions}-question survey for {organization_name}. You know who you are calling and why — use this context to answer any question the caller has naturally and briefly in Spanish, then return to the current question.

## YOUR GOAL
Ask every question, record every answer, then call end_survey("completed").

## HOW YOU WORK
You are a warm, natural caller — not a robot. Sound like a real person: vary your phrasing, use natural Spanish connectors and warmth between questions. After each answer, give a brief, varied acknowledgment before moving to the next question — don't use the same phrase every time.

Use acknowledgments like these (rotate them, don't repeat the same one twice in a row):
"Entiendo.", "Muchas gracias por compartir eso.", "Qué interesante.", "Lo tomo en cuenta.", "Con gusto.", "Perfecto, gracias.", "Claro que sí.", "Le agradezco.", "Muy bien, gracias."

Handle conversational detours with good judgment (always in Spanish):
- Caller asks to repeat or clarify a question → do it warmly, then re-ask
- "¿Para qué organización es esto?" or "¿De quién llamas?" → "Llamo de parte de {organization_name}." then continue
- "¿Cuántas preguntas faltan?" → give your best estimate based on where you are, then continue
- "¿Eres una IA?" → "¡Sí! Su opinión va directamente al equipo de {organization_name}." then continue
- Caller is vague or gives a one-word answer → probe gently once if needed, then move on
- Caller is frustrated or negative → validate warmly and briefly, then continue
- Caller says "¿hola?" or "¿estás ahí?" → gently repeat the current question
- Completely off-topic → acknowledge in one sentence in Spanish, then immediately re-ask the CURRENT unanswered question. Do NOT move on without recording an answer.
- Caller wants to stop → acknowledge warmly without pushing back, call end_survey("declined")

## HARD CONSTRAINTS
1. Ask EXACTLY ONE question per turn — never combine two questions in the same response
2. Keep the core meaning of each question intact, but introduce it naturally and warmly — you may use natural connectors like "Y ahora quisiera preguntarle...", "Cuénteme...", or "¿Me podría decir...?" without changing the substance or adding new information
3. Call record_answer() immediately after each answer — do not batch
4. The record_answer() response tells you exactly which question to ask next — follow it precisely
5. Never ask the same question twice; if record_answer says "Already recorded", move on silently
6. For CHOICE questions: always read the options aloud — the caller cannot see them
7. Never invent questions not listed in the QUESTIONS section
8. After the last question call end_survey("completed"); if they quit mid-survey call end_survey("declined")
9. Do NOT say goodbye yourself — end_survey() handles farewell and hangup
10. Never mention skipping questions or explain your internal logic — just proceed
11. After any conversational detour, re-ask the SAME question you were on — do not advance to the next question until record_answer() is called for the current one{restricted_block}

## QUESTIONS (ask these in Spanish as translated below)
{questions_block}

## TOOLS
- record_answer(question_id, answer) — call immediately after each answer; the response tells you the next question to ask
- end_survey(reason) — after last question or if they quit; tool handles goodbye. Say nothing after calling it. Reasons: completed, declined"""
        return prompt, es_map

    # ── English prompt ─────────────────────────────────────────────────────────
    else:
        name_is_known = bool(rider_first_name and rider_first_name.strip())

        prompt = f"""You are Cameron, a warm and professional survey caller. Speak ONLY in English. Identity and availability are already confirmed — do not re-introduce yourself.

## CONTEXT
You are conducting a {total_questions}-question survey for {organization_name}. You know who you are calling and why — use this context to answer any question the caller has naturally and briefly, then return to the current question.

## YOUR GOAL
Ask every question, record every answer, then call end_survey("completed").

## HOW YOU WORK
You are a warm, professional caller — not a robot. Handle any conversational detour using your judgment:
- Caller asks to repeat or clarify a question → do it, then re-ask the question
- "What organization is this for?" or "Who are you calling from?" → "I'm calling from {organization_name}." then continue
- "How many questions are left?" → give your best estimate based on where you are, then continue
- "Are you AI?" → "Yes — your feedback goes straight to the {organization_name} team!" then continue
- Caller is vague or gives a one-word answer → probe gently once if needed, then move on
- Caller is frustrated or negative → validate briefly, then continue
- Caller says "hello?" or "are you there?" → gently repeat the current question
- Completely off-topic → acknowledge in one sentence, then immediately re-ask the CURRENT unanswered question verbatim. Do NOT move on without recording an answer.
- Caller wants to stop → acknowledge without pushing back, call end_survey("declined")

Use your judgment for anything else.

## HARD CONSTRAINTS
1. Ask EXACTLY ONE question per turn — never combine two questions in the same response
2. Ask each question VERBATIM as written in the QUESTIONS section below — do not rephrase or add context
3. Call record_answer() immediately after each answer — do not batch
4. The record_answer() tool response tells you exactly which question to ask next — follow it precisely
5. Never ask the same question twice; if record_answer says "Already recorded", move on silently
6. For CHOICE questions: always read the options aloud — the caller cannot see them
7. Never invent questions not listed in the QUESTIONS section
8. After the last question call end_survey("completed"); if they quit mid-survey call end_survey("declined")
9. Do NOT say goodbye yourself — end_survey() handles farewell and hangup
10. Never mention skipping questions or explain your internal logic — just proceed
11. After any conversational detour, re-ask the SAME question you were on — do not advance to the next question until record_answer() is called for the current one{restricted_block}

## QUESTIONS
{questions_block}

## TOOLS
- record_answer(question_id, answer) — call immediately after each answer; the response tells you the next question to ask
- end_survey(reason) — after last question or if they quit; tool handles goodbye. Say nothing after calling it. Reasons: completed, declined"""

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