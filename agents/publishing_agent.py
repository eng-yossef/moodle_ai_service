from typing import List, Dict, Any, Optional
from services.moodle_export_service import MoodleExportService
from services.pdf_service import PDFService
import os
from core.config import settings

class PublishingAgent:
    def __init__(self):
        self.export_service = MoodleExportService()
        self.pdf_service = PDFService()

    def export_moodle(self, course_title: str, lectures: List[Dict[str, Any]], 
                      quizzes: List[List[Dict[str, Any]]]) -> str:
        return self.export_service.generate_xml(course_title, lectures, quizzes)

    def export_pdf(self, course_id: str, course_title: str, 
                   lectures: List[Dict[str, Any]], 
                   include_quizzes: bool = True, 
                   quizzes: List[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate complete course PDF, individual lecture PDFs, and a ZIP package.
        Returns dict with paths.
        """
        # 1. Complete course PDF
        course_pdf = self.pdf_service.generate_course_pdf(
            course_title, lectures, include_quizzes, quizzes
        )

        # 2. Individual lecture PDFs
        lecture_pdfs = self.pdf_service.generate_all_lecture_pdfs(
            course_id, lectures, quizzes
        )

        # 3. Save Moodle XML to file (needed for ZIP)
        moodle_xml_str = self.export_service.generate_xml(course_title, lectures, quizzes)
        course_folder = os.path.join(settings.OUTPUT_DIR, course_id)
        os.makedirs(course_folder, exist_ok=True)
        moodle_xml_path = os.path.join(course_folder, f"{course_id}_moodle.xml")
        with open(moodle_xml_path, "w") as f:
            f.write(moodle_xml_str)

        # 4. Create ZIP package
        zip_path = self.pdf_service.create_zip_package(
            course_id, course_title, course_pdf, lecture_pdfs, moodle_xml_path
        )

        return {
            "course_pdf": course_pdf,
            "lecture_pdfs": lecture_pdfs,
            "moodle_xml": moodle_xml_str,
            "moodle_xml_path": moodle_xml_path,
            "zip_path": zip_path
        }