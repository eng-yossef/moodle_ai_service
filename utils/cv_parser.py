import io
import docx2txt
from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
from core.config import *

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from a PDF or DOCX file."""
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        text = " ".join(page.extract_text() or "" for page in reader.pages)
        return text.strip()
    elif filename.lower().endswith(".docx"):
        return docx2txt.process(io.BytesIO(file_bytes)).strip()
    else:
        raise ValueError("Unsupported file format. Please upload PDF or DOCX.")

def parse_cv_with_llm(cv_text: str) -> Dict[str, Any]:
    """Use an LLM to extract structured information from CV text."""
    prompt = ChatPromptTemplate.from_template(
        """You are a CV parser. Extract the following information from the CV text below.
Return a JSON with keys: "skills" (list of strings), "experience" (list of dicts with "title", "company", "years"), "education" (list of dicts with "degree", "field", "institution"), "projects" (list of dicts with "name", "description").

CV Text:
{cv_text}

JSON output:"""
    )
    llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    max_tokens=1000,
    api_key="REMOVED_OPENROUTER_KEY"
)

    chain = prompt | llm
    response = chain.invoke({"cv_text": cv_text})
    # Parse the response (assuming it's valid JSON)
    import json
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback: return raw string if parsing fails
        return {"raw_cv": cv_text, "error": "Could not parse structured data"}