import xml.etree.ElementTree as ET
import os
from html import escape
from core.config import settings

class MoodleExportService:
    def generate_xml(self, course_title: str, lectures: list, quizzes: list) -> str:
        """
        Build a valid Moodle XML file.
        Root element: <quiz>
        Each question is a <question type="multichoice"> with all required fields.
        """
        root = ET.Element("quiz")

        question_number = 0  # global question counter for unique names

        for i, lecture in enumerate(lectures):
            # If there are questions for this lecture, add them
            if i < len(quizzes) and quizzes[i]:
                # Optional: wrap all questions of a lecture in a <category>
                # But this is not required; you can also just put questions directly under <quiz>
                # Using category helps organize in Moodle.
                category = ET.SubElement(root, "category")
                cat_name = ET.SubElement(category, "text")
                cat_name.text = f"Lecture {i+1}: {lecture['title']}"

                for q in quizzes[i]:
                    question_number += 1

                    # Create question element
                    question = ET.SubElement(root, "question", type="multichoice")

                    # 1. Name (unique short identifier) – often a number
                    name = ET.SubElement(question, "name")
                    ET.SubElement(name, "text").text = f"Q{question_number}"

                    # 2. Question text with HTML format
                    qtext = ET.SubElement(question, "questiontext", format="html")
                    text_elem = ET.SubElement(qtext, "text")
                    # Use CDATA to safely embed any characters
                    text_elem.text = f"<![CDATA[{q['question']}]]>"

                    # 3. Standard fields
                    ET.SubElement(question, "defaultgrade").text = "1.0000000"
                    ET.SubElement(question, "penalty").text = "0.3333333"
                    ET.SubElement(question, "hidden").text = "0"
                    ET.SubElement(question, "single").text = "true"       # single answer
                    ET.SubElement(question, "shuffleanswers").text = "true"
                    ET.SubElement(question, "answernumbering").text = "abc"

                    # 4. Answers
                    correct_answer = q['correct_answer']
                    for opt in q['options']:
                        answer = ET.SubElement(question, "answer",
                                               fraction="100" if opt == correct_answer else "0")
                        ans_text = ET.SubElement(answer, "text")
                        ans_text.text = opt
                        # Optional feedback
                        feedback = ET.SubElement(answer, "feedback")
                        fb_text = ET.SubElement(feedback, "text")
                        fb_text.text = "Correct!" if opt == correct_answer else "Incorrect."

        # Convert to pretty‑printed XML, fixing CDATA escaping
        rough = ET.tostring(root, encoding='unicode')
        # ET escapes < and >, so we need to restore CDATA markers
        rough = rough.replace("&lt;![CDATA[", "<![CDATA[").replace("]]&gt;", "]]>")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + rough

    def save_xml(self, xml_content: str, course_id: str) -> str:
        filepath = os.path.join(settings.OUTPUT_DIR, f"{course_id}_moodle.xml")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_content)
        return filepath