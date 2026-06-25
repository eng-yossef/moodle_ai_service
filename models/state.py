from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class CourseState(BaseModel):
    """State object used by the course generation graph"""
    course_id: str
    title: str
    description: Optional[str] = None
    raw_text: Optional[str] = None
    curriculum: Optional[List[Dict[str, str]]] = None   # <-- new
    chunks: Optional[List[str]] = None
    lectures: Optional[List[Dict[str, Any]]] = None  # list of {title, content, order}
    quizzes: Optional[List[Dict[str, Any]]] = None   # list of quizzes per lecture
    moodle_xml: Optional[str] = None
    errors: List[str] = []
    pdf_path: Optional[str] = None
    completed: bool = False
    created_at: datetime = datetime.utcnow()