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





        