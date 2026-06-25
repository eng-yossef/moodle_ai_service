def generate_curriculum_prompt(text: str, num_lectures: int, course_title: str, course_description: str = "") -> str:
    return f"""
You are an expert curriculum designer. Given the reference material for a course titled "{course_title}", 
create a logical division into exactly {num_lectures} lectures. Each lecture should cover a distinct topic 
that flows naturally and covers the essential content.

For each lecture, provide:
- Title (concise and descriptive)
- A brief summary (2‑3 sentences) of what will be covered

Return the result as a JSON array of objects with keys: "title", "summary".

Reference material:
{text}
"""