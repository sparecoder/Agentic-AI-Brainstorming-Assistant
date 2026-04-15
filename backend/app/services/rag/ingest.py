"""Document Ingestion — PDF parsing, chunking, and embedding into ChromaDB."""

import os
import uuid
import logging
from typing import List
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.rag.vectorstore import add_documents

logger = logging.getLogger(__name__)

# Chunk config
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file."""
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())
    full_text = "\n\n".join(pages)
    logger.info(f"Extracted {len(full_text)} chars from {len(reader.pages)} pages")
    return full_text


def chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = _splitter.split_text(text)
    logger.info(f"Split into {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


def ingest_pdf(file_path: str, source_name: str) -> dict:
    """Full ingestion pipeline: PDF → text → chunks → embeddings → ChromaDB.

    Returns metadata about the ingestion.
    """
    logger.info(f"Ingesting PDF: {source_name} ({file_path})")

    # Extract text
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise ValueError("PDF contains no extractable text")

    # Chunk
    chunks = chunk_text(text)

    # Prepare metadata and IDs
    metadatas = [{"source": source_name, "chunk_index": i, "page": "all"} for i in range(len(chunks))]
    ids = [f"{source_name}_{uuid.uuid4().hex[:8]}" for _ in chunks]

    # Add to vector store
    add_documents(texts=chunks, metadatas=metadatas, ids=ids)

    result = {
        "source": source_name,
        "total_chars": len(text),
        "total_chunks": len(chunks),
        "chunk_size": CHUNK_SIZE,
    }
    logger.info(f"Ingestion complete: {result}")
    return result
