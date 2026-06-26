from utils.pdf_utils import extract_text_from_pdf
from utils.ppt_utils import extract_text_from_ppt
from utils.file_utils import save_uploaded_file, delete_file

"""
services/document_service.py

Responsibilities:
  1. Extract raw text from uploaded files (PDF, PPT/PPTX, plain-text).
  2. Split the text into overlapping chunks suitable for embedding + retrieval.
"""

class DocumentService:
    """Handles text extraction and chunking for uploaded course materials."""

    # ── Chunking defaults ────────────────────────────────────────────────────
    DEFAULT_CHUNK_SIZE    = 500   # characters per chunk
    DEFAULT_CHUNK_OVERLAP = 100   # characters of overlap between adjacent chunks

    # ── Text extraction ──────────────────────────────────────────────────────

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """
        Dispatch to the correct extractor based on file extension.

        Supported formats:
          • PDF  → pypdf
          • PPT / PPTX → python-pptx
          • TXT / plain text → decoded directly

        Raises ValueError for unsupported formats.
        """
        ext = filename.lower().rsplit(".", 1)[-1]

        if ext == "pdf":
            return extract_text_from_pdf(file_bytes)
        elif ext in ("ppt", "pptx"):
            return extract_text_from_ppt(file_bytes)
        elif ext in ("txt", "md", "csv", "html", "htm"):
            try:
                return file_bytes.decode("utf-8", errors="replace")
            except Exception as e:
                raise ValueError(f"Could not decode text file: {e}")
        else:
            raise ValueError(
                f"Unsupported file format '{ext}'. "
                "Supported: PDF, PPT, PPTX, TXT, MD, CSV, HTML."
            )

    # ── Chunking ─────────────────────────────────────────────────────────────

    def chunk_text(
        self,
        text: str,
        chunk_size: int  = DEFAULT_CHUNK_SIZE,
        overlap: int     = DEFAULT_CHUNK_OVERLAP,
    ) -> list[str]:
        """
        Split *text* into overlapping character-level chunks.

        Strategy:
          • Try to break at the nearest sentence boundary ('. ') before the
            hard limit so chunks read naturally.
          • If no sentence boundary is found within the last 20 % of the chunk,
            fall back to the hard character limit.
          • Empty / whitespace-only chunks are discarded.

        Returns a list of non-empty string chunks.
        """
        text = text.strip()
        if not text:
            return []

        chunks = []
        start  = 0

        while start < len(text):
            end = start + chunk_size

            if end < len(text):
                # Try to find a sentence boundary in the last 20 % of the window
                search_from = start + int(chunk_size * 0.8)
                boundary    = text.rfind(". ", search_from, end)
                if boundary != -1:
                    end = boundary + 1  # include the period

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Advance with overlap
            start = end - overlap if end < len(text) else len(text)

        return chunks

    # ── Convenience: extract + chunk in one call ─────────────────────────────

    def extract_and_chunk(
        self,
        file_bytes: bytes,
        filename: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int    = DEFAULT_CHUNK_OVERLAP,
    ) -> list[str]:
        """
        Extract text from *file_bytes* and return a list of text chunks.
        Raises ValueError for unsupported file types.
        """
        raw_text = self.extract_text(file_bytes, filename)
        return self.chunk_text(raw_text, chunk_size=chunk_size, overlap=overlap)

    def save_file(self, file_bytes: bytes, filename: str) -> str:
        return save_uploaded_file(file_bytes, filename)

    def delete_file(self, filepath: str):
        delete_file(filepath)