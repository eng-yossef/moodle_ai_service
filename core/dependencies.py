from .config import settings
from services.document_service import DocumentService
from services.lecture_service import LectureService
from services.quiz_service import QuizService
from services.moodle_export_service import MoodleExportService
from services.course_generator_service import CourseGeneratorService
from agents.document_analysis_agent import DocumentAnalysisAgent
from agents.curriculum_agent import CurriculumAgent
from agents.lecture_generation_agent import LectureGenerationAgent
from agents.assessment_agent import AssessmentAgent
from agents.publishing_agent import PublishingAgent

def get_document_service() -> DocumentService:
    return DocumentService()

def get_lecture_service() -> LectureService:
    return LectureService()

def get_quiz_service() -> QuizService:
    return QuizService()

def get_moodle_export_service() -> MoodleExportService:
    return MoodleExportService()

def get_course_generator_service() -> CourseGeneratorService:
    # Wire up agents
    doc_agent = DocumentAnalysisAgent()
    cur_agent = CurriculumAgent()
    lec_agent = LectureGenerationAgent()
    ass_agent = AssessmentAgent()
    pub_agent = PublishingAgent()
    return CourseGeneratorService(
        doc_agent=doc_agent,
        cur_agent=cur_agent,
        lec_agent=lec_agent,
        ass_agent=ass_agent,
        pub_agent=pub_agent
    )