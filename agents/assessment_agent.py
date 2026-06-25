from typing import List, Dict, Any
from services.quiz_service import QuizService
from prompts.quiz_prompt import generate_quiz_prompt

from langchain_openai import ChatOpenAI
from core.config import settings

import json


class AssessmentAgent:
    def __init__(self):
        self.quiz_service = QuizService()

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            base_url="https://openrouter.ai/api/v1",
            max_tokens=1000,
            api_key=settings.OPENAI_API_KEY
        ) if settings.OPENAI_API_KEY else None

    def generate_quizzes(
        self,
        lectures: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:

        quizzes = []

        for lecture in lectures:
            try:
                if self.llm:
                    prompt = generate_quiz_prompt(
                        lecture["content"]
                    )

                    response = self.llm.invoke(prompt)

                    content = response.content.strip()

                    print("\n========== QUIZ RAW RESPONSE ==========")
                    print(content)
                    print("=======================================\n")

                    if content.startswith("```json"):
                        content = (
                            content
                            .replace("```json", "")
                            .replace("```", "")
                            .strip()
                        )

                    try:
                        qs = json.loads(content)

                        # ✅ Validation: ensure the response is a list
                        if not isinstance(qs, list):
                            raise ValueError("Quiz response is not a list")

                    except Exception as e:
                        print(
                            f"Failed to parse LLM response for lecture "
                            f"{lecture['title']}: {e}"
                        )

                        qs = self.quiz_service.create_quiz(
                            lecture["content"],
                            lecture["title"]
                        )

                else:
                    qs = self.quiz_service.create_quiz(
                        lecture["content"],
                        lecture["title"]
                    )

            except Exception as e:
                print(f"Quiz generation error: {e}")

                qs = self.quiz_service.create_quiz(
                    lecture["content"],
                    lecture["title"]
                )

            quizzes.append(qs)

        return quizzes
