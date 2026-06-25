import xml.etree.ElementTree as ET
import os
from core.config import settings

class MoodleExportService:
    def generate_xml(self, course_title: str, lectures: list, quizzes: list) -> str:
        # Build Moodle XML (simplified)
        root = ET.Element("quiz")
        # Add course info
        for i, lecture in enumerate(lectures):
            # Add a category for each lecture
            category = ET.SubElement(root, "category")
            ET.SubElement(category, "name").text = f"Lecture {i+1}: {lecture['title']}"
            # Add questions
            if i < len(quizzes):
                for q in quizzes[i]:
                    question = ET.SubElement(category, "question", type="multichoice")
                    ET.SubElement(question, "name").text = q['question'][:50]
                    ET.SubElement(question, "questiontext").text = q['question']
                    for opt in q['options']:
                        answer = ET.SubElement(question, "answer", fraction="100" if opt == q['correct_answer'] else "0")
                        ET.SubElement(answer, "text").text = opt
        return ET.tostring(root, encoding='unicode')

    def save_xml(self, xml_content: str, course_id: str) -> str:
        filepath = os.path.join(settings.OUTPUT_DIR, f"{course_id}_moodle.xml")
        with open(filepath, "w") as f:
            f.write(xml_content)
        return filepath