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

    def _sanitize_text(self, text: str) -> str:
        replacements = {
            '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"',
            '\u2013': '-', '\u2014': '-',
            '\u2026': '...', '\u00a0': ' ',
            '\u00e9': 'e', '\u00e8': 'e',
            '\u00e0': 'a', '\u00f4': 'o',
            '\u00e7': 'c', '\u00e2': 'a',
            '\u00ea': 'e', '\u00ee': 'i',
            '\u00f6': 'o', '\u00fc': 'u',
            '\u00df': 'ss',
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    def _get_effective_width(self, pdf: FPDF, indent: float = 0) -> float:
        """Return the available width for text after indentation and margins."""
        return pdf.w - pdf.l_margin - pdf.r_margin - indent

    def _render_markdown(self, pdf: FPDF, text: str, font_size: int = 12):
        if not text:
            return
        sanitized = self._sanitize_text(text)
        html = markdown.markdown(sanitized, extensions=['extra'])
        pdf.set_font("helvetica", size=font_size)
        pdf.write_html(html)

    def generate_course_pdf(self, course_title: str, lectures: List[Dict[str, Any]], 
                            include_quizzes: bool = True, quizzes: List[List[Dict[str, Any]]] = None) -> str:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("helvetica", "B", 20)
        pdf.cell(0, 10, self._sanitize_text(course_title), ln=True, align='C')
        pdf.ln(10)

        # Table of contents
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "Table of Contents", ln=True)
        pdf.set_font("helvetica", "", 12)
        for idx, lecture in enumerate(lectures, start=1):
            pdf.cell(0, 8, f"Lecture {idx}: {self._sanitize_text(lecture['title'])}", ln=True)
        pdf.ln(10)

        # Lectures
        for idx, lecture in enumerate(lectures, start=1):
            pdf.add_page()
            pdf.set_font("helvetica", "B", 18)
            pdf.cell(0, 10, f"Lecture {idx}: {self._sanitize_text(lecture['title'])}", ln=True)
            pdf.ln(5)
            self._render_markdown(pdf, lecture.get('content', ''), font_size=12)
            pdf.ln(5)

            # Quiz
            if include_quizzes and quizzes and idx - 1 < len(quizzes):
                pdf.set_font("helvetica", "B", 14)
                pdf.cell(0, 10, "Quiz Questions", ln=True)
                pdf.ln(3)
                for q_idx, q in enumerate(quizzes[idx - 1], start=1):
                    pdf.set_font("helvetica", "B", 12)
                    pdf.multi_cell(0, 6, f"Q{q_idx}: {self._sanitize_text(q['question'])}")
                    pdf.set_font("helvetica", "", 12)
                    # Options with indentation
                    indent = 10
                    available_width = self._get_effective_width(pdf, indent)
                    for opt in q['options']:
                        pdf.set_x(pdf.l_margin + indent)
                        pdf.multi_cell(available_width, 6, f"  - {self._sanitize_text(opt)}")
                    pdf.ln(2)
                    pdf.set_text_color(0, 128, 0)
                    pdf.multi_cell(0, 6, f"  Correct: {self._sanitize_text(q['correct_answer'])}")
                    pdf.set_text_color(0, 0, 0)
                    pdf.ln(4)

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
        pdf.set_font("helvetica", "B", 18)
        pdf.cell(0, 10, self._sanitize_text(lecture['title']), ln=True, align='C')
        pdf.ln(5)

        # Content
        self._render_markdown(pdf, lecture.get('content', ''), font_size=12)
        pdf.ln(5)

        # Quiz
        if quiz:
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "Quiz Questions", ln=True)
            pdf.ln(3)
            for q_idx, q in enumerate(quiz, start=1):
                pdf.set_font("helvetica", "B", 12)
                pdf.multi_cell(0, 6, f"Q{q_idx}: {self._sanitize_text(q['question'])}")
                pdf.set_font("helvetica", "", 12)
                indent = 10
                available_width = self._get_effective_width(pdf, indent)
                for opt in q['options']:
                    pdf.set_x(pdf.l_margin + indent)
                    pdf.multi_cell(available_width, 6, f"  - {self._sanitize_text(opt)}")
                pdf.ln(2)
                pdf.set_text_color(0, 128, 0)
                pdf.multi_cell(0, 6, f"  Correct: {self._sanitize_text(q['correct_answer'])}")
                pdf.set_text_color(0, 0, 0)
                pdf.ln(4)

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