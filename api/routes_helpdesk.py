# file: api/routes_helpdesk.py
from fastapi import APIRouter
from pydantic import BaseModel
from services.llm_service import ask_helpdesk_llm 

router = APIRouter()

# Only question is sent from PHP
class RequestModel(BaseModel):
    question: str

@router.post("/helpdesk-ai")
def helpdesk_ai(req: RequestModel):
    # Hard-coded context sources
    context_sources = {
        "moodle_docs": "https://docs.moodle.org/",
        "site_name": "My Moodle Site"
    }

    # Call your LLM service
    result = ask_helpdesk_llm(
        question=req.question,
        context_sources=context_sources
    )

    return result