from utils.pdf_utils import extract_text_from_pdf
from utils.ppt_utils import extract_text_from_ppt
from utils.file_utils import save_uploaded_file, delete_file

class DocumentService:
    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        ext = filename.lower().split('.')[-1]
        if ext in ['pdf']:
            return extract_text_from_pdf(file_bytes)
        elif ext in ['ppt', 'pptx']:
            return extract_text_from_ppt(file_bytes)
        else:
            raise ValueError("Unsupported file format. Use PDF or PowerPoint.")

    def save_file(self, file_bytes: bytes, filename: str) -> str:
        return save_uploaded_file(file_bytes, filename)

    def delete_file(self, filepath: str):
        delete_file(filepath)