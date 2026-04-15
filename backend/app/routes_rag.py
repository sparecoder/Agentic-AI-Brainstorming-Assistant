"""RAG API routes — document upload, list, and deletion."""

import os
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session as DBSession

from app.config import get_settings
from app.database import get_db
from app.models import Document
from app.schemas import DocumentResponse, DocumentUploadResponse, KBChatRequest, KBChatResponse
from app.services.rag.ingest import ingest_pdf
from app.services.rag.vectorstore import delete_by_source, get_stats
from app.services.rag.chat import chat_kb

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), db: DBSession = Depends(get_db)):
    """Upload a PDF document for RAG ingestion."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Save file to disk
    file_path = os.path.join(settings.upload_dir, file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        # Check if document already exists
        existing = db.query(Document).filter(Document.source_name == file.filename).first()
        if existing:
            # Delete old vectors and DB entry, re-ingest
            delete_by_source(file.filename)
            db.delete(existing)
            db.flush()

        # Ingest into vector store
        result = ingest_pdf(file_path, source_name=file.filename)

        # Save metadata to DB
        doc = Document(
            filename=file.filename,
            source_name=file.filename,
            file_size=len(content),
            total_chunks=result["total_chunks"],
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        return DocumentUploadResponse(
            document=DocumentResponse(
                id=doc.id, filename=doc.filename, source_name=doc.source_name,
                file_size=doc.file_size, total_chunks=doc.total_chunks,
                uploaded_at=doc.uploaded_at,
            ),
            message=f"Successfully ingested {result['total_chunks']} chunks from {file.filename}",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Document upload failed: {e}")
        # Clean up the file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(db: DBSession = Depends(get_db)):
    """List all uploaded documents."""
    docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return [
        DocumentResponse(
            id=d.id, filename=d.filename, source_name=d.source_name,
            file_size=d.file_size, total_chunks=d.total_chunks,
            uploaded_at=d.uploaded_at,
        )
        for d in docs
    ]


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: DBSession = Depends(get_db)):
    """Delete a document and its vector store entries."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from vector store
    delete_by_source(doc.source_name)

    # Delete file from disk
    settings = get_settings()
    file_path = os.path.join(settings.upload_dir, doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete DB record
    db.delete(doc)
    db.commit()

    return {"message": f"Deleted document: {doc.filename}"}


@router.get("/documents/stats")
def document_stats():
    """Get vector store statistics."""
    return get_stats()


@router.post("/chat-kb", response_model=KBChatResponse)
def kb_chat_endpoint(req: KBChatRequest):
    """Chat with the Knowledge Base using RAG."""
    result = chat_kb(req.message)
    return KBChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
