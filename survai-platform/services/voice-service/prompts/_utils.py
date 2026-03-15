# -*- coding: utf-8 -*-
"""
Shared utilities for prompt builders:
  - Spanish translation cache + batch-translation via OpenAI
  - Per-language question block formatters
"""

import hashlib
import logging
import os
from typing import Any, Dict, List

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
