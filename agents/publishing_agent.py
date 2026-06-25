from typing import List, Dict, Any
from services.moodle_export_service import MoodleExportService
from services.pdf_service import PDFService

class PublishingAgent:
    def __init__(self):
        self.export_service = MoodleExportService()
        self.pdf_service = PDFService()

    def export_moodle(self, course_title: str, lectures: List[Dict[str, Any]], 
                      quizzes: List[List[Dict[str, Any]]]) -> str:
        return self.export_service.generate_xml(course_title, lectures, quizzes)

    def export_pdf(self, course_title: str, lectures: List[Dict[str, Any]], 
                   include_quizzes: bool = True, quizzes: List[List[Dict[str, Any]]] = None) -> str:
        return self.pdf_service.generate_course_pdf(course_title, lectures, include_quizzes, quizzes)