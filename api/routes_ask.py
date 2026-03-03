from fastapi import APIRouter, Form
from services.llm_service import ask_llm
from utils.markdown_utils import to_html

router = APIRouter()

@router.post("/ask")
def ask(question: str = Form(...), context: str = Form(""), history: str = Form("")):
    reply_text = ask_llm(question, context, history)
    reply_html = to_html(reply_text)
    return {"reply": reply_html}