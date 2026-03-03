import requests, json
from core.config import *

def ask_llm(question, context, history):

    prompt = f"""
You are an AI Course Assistant inside Moodle.
Your job is to help students and teachers with:
- Understanding course materials
- Explaining lessons
- Answering questions based on the provided course context
- Guiding users through Moodle course activities

STRICT RULES:
1) You MUST answer using the provided Context as the primary source.
2) If the answer is not in the Context, give a helpful general explanation
   related to the course topic.
3) If the question is NOT related to the course or Moodle learning,
   reply ONLY with:
   I can only answer questions related to this course in Moodle.
4) Do NOT answer general knowledge or unrelated questions.
5) Keep answers clear, structured, and educational.
6) When possible, give step-by-step guidance.

Context: {context}
History: {history}
Question: {question}
Answer:
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": SITE_URL,
        "X-Title": SITE_NAME,
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": f"Context: {context}"},
            {"role": "system", "content": f"History: {history}"},
            {"role": "user", "content": prompt},
        ],
    }

    response = requests.post(
        url=OPENROUTER_URL,
        headers=headers,
        data=json.dumps(payload),
    )

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return str(data)
    


def ask_helpdesk_llm(question, context_sources=None):

    if context_sources is None:
        context_sources = {}

    moodle_docs = context_sources.get("moodle_docs", "")
    site_name = context_sources.get("site_name", "")

    system_prompt = f"""
You are a Moodle Helpdesk AI for the site: {site_name}

Reference documentation:
{moodle_docs}

Rules:
1. Only answer Moodle-related questions.
2. NEVER invent Moodle features.
3. If unsure or admin-level issue → escalate=true.
4. If unrelated to Moodle → escalate=true.
5. Return VALID JSON ONLY.

Return JSON format:
{{
  "answer": "...",
  "confidence": 0-100,
  "escalate": true/false,
  "ticket_summary": "...",
  "priority": "low|medium|high",
  "category": "technical|account|course|other"
}}

Question:
{question}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": SITE_URL,
        "X-Title": SITE_NAME,
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You must return valid JSON only."},
            {"role": "user", "content": system_prompt},
        ],
        "temperature": 0.2
    }

    response = requests.post(
        url=OPENROUTER_URL,
        headers=headers,
        data=json.dumps(payload),
    )

    data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception:
        return {
            "answer": "",
            "confidence": 0,
            "escalate": True,
            "ticket_summary": question,
            "priority": "medium",
            "category": "technical"
        }





        