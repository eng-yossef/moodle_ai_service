from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState

# ---------- API Request / Response Models ----------
class StartInterviewResponse(BaseModel):
    session_id: str
    first_question: str

class AnswerRequest(BaseModel):
    answer: str

class AnswerResponse(BaseModel):
    next_question: Optional[str] = None
    is_finished: bool = False
    final_evaluation: Optional[Dict[str, Any]] = None   # {"level": "...", "feedback": "..."}

# ---------- Internal State (used by LangGraph) ----------
class InterviewState(MessagesState):
    """Custom state shared across interview agents."""
    cv_text: str = ""
    extracted_cv: Dict[str, Any] = Field(default_factory=dict)
    question_count: int = 0
    current_question: str = ""
    final_evaluation: Optional[Dict[str, Any]] = None
    phase: str = "init"  # init, interview, evaluation, done
    user_answer: Optional[str] = None