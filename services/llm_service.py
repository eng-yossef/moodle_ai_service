"""
services/llm_service.py

Sends prompts to OpenRouter (or any OpenAI-compatible API) via LangChain.

Fixes vs original:
  • Uses langchain_openai.ChatOpenAI for reliable, clean API calls.
  • Keeps the single system prompt, history parsing, and structured helpdesk output.
  • Temperature is set per call (0.7 for tutor, 0.2 for helpdesk).
"""

import json
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, AIMessage, SystemMessage

from core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_URL,
    MODEL_NAME,
    SITE_URL,
    SITE_NAME,
)


# ── Shared LLM helper ────────────────────────────────────────────────────────

def _get_chat_model(temperature: float = 0.7) -> ChatOpenAI:
    """
    Returns a ChatOpenAI instance configured for OpenRouter.
    """
    return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            base_url="https://openrouter.ai/api/v1",
            max_tokens=500,
            api_key=OPENROUTER_API_KEY
        ) if OPENROUTER_API_KEY else None


def _chat(messages: list[dict], temperature: float = 0.7) -> str:
    """
    Send a chat-completion request using LangChain.
    Returns the raw text content of the first choice.
    Raises RuntimeError on failure.
    """
    llm = _get_chat_model(temperature)
    try:
        # Convert dict messages to LangChain message objects
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                raise ValueError(f"Unknown role: {role}")

        response = llm.invoke(lc_messages)
        return response.content
    except Exception as exc:
        raise RuntimeError(f"LLM call failed: {exc}") from exc


# ── History parser (unchanged) ───────────────────────────────────────────────

def _parse_history(history: str) -> list[dict]:
    """
    Convert the flat history string (sent by PHP) into alternating
    user/assistant dicts.
    """
    messages = []
    for block in history.strip().split("\n\n"):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n", 1)
        if len(lines) == 2:
            q = lines[0].removeprefix("Q:").strip()
            a = lines[1].removeprefix("A:").strip()
            if q:
                messages.append({"role": "user",      "content": q})
            if a:
                messages.append({"role": "assistant", "content": a})
    return messages


# ── Course‑tutor LLM ─────────────────────────────────────────────────────────

def ask_llm(
    question:     str,
    context:      str = "",
    history:      str = "",
    file_context: str = "",   # RAG‑retrieved chunks
) -> str:
    """
    Ask the course-tutor LLM a question.
    """
    system_parts = [
        "You are an AI Course Assistant embedded in Moodle.",
        "Help students and teachers understand course materials, explain lessons, "
        "and guide them through activities.",
        "",
        "STRICT RULES:",
        "1. Answer primarily from the Context and Material sections below.",
        "2. If the answer is not in those sections, give a helpful general explanation "
        "   related to the course topic.",
        "3. If the question is completely unrelated to the course or Moodle, reply ONLY with: "
        "   'I can only answer questions related to this course in Moodle.'",
        "4. Keep answers clear, structured, and educational.",
        "5. When helpful, give step-by-step guidance.",
    ]

    if context:
        system_parts += ["", "--- Course Information ---", context]
    if file_context:
        system_parts += ["", "--- Relevant Material ---", file_context]

    system_prompt = "\n".join(system_parts)

    messages = [{"role": "system", "content": system_prompt}]
    messages += _parse_history(history)
    messages.append({"role": "user", "content": question})

    try:
        return _chat(messages, temperature=0.7)
    except RuntimeError as e:
        return f"Sorry, the AI service returned an error: {e}"


# ── Helpdesk LLM ─────────────────────────────────────────────────────────────

def ask_helpdesk_llm(
    question:        str,
    context_sources: dict | None = None,
) -> dict:
    """
    Ask the Moodle helpdesk LLM, returning structured JSON.
    """
    if context_sources is None:
        context_sources = {}

    moodle_docs = context_sources.get("moodle_docs", "")
    site_name   = context_sources.get("site_name", SITE_NAME)

    system_prompt = "\n".join([
        f"You are a Moodle Helpdesk AI for the site: {site_name}",
        "",
        "Reference documentation:",
        moodle_docs,
        "",
        "Rules:",
        "1. Only answer Moodle-related questions.",
        "2. NEVER invent Moodle features.",
        "3. If unsure or it is an admin-level issue → set escalate: true.",
        "4. If the question is unrelated to Moodle → set escalate: true.",
        "5. Return VALID JSON ONLY — no markdown fences, no extra text.",
        "",
        'Return this exact JSON shape:',
        '{',
        '  "answer": "...",',
        '  "confidence": 0-100,',
        '  "escalate": true/false,',
        '  "ticket_summary": "...",',
        '  "priority": "low|medium|high",',
        '  "category": "technical|account|course|other"',
        '}',
    ])

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": question},
    ]

    _fallback = {
        "answer":         "",
        "confidence":     0,
        "escalate":       True,
        "ticket_summary": question,
        "priority":       "medium",
        "category":       "technical",
    }

    try:
        raw = _chat(messages, temperature=0.2)
        raw = raw.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]          # remove opening fence + language
            raw = raw.split("```", 1)[0].strip()  # remove closing fence
        return json.loads(raw)
    except (RuntimeError, json.JSONDecodeError):
        return _fallback