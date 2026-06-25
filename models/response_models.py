from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class LectureSummary(BaseModel):
    id: str
    title: str
    order: int
    summary: str

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str

class LectureDetail(LectureSummary):
    content: str
    quiz: Optional[List[QuizQuestion]] = None

class CourseGenerationResponse(BaseModel):
    course_id: str
    title: str
    lectures: List[LectureSummary]
    total_quizzes: int
    moodle_export_url: Optional[str] = None
    pdf_url: Optional[str] = None
    created_at: datetime