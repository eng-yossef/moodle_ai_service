from typing import List, Dict, Any
import json

from langchain_openai import ChatOpenAI

from core.config import settings
from prompts.curriculum_prompt import generate_curriculum_prompt


class CurriculumAgent:

    def __init__(self):

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            base_url="https://openrouter.ai/api/v1",
            max_tokens=3000,
            api_key=settings.OPENAI_API_KEY
        ) if settings.OPENAI_API_KEY else None

    def generate_curriculum(
        self,
        text: str,
        num_lectures: int,
        course_title: str,
        course_description: str = ""
    ) -> List[Dict[str, Any]]:

        if not self.llm:
            return self._fallback_curriculum(
                num_lectures,
                course_title
            )

        prompt = f"""
{generate_curriculum_prompt(
    text,
    num_lectures,
    course_title,
    course_description
)}

IMPORTANT:

Return ONLY valid JSON.

Output Format:

[
    {{
        "title": "Introduction to AI",
        "summary": "Overview of AI concepts",
        "learning_objectives": [
            "Understand AI",
            "Learn applications"
        ]
    }}
]

Do not use markdown.
Do not wrap in ```json.
Do not add explanations.
"""

        try:

            response = self.llm.invoke(prompt)

            content = response.content.strip()

            print("\n====== CURRICULUM RAW RESPONSE ======")
            print(content[:1000])
            print("=====================================\n")

            if content.startswith("```json"):
                content = (
                    content
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            data = json.loads(content)

            if isinstance(data, list):
                return data

            if isinstance(data, dict):

                if "lectures" in data:
                    return data["lectures"]

                for value in data.values():
                    if isinstance(value, list):
                        return value

            raise ValueError(
                "Invalid curriculum response format"
            )

        except Exception as e:

            print(
                f"Curriculum generation failed: {e}"
            )

            return self._fallback_curriculum(
                num_lectures,
                course_title
            )

    def _fallback_curriculum(
        self,
        num_lectures: int,
        course_title: str
    ) -> List[Dict[str, Any]]:

        return [
            {
                "title": (
                    f"Lecture {i + 1}: "
                    f"{course_title}"
                ),
                "summary": (
                    "Overview of key concepts."
                ),
                "learning_objectives": []
            }
            for i in range(num_lectures)
        ]