"""Shared LLM client — Groq connections reused across all agents."""

import json
import logging
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_settings

logger = logging.getLogger(__name__)

# Model constants
MODEL_FAST = "llama-3.1-8b-instant"
MODEL_SMART = "llama-3.3-70b-versatile"

_models = {}

def get_llm(model_id: Optional[str] = None) -> ChatGroq:
    """Lazily create and cache specific Groq LLM clients."""
    global _models
    s = get_settings()
    
    # Default to config or MODEL_SMART if not specified
    model_id = model_id or s.groq_model or MODEL_SMART
    
    if model_id not in _models:
        logger.info(f"Initializing LLM client for model: {model_id}")
        _models[model_id] = ChatGroq(
            api_key=s.groq_api_key,
            model=model_id,
            temperature=0.8,
            max_tokens=4096,
        )
    return _models[model_id]


def call_llm(system: str, user: str, model_id: Optional[str] = None) -> dict:
    """Call Groq in JSON mode and parse the response using a specific model."""
    llm = get_llm(model_id)
    msgs = [SystemMessage(content=system), HumanMessage(content=user)]
    
    # Bind response format and invoke
    resp = llm.bind(response_format={"type": "json_object"}).invoke(msgs)
    text = resp.content
    logger.info(f"LLM Response ({model_id or 'default'}): {len(text)} chars")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback for minor formatting issues
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text.strip())
