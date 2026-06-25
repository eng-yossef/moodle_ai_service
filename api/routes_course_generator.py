from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException
)

from fastapi.responses import FileResponse

from typing import Optional
from datetime import datetime
from pathlib import Path
import uuid
import os

from core.dependencies import get_course_generator_service
from services.course_generator_service import CourseGeneratorService
from models.response_models import (
    CourseGenerationResponse,
    LectureSummary
)
from core.config import settings

router = APIRouter(
    prefix="/course",
    tags=["Course Generator"]
)


@router.post(
    "/generate",
    response_model=CourseGenerationResponse
)
async def generate_course(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    num_lectures: int = Form(5, ge=1, le=20),
    include_quizzes: bool = Form(True),
    moodle_export: bool = Form(True),  # currently always true for XML
    service: CourseGeneratorService = Depends(
        get_course_generator_service
    )
):

    allowed_extensions = [
        "pdf",
        "ppt",
        "pptx"
    ]

    ext = file.filename.split(".")[-1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File must be one of: "
                f"{', '.join(allowed_extensions)}"
            )
        )

    file_bytes = await file.read()

    if len(file_bytes) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large (max 50MB)"
        )

    course_id = f"course_{uuid.uuid4().hex[:8]}"

    request_data = {
        "course_id": course_id,
        "title": title,
        "description": description,
        "num_lectures": num_lectures,
        "include_quizzes": include_quizzes,
        "moodle_export": moodle_export
    }

    result = await service.generate_course(
        request_data,
        file_bytes,
        file.filename
    )

    lectures_summary = []

    for lec in result.get("lectures", []):
        lectures_summary.append(
            LectureSummary(
                id=lec.get("id", ""),
                title=lec.get("title", ""),
                order=lec.get("order", 0),
                summary=lec.get("content", "")[:200]
            )
        )

    # --------------------------------------------------
    # Helper: build download URL if file exists
    # --------------------------------------------------
    def get_download_url(filepath: str) -> Optional[str]:
        if filepath and os.path.exists(filepath):
            return f"/course/download/{os.path.basename(filepath)}"
        return None

    # --------------------------------------------------
    # Moodle XML
    # --------------------------------------------------
    moodle_url = None
    if result.get("moodle_xml"):
        xml_path = os.path.join(
            settings.OUTPUT_DIR,
            course_id,
            f"{course_id}_moodle.xml"
        )
        if os.path.exists(xml_path):
            moodle_url = f"/course/download/{os.path.basename(xml_path)}"

    # --------------------------------------------------
    # PDF (full course)
    # --------------------------------------------------
    pdf_url = get_download_url(result.get("pdf_path"))

    # --------------------------------------------------
    # Lecture PDFs
    # --------------------------------------------------
    lecture_pdf_urls = []
    for path in result.get("lecture_pdf_paths", []):
        url = get_download_url(path)
        if url:
            lecture_pdf_urls.append(url)

    # --------------------------------------------------
    # ZIP archive
    # --------------------------------------------------
    zip_url = get_download_url(result.get("zip_path"))

    return CourseGenerationResponse(
        course_id=course_id,
        title=result.get("title", title),
        lectures=lectures_summary,
        total_quizzes=len(result.get("quizzes", [])),
        moodle_export_url=moodle_url,
        pdf_url=pdf_url,
        lecture_pdf_urls=lecture_pdf_urls,
        zip_url=zip_url,
        created_at=datetime.utcnow()
    )


@router.get(
    "/download/{filename}"
)
async def download_file(
    filename: str
):

    # Security: prevent directory traversal
    if (
        ".." in filename
        or "/" in filename
        or "\\" in filename
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    # Search in output directory and its subdirectories
    for root, dirs, files in os.walk(settings.OUTPUT_DIR):
        if filename in files:
            return FileResponse(
                os.path.join(root, filename),
                filename=filename
            )

    raise HTTPException(
        status_code=404,
        detail="File not found"
    )
