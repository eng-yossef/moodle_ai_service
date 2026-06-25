from fpdf import FPDF
import os
import unicodedata
from typing import List, Dict, Any

from core.config import settings


class PDFService:

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Remove unsupported unicode characters for FPDF.
        """

        if not text:
            return ""

        replacements = {
            "•": "-",
            "–": "-",
            "—": "-",
            "“": '"',
            "”": '"',
            "‘": "'",
            "’": "'",
            "≤": "<=",
            "≥": ">=",
            "≠": "!=",
            "≈": "~",
            "√": "sqrt",
            "°": " degrees ",
            "μ": "micro",
            "α": "alpha",
            "β": "beta",
            "γ": "gamma",
            "Δ": "delta",
            "∫": "integral",
            "∞": "infinity"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = unicodedata.normalize("NFKD", text)

        text = text.encode(
            "latin-1",
            "ignore"
        ).decode(
            "latin-1"
        )

        return text

    def generate_course_pdf(
        self,
        course_title: str,
        lectures: List[Dict[str, Any]],
        include_quizzes: bool = True,
        quizzes: List[List[Dict[str, Any]]] = None
    ) -> str:

        output_dir = settings.OUTPUT_DIR

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        pdf = FPDF()

        pdf.set_auto_page_break(
            auto=True,
            margin=15
        )

        pdf.add_page()

        # --------------------------------------------------
        # Cover Page
        # --------------------------------------------------

        pdf.set_font(
            "Arial",
            "B",
            22
        )

        pdf.cell(
            0,
            12,
            self.clean_text(course_title),
            ln=True,
            align="C"
        )

        pdf.ln(15)

        # --------------------------------------------------
        # Table of Contents
        # --------------------------------------------------

        pdf.set_font(
            "Arial",
            "B",
            16
        )

        pdf.cell(
            0,
            10,
            "Table of Contents",
            ln=True
        )

        pdf.ln(5)

        pdf.set_font(
            "Arial",
            "",
            12
        )

        for idx, lecture in enumerate(
            lectures,
            start=1
        ):
            pdf.cell(
                0,
                8,
                self.clean_text(
                    f"Lecture {idx}: {lecture['title']}"
                ),
                ln=True
            )

        # --------------------------------------------------
        # Lecture Pages
        # --------------------------------------------------

        for idx, lecture in enumerate(
            lectures,
            start=1
        ):

            pdf.add_page()

            pdf.set_font(
                "Arial",
                "B",
                18
            )

            pdf.multi_cell(
                0,
                10,
                self.clean_text(
                    f"Lecture {idx}: {lecture['title']}"
                )
            )

            pdf.ln(5)

            pdf.set_font(
                "Arial",
                "",
                12
            )

            content = self.clean_text(
                lecture.get(
                    "content",
                    ""
                )
            )

            for paragraph in content.split("\n"):

                paragraph = paragraph.strip()

                if not paragraph:
                    continue

                pdf.multi_cell(
                    0,
                    6,
                    paragraph
                )

                pdf.ln(2)

            # ----------------------------------------------
            # Quiz Section
            # ----------------------------------------------

            if (
                include_quizzes
                and quizzes
                and idx - 1 < len(quizzes)
            ):

                pdf.ln(5)

                pdf.set_font(
                    "Arial",
                    "B",
                    14
                )

                pdf.cell(
                    0,
                    10,
                    "Quiz Questions",
                    ln=True
                )

                pdf.set_font(
                    "Arial",
                    "",
                    12
                )

                for q_idx, question in enumerate(
                    quizzes[idx - 1],
                    start=1
                ):

                    pdf.multi_cell(
                        0,
                        6,
                        self.clean_text(
                            f"{q_idx}. {question['question']}"
                        )
                    )

                    pdf.ln(2)

                    for option in question["options"]:

                        pdf.multi_cell(
                            0,
                            6,
                            self.clean_text(
                                f"  - {option}"
                            )
                        )

                    pdf.ln(1)

                    pdf.multi_cell(
                        0,
                        6,
                        self.clean_text(
                            f"Correct Answer: {question['correct_answer']}"
                        )
                    )

                    pdf.ln(3)

        filename = os.path.join(
            output_dir,
            f"{course_title.replace(' ', '_')}_course_material.pdf"
        )

        pdf.output(filename)

        return filename