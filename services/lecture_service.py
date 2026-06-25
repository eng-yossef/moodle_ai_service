from typing import List, Dict, Any
import json

class LectureService:
    def create_lecture(self, title: str, content: str, order: int) -> Dict[str, Any]:
        return {
            "id": f"lec_{order}",
            "title": title,
            "content": content,
            "order": order
        }

    def save_lectures(self, lectures: List[Dict[str, Any]], course_id: str) -> str:
        # In production, save to DB or file; here we store as JSON in outputs
        import os
        from core.config import settings
        output_file = os.path.join(settings.OUTPUT_DIR, f"{course_id}_lectures.json")
        with open(output_file, "w") as f:
            json.dump(lectures, f, indent=2)
        return output_file

    def load_lectures(self, course_id: str) -> List[Dict[str, Any]]:
        import os
        from core.config import settings
        filepath = os.path.join(settings.OUTPUT_DIR, f"{course_id}_lectures.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
        return []