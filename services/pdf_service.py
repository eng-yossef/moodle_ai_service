import os
import zipfile
import json
import markdown
from fpdf import FPDF
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.config import settings

class PDFService:
    def _sanitize_filename(self, name: str) -> str:
        return "".join(c for c in name if c.isalnum() or c in " _-").strip()

    def _render_markdown(self, pdf: FPDF, text: str, font_size: int = 12):
        """
        Convert markdown to HTML and render using fpdf2's write_html().
        This gives us headings, bold, lists, etc.
        """
        if not text:
            return
        html = markdown.markdown(text, extensions=['extra'])
        pdf.set_font("Arial", size=font_size)
        pdf.write_html(html)

    def _render_quiz(self, pdf: FPDF, quizzes_for_lecture: List[Dict[str, Any]]):
        """Render quiz questions for a lecture."""
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Quiz Questions", ln=True)
        pdf.ln(3)

        left_margin = pdf.l_margin

        for q_idx, q in enumerate(quizzes_for_lecture, start=1):
            # Question
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 6, f"Q{q_idx}: {q['question']}")

            # Options — indent by temporarily widening the left margin
            pdf.set_font("Arial", "", 12)
            for opt in q.get('options', []):
                pdf.set_left_margin(left_margin + 10)
                pdf.set_x(left_margin + 10)
                pdf.multi_cell(0, 6, f"- {opt}")
            pdf.set_left_margin(left_margin)
            pdf.set_x(left_margin)

            pdf.ln(2)

            # Correct answer
            pdf.set_text_color(0, 128, 0)
            pdf.set_font("Arial", "I", 12)
            pdf.multi_cell(0, 6, f"Correct: {q.get('correct_answer', '')}")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 12)
            pdf.ln(4)

    def generate_course_pdf(self, course_title: str, lectures: List[Dict[str, Any]],
                            include_quizzes: bool = True,
                            quizzes: List[List[Dict[str, Any]]] = None) -> str:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, course_title, ln=True, align='C')
        pdf.ln(10)

        # Table of contents
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Table of Contents", ln=True)
        pdf.set_font("Arial", "", 12)
        for idx, lecture in enumerate(lectures, start=1):
            pdf.cell(0, 8, f"Lecture {idx}: {lecture['title']}", ln=True)
        pdf.ln(10)

        # Lectures
        for idx, lecture in enumerate(lectures, start=1):
            pdf.add_page()
            pdf.set_font("Arial", "B", 18)
            pdf.cell(0, 10, f"Lecture {idx}: {lecture['title']}", ln=True)
            pdf.ln(5)

            # Render content with markdown
            self._render_markdown(pdf, lecture.get('content', ''), font_size=12)
            pdf.ln(5)

            # Quiz
            if include_quizzes and quizzes and idx - 1 < len(quizzes):
                self._render_quiz(pdf, quizzes[idx - 1])

        safe_title = self._sanitize_filename(course_title)
        filename = f"{settings.OUTPUT_DIR}/{safe_title}_complete_course.pdf"
        pdf.output(filename)
        return filename

    def generate_lecture_pdf(self, course_id: str, lecture: Dict[str, Any],
                             quiz: List[Dict[str, Any]] = None) -> str:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 10, lecture['title'], ln=True, align='C')
        pdf.ln(5)

        # Content with markdown
        self._render_markdown(pdf, lecture.get('content', ''), font_size=12)
        pdf.ln(5)

        # Quiz
        if quiz:
            self._render_quiz(pdf, quiz)

        course_folder = os.path.join(settings.OUTPUT_DIR, course_id)
        os.makedirs(course_folder, exist_ok=True)
        safe_title = self._sanitize_filename(lecture['title'])
        order = lecture.get('order', 0)
        filename = f"lecture_{order:02d}_{safe_title}.pdf"
        filepath = os.path.join(course_folder, filename)
        pdf.output(filepath)
        return filepath

    def generate_all_lecture_pdfs(self, course_id: str, lectures: List[Dict[str, Any]],
                                  quizzes: List[List[Dict[str, Any]]] = None) -> List[str]:
        paths = []
        for idx, lecture in enumerate(lectures):
            quiz = quizzes[idx] if quizzes and idx < len(quizzes) else []
            path = self.generate_lecture_pdf(course_id, lecture, quiz)
            paths.append(path)
        return paths

    def create_zip_package(self, course_id: str, course_title: str,
                           complete_pdf_path: str, lecture_pdf_paths: List[str],
                           moodle_xml_path: str) -> str:
        course_folder = os.path.join(settings.OUTPUT_DIR, course_id)
        os.makedirs(course_folder, exist_ok=True)
        zip_filename = f"{course_id}_package.zip"
        zip_path = os.path.join(course_folder, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(complete_pdf_path, os.path.basename(complete_pdf_path))
            for path in lecture_pdf_paths:
                zipf.write(path, os.path.basename(path))
            if moodle_xml_path and os.path.exists(moodle_xml_path):
                zipf.write(moodle_xml_path, os.path.basename(moodle_xml_path))
            metadata = {
                "course_id": course_id,
                "title": course_title,
                "total_lectures": len(lecture_pdf_paths),
                "generated_at": str(datetime.utcnow())
            }
            metadata_path = os.path.join(course_folder, "metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            zipf.write(metadata_path, "metadata.json")
            os.remove(metadata_path)
        return zip_path