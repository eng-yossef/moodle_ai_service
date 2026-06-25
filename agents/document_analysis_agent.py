from services.document_service import DocumentService

class DocumentAnalysisAgent:
    def __init__(self):
        self.doc_service = DocumentService()

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        return self.doc_service.extract_text(file_bytes, filename)