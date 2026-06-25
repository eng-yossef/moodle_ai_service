from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class CourseState(BaseModel):
    course_id: str
    title: str
    description: Optional[str] = None
    raw_text: Optional[str] = None
    curriculum: Optional[List[Dict[str, str]]] = None
    lectures: Optional[List[Dict[str, Any]]] = None
    quizzes: Optional[List[List[Dict[str, Any]]]] = None
    moodle_xml: Optional[str] = None
    pdf_path: Optional[str] = None                     # complete course PDF
    lecture_pdf_paths: Optional[List[str]] = None      # list of lecture PDF paths
    zip_path: Optional[str] = None                     # ZIP package path
    errors: List[str] = []
    completed: bool = False
    created_at: datetime = datetime.utcnow()