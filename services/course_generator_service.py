from typing import Dict, Any
from models.state import CourseState
from agents.document_analysis_agent import DocumentAnalysisAgent
from agents.curriculum_agent import CurriculumAgent
from agents.lecture_generation_agent import LectureGenerationAgent
from agents.assessment_agent import AssessmentAgent
from agents.publishing_agent import PublishingAgent

class CourseGeneratorService:
    def __init__(self, 
                 doc_agent: DocumentAnalysisAgent,
                 cur_agent: CurriculumAgent,
                 lec_agent: LectureGenerationAgent,
                 ass_agent: AssessmentAgent,
                 pub_agent: PublishingAgent):
        self.doc_agent = doc_agent
        self.cur_agent = cur_agent
        self.lec_agent = lec_agent
        self.ass_agent = ass_agent
        self.pub_agent = pub_agent

    async def generate_course(self, request_data: Dict[str, Any], file_bytes: bytes, filename: str) -> Dict[str, Any]:
        state = CourseState(
            course_id=request_data.get("course_id", "default"),
            title=request_data.get("title", "Untitled Course"),
            description=request_data.get("description", "")
        )
        # Step 1: Extract text
        state.raw_text = self.doc_agent.extract_text(file_bytes, filename)

        # Step 2: Generate curriculum
        num_lectures = request_data.get("num_lectures", 5)
        state.curriculum = self.cur_agent.generate_curriculum(
            state.raw_text, num_lectures, state.title, state.description
        )

        # Step 3: Generate lectures
        state.lectures = self.lec_agent.generate_lectures(state.curriculum, state.raw_text, state.title)

        # Step 4: Generate quizzes
        include_quizzes = request_data.get("include_quizzes", True)
        if include_quizzes:
            state.quizzes = self.ass_agent.generate_quizzes(state.lectures)

        # Step 5: Export all artifacts (PDFs + Moodle XML + ZIP)
        export_result = self.pub_agent.export_pdf(
            state.course_id,
            state.title,
            state.lectures,
            include_quizzes,
            state.quizzes
        )
        state.pdf_path = export_result["course_pdf"]
        state.lecture_pdf_paths = export_result["lecture_pdfs"]
        state.moodle_xml = export_result["moodle_xml"]
        state.zip_path = export_result["zip_path"]

        state.completed = True
        return state.dict()