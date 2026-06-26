"""
routers/ask_router.py

POST /ask endpoint.

Full pipeline when a file is uploaded:
  1. DocumentService  → extract text from PDF/PPT/TXT
  2. DocumentService  → chunk the text
  3. EmbeddingService → build ephemeral FAISS index, retrieve top-k chunks
  4. llm_service      → ask_llm(question, context, history, file_context=chunks)
  5. markdown_utils   → convert markdown reply to HTML
  6. Return {"reply": html}

When no file is supplied the pipeline skips steps 1-3 and calls ask_llm
with an empty file_context (original behaviour).
"""

import logging
from typing import Optional

from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from services.document_service  import DocumentService
from services.embedding_service import EmbeddingService
from services.llm_service       import ask_llm
from utils.markdown_utils       import to_html

logger = logging.getLogger(__name__)
router = APIRouter()

# Singletons — stateless, safe to reuse across requests
_doc_service = DocumentService()

# How many chunks to retrieve from FAISS and send to the LLM
TOP_K_CHUNKS = 5

# Maximum characters we pass to the LLM as file context
# (keeps the prompt within a reasonable token budget)
MAX_FILE_CONTEXT_CHARS = 6_000


@router.post("/ask")
async def ask(
    question:  str                    = Form(...),
    context:   str                    = Form(""),
    history:   str                    = Form(""),
    # ── Binary file upload (PDF, PPTX, …) sent by PHP via CURLFile ──────────
    file:      Optional[UploadFile]   = File(None),
    # ── Plain-text fallback (PHP decoded TXT/HTML before sending) ───────────
    file_text: Optional[str]          = Form(""),
    file_name: Optional[str]          = Form(""),
) -> JSONResponse:
    """
    Accepts a question (and optional course context / history / file) and
    returns an HTML-formatted AI reply.
    """

    file_context = ""

    # ── Path A: real file upload ─────────────────────────────────────────────
    if file is not None and file.filename:
        try:
            file_bytes = await file.read()
            filename   = file.filename

            # 1. Extract text
            raw_text = _doc_service.extract_text(file_bytes, filename)

            # 2. Chunk
            chunks = _doc_service.chunk_text(raw_text)

            if chunks:
                # 3. Build ephemeral FAISS index + retrieve top-k chunks
                emb_service  = EmbeddingService(chunks)
                top_chunks   = emb_service.search(question, k=TOP_K_CHUNKS)

                # 4. Join and truncate for the LLM prompt
                joined = "\n\n---\n\n".join(top_chunks)
                file_context = (
                    f"[Source: {filename}]\n\n"
                    + joined[:MAX_FILE_CONTEXT_CHARS]
                )
            else:
                logger.warning("No chunks extracted from file: %s", filename)

        except ValueError as exc:
            # Unsupported file type — not a server error, tell the LLM
            logger.warning("Unsupported file type: %s", exc)
            file_context = f"[File upload skipped: {exc}]"

        except Exception as exc:
            logger.error("File processing error: %s", exc, exc_info=True)
            raise HTTPException(status_code=500, detail="File processing failed.")

    # ── Path B: plain-text content pre-decoded by PHP ────────────────────────
    elif file_text:
        label = file_name or "material"
        # Chunk even plain-text so we only send the most relevant parts
        chunks = _doc_service.chunk_text(file_text)

        if chunks:
            emb_service  = EmbeddingService(chunks)
            top_chunks   = emb_service.search(question, k=TOP_K_CHUNKS)
            joined       = "\n\n---\n\n".join(top_chunks)
            file_context = (
                f"[Source: {label}]\n\n"
                + joined[:MAX_FILE_CONTEXT_CHARS]
            )
        else:
            file_context = file_text[:MAX_FILE_CONTEXT_CHARS]

    # ── Call the LLM ─────────────────────────────────────────────────────────
    reply_text = ask_llm(
        question     = question,
        context      = context,
        history      = history,
        file_context = file_context,
    )

    reply_html = to_html(reply_text)
    return JSONResponse(content={"reply": reply_html})