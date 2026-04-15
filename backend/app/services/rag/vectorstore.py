"""ChromaDB Vector Store — persistent local vector database for RAG."""

import logging
from typing import List
import chromadb
from langchain_chroma import Chroma
from app.config import get_settings
from app.services.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)

_chroma_client = None
_collection = None
COLLECTION_NAME = "brainstorm_knowledge"


def _get_client():
    """Get or create the persistent ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        s = get_settings()
        _chroma_client = chromadb.PersistentClient(path=s.chroma_persist_dir)
        logger.info(f"ChromaDB initialized at: {s.chroma_persist_dir}")
    return _chroma_client


def _get_langchain_store() -> Chroma:
    """Get LangChain-compatible Chroma store."""
    s = get_settings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=s.chroma_persist_dir,
    )


def add_documents(texts: List[str], metadatas: List[dict] = None, ids: List[str] = None):
    """Add text chunks to the vector store."""
    store = _get_langchain_store()
    store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    logger.info(f"Added {len(texts)} chunks to vector store")


def search(query: str, k: int = 5) -> List[dict]:
    """Search for relevant documents by semantic similarity.

    Returns list of {"content": str, "source": str, "score": float}.
    """
    store = _get_langchain_store()

    try:
        results = store.similarity_search_with_relevance_scores(query, k=k)
    except Exception as e:
        logger.warning(f"Vector search failed: {e}")
        return []

    docs = []
    for doc, score in results:
        docs.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page", None),
            "score": round(score, 3),
        })

    logger.info(f"Vector search: {len(docs)} results for '{query[:50]}...'")
    return docs


def get_stats() -> dict:
    """Get collection statistics."""
    try:
        client = _get_client()
        collection = client.get_or_create_collection(COLLECTION_NAME)
        return {"collection": COLLECTION_NAME, "count": collection.count()}
    except Exception:
        return {"collection": COLLECTION_NAME, "count": 0}


def delete_by_source(source: str):
    """Delete all chunks from a specific source document."""
    try:
        client = _get_client()
        collection = client.get_or_create_collection(COLLECTION_NAME)
        # Get IDs with matching source metadata
        results = collection.get(where={"source": source})
        if results["ids"]:
            collection.delete(ids=results["ids"])
            logger.info(f"Deleted {len(results['ids'])} chunks from source: {source}")
    except Exception as e:
        logger.error(f"Failed to delete from source {source}: {e}")
