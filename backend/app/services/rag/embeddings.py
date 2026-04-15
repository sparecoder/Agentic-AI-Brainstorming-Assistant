"""Embedding model — HuggingFace sentence-transformers for vector operations."""

import logging
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import get_settings

logger = logging.getLogger(__name__)

_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Lazily create and cache the embedding model."""
    global _embeddings
    if _embeddings is None:
        s = get_settings()
        logger.info(f"Loading embedding model: {s.embedding_model}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=s.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("Embedding model loaded successfully")
    return _embeddings
