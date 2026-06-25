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
        # Initialize state
        state = CourseState(
            course_id=request_data.get("course_id", "default"),
            title=request_data.get("title", "Untitled Course"),
            description=request_data.get("description", "")
        )
        # Step 1: Extract text from document
        state.raw_text = self.doc_agent.extract_text(file_bytes, filename)

        # Step 2: Generate a logical curriculum (list of lecture topics)
        num_lectures = request_data.get("num_lectures", 5)
        curriculum = self.cur_agent.generate_curriculum(
            state.raw_text,
            num_lectures,
            state.title,
            state.description
        )
        state.curriculum = curriculum

        # Step 3: Generate lecture content for each topic using the full text
        state.lectures = self.lec_agent.generate_lectures(curriculum, state.raw_text, state.title)

        # Step 4: Generate quizzes if requested
        if request_data.get("include_quizzes", True):
            state.quizzes = self.ass_agent.generate_quizzes(state.lectures)

        # Step 5: Export to Moodle XML if requested
        if request_data.get("moodle_export", True):
            state.moodle_xml = self.pub_agent.export_moodle(state.title, state.lectures, state.quizzes)

        # Step 6: Generate PDF course material
        include_quizzes = request_data.get("include_quizzes", True)
        pdf_path = self.pub_agent.export_pdf(
            state.title, 
            state.lectures, 
            include_quizzes, 
            state.quizzes if include_quizzes else None
        )
        state.pdf_path = pdf_path

        state.completed = True
        return state.dict()