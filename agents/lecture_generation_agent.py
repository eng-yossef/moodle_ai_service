from typing import List, Dict, Any
import json

from langchain_openai import ChatOpenAI

from services.lecture_service import LectureService
from prompts.lecture_prompt import generate_lecture_prompt
from core.config import settings


class LectureGenerationAgent:

    def __init__(self):

        self.lecture_service = LectureService()

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            base_url="https://openrouter.ai/api/v1",
            max_tokens=2000,
            api_key=settings.OPENAI_API_KEY
        ) if settings.OPENAI_API_KEY else None

    def generate_lectures(
        self,
        curriculum: List[Dict[str, Any]],
        full_text: str,
        course_title: str
    ) -> List[Dict[str, Any]]:

        lectures = []

        for idx, topic in enumerate(curriculum):

            title = topic.get(
                "title",
                f"Lecture {idx + 1}"
            )

            summary = topic.get(
                "summary",
                ""
            )

            learning_objectives = topic.get(
                "learning_objectives",
                []
            )

            try:

                if self.llm:

                    prompt = f"""
{generate_lecture_prompt(
    full_text,
    title,
    summary,
    course_title
)}

Learning Objectives:
{json.dumps(learning_objectives, ensure_ascii=False)}

IMPORTANT:

Create a complete lecture.

Return ONLY valid JSON.

Format:

{{
    "title": "Lecture Title",
    "content": "Full lecture content"
}}

Do not use markdown.
Do not wrap with ```json.
"""

                    response = self.llm.invoke(prompt)

                    result = response.content.strip()

                    print(
                        f"\n====== LECTURE {idx + 1} RAW RESPONSE ======"
                    )
                    print(result[:1000])
                    print(
                        "\n============================================\n"
                    )

                    if result.startswith("```json"):
                        result = (
                            result
                            .replace("```json", "")
                            .replace("```", "")
                            .strip()
                        )

                    try:

                        lecture_data = json.loads(result)

                        generated_title = lecture_data.get(
                            "title",
                            title
                        )

                        content = lecture_data.get(
                            "content",
                            result
                        )

                    except Exception:

                        generated_title = title
                        content = result

                else:

                    generated_title = title

                    content = (
                        full_text[:2000]
                        + "\n\n(Content truncated)"
                    )

            except Exception as e:

                print(
                    f"Lecture generation failed "
                    f"for lecture '{title}': {e}"
                )

                generated_title = title

                content = (
                    f"Lecture content could not "
                    f"be generated.\n\n"
                    f"Summary:\n{summary}"
                )

            lecture = self.lecture_service.create_lecture(
                generated_title,
                content,
                idx + 1
            )

            lectures.append(lecture)

        return lectures