def generate_lecture_prompt(full_text: str, lecture_title: str, lecture_summary: str, course_title: str) -> str:
    return f"""
You are an instructional designer. You are creating a lecture for a course titled "{course_title}".
The lecture is titled "{lecture_title}" and should cover: {lecture_summary}.

Using the reference material provided below, generate a comprehensive lecture that explains the key concepts, 
provides examples, and is structured clearly. The lecture should be self‑contained and suitable for students.

Reference material:
{full_text}

Return the lecture content as a coherent text with proper headings, paragraphs, and possibly bullet points.
"""