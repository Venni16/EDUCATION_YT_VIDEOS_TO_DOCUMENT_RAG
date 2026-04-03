"""
FastAPI AI Service — Main Entry Point
YouTube → Document RAG Pipeline

Endpoints:
  GET  /health          → health check
  POST /generate-doc    → full pipeline: transcript → document + PDF
"""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Services
from services.youtube_service import extract_youtube_data
from services.processing_service import process_transcript
from services.vector_service import VectorStore
from services.agent_service import run_agent_pipeline
from services.document_service import assemble_markdown
from services.pdf_service import generate_pdf

# ── Logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("app")

# ── Ensure static dirs exist ───────────────────────────────
PDF_DIR = Path(os.getenv("PDF_OUTPUT_DIR", "static/pdfs"))
PDF_DIR.mkdir(parents=True, exist_ok=True)


# ── Lifespan (startup / shutdown) ──────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load the embedding model on startup to avoid cold start on first request."""
    logger.info("🚀 AI Service starting up — pre-loading embedding model...")
    from services.vector_service import get_embedding_model
    get_embedding_model()
    logger.info("✅ Embedding model ready.")
    yield
    logger.info("🛑 AI Service shutting down.")


# ── App ────────────────────────────────────────────────────
app = FastAPI(
    title="YouTube → Document AI Service",
    description="Agentic RAG pipeline: YouTube URL → structured Markdown document + PDF",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated PDFs as static files at /static/pdfs/
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Request / Response Models ──────────────────────────────
class GenerateRequest(BaseModel):
    url: str  # YouTube URL


class GenerateResponse(BaseModel):
    video_id: str
    title: str
    thumbnail_url: str
    document: str       # Full Markdown document
    pdf_url: str        # Relative URL, e.g. /static/pdfs/abc123.pdf


# ── Endpoints ──────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """Health check — returns OK if the service is running."""
    return {"status": "ok", "service": "YouTube → Document AI Service"}


@app.post("/generate-doc", response_model=GenerateResponse, tags=["Pipeline"])
async def generate_document(request: GenerateRequest):
    """
    Full pipeline:
    1. Extract YouTube transcript + title
    2. Clean & chunk transcript
    3. Embed chunks → FAISS vector store
    4. Run ReAct agent (identify topics → write sections → abstract → conclusion)
    5. Assemble Markdown document
    6. Generate PDF
    7. Return { video_id, title, thumbnail_url, document, pdf_url }
    """
    url = request.url.strip()
    logger.info(f"📥 Received request for URL: {url}")

    # ── Step 1: Extract YouTube data ──
    try:
        yt_data = extract_youtube_data(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))

    video_id     = yt_data["video_id"]
    title        = yt_data["title"]
    transcript   = yt_data["transcript"]
    thumbnail    = yt_data["thumbnail_url"]

    logger.info(f"📄 Transcript length: {len(transcript)} chars")

    # ── Step 2: Process transcript ──
    chunks = process_transcript(transcript)
    if not chunks:
        raise HTTPException(status_code=422, detail="Transcript processing produced no chunks.")

    # ── Step 3: Build vector store ──
    vector_store = VectorStore()
    try:
        vector_store.build(chunks)
    except Exception as e:
        logger.error(f"Vector store build failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    # ── Step 4: Run agent pipeline ──
    try:
        agent_output = run_agent_pipeline(title, chunks, vector_store)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Agent pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent pipeline failed: {str(e)}")

    # ── Step 5: Assemble Markdown ──
    document = assemble_markdown(agent_output)

    # ── Step 6: Generate PDF ──
    try:
        pdf_url = generate_pdf(document, video_id)
    except Exception as e:
        logger.warning(f"PDF generation failed (non-fatal): {e}")
        pdf_url = ""   # PDF is optional — don't fail the whole request

    logger.info(f"✅ Document generated for '{title}' | PDF: {pdf_url}")

    return GenerateResponse(
        video_id=video_id,
        title=title,
        thumbnail_url=thumbnail,
        document=document,
        pdf_url=pdf_url,
    )
