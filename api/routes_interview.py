from fastapi import APIRouter, UploadFile, File, HTTPException
from core.models import StartInterviewResponse, AnswerRequest, AnswerResponse
from services.interview_service import InterviewService
from utils.cv_parser import extract_text_from_file

router = APIRouter(prefix="/interview", tags=["Interview"])
service = InterviewService()

@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        cv_text = extract_text_from_file(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process CV: {str(e)}")
    
    session_id, first_question = service.start_interview(cv_text)
    return StartInterviewResponse(session_id=session_id, first_question=first_question)

@router.post("/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(session_id: str, req: AnswerRequest):
    try:
        result = service.process_answer(session_id, req.answer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return AnswerResponse(**result)

@router.delete("/{session_id}")
async def end_interview(session_id: str):
    service.end_interview(session_id)
    return {"message": "Session ended"}