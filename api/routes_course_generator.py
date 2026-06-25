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
    moodle_export: bool = Form(True),
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
                summary=lec.get(
                    "content",
                    ""
                )[:200]
            )
        )

    output_dir = Path("outputs")
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    moodle_url = None
    pdf_url = None

    # --------------------------------------------------
    # Moodle XML
    # --------------------------------------------------

    if result.get("moodle_xml"):

        xml_content = result["moodle_xml"]

        xml_filename = (
            f"{course_id}_moodle.xml"
        )

        xml_path = (
            output_dir /
            xml_filename
        )

        with open(
            xml_path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(xml_content)

        moodle_url = (
            f"/course/download/"
            f"{xml_filename}"
        )

    # --------------------------------------------------
    # PDF
    # --------------------------------------------------

    pdf_path = result.get("pdf_path")

    print(
        f"Generated PDF Path: "
        f"{pdf_path}"
    )

    if pdf_path:

        pdf_file = Path(pdf_path)

        if pdf_file.exists():

            pdf_url = (
                f"/course/download/"
                f"{pdf_file.name}"
            )

            print(
                f"PDF URL: {pdf_url}"
            )

        else:

            print(
                f"PDF not found: "
                f"{pdf_file}"
            )

    return CourseGenerationResponse(
        course_id=course_id,
        title=result.get(
            "title",
            title
        ),
        lectures=lectures_summary,
        total_quizzes=len(
            result.get(
                "quizzes",
                []
            )
        ),
        moodle_export_url=moodle_url,
        pdf_url=pdf_url,
        created_at=datetime.utcnow()
    )


@router.get(
    "/download/{filename}"
)
async def download_file(
    filename: str
):

    if (
        ".." in filename
        or "/" in filename
        or "\\" in filename
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    filepath = (
        Path("outputs")
        / filename
    )

    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return FileResponse(
        path=str(filepath),
        filename=filename
    )