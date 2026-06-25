def generate_quiz_prompt(lecture_content: str) -> str:

    return f"""
You are an educational assessment expert.

Generate exactly 3 multiple-choice questions.

Requirements:

- 4 options per question.
- Only one correct answer.
- Questions must be based on the lecture.
- Return ONLY valid JSON.
- Do not use markdown.
- Do not add explanations.

Output format:

[
  {{
    "question": "What is Python?",
    "options": [
      "Programming Language",
      "Database",
      "Operating System",
      "Browser"
    ],
    "correct_answer": "Programming Language"
  }}
]

Lecture:

{lecture_content}
"""