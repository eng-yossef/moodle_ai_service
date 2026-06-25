from pydantic import BaseModel, Field
from typing import Optional

class CourseGenerationRequest(BaseModel):
    title: str = Field(..., description="Course title")
    description: Optional[str] = Field(None, description="Course description")
    num_lectures: Optional[int] = Field(5, ge=1, le=20, description="Desired number of lectures")
    include_quizzes: bool = Field(True, description="Generate quizzes for each lecture")
    moodle_export: bool = Field(True, description="Export to Moodle XML format")