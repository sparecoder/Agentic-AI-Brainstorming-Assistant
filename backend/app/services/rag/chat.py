"""KB Chat Service — conversational RAG logic for answering questions about uploaded docs."""

import logging
from typing import List, Dict
from app.services.llm import call_llm
from app.services.rag.vectorstore import search

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful Knowledge Assistant. Your job is to answer the user's questions based EXCLUSIVELY on the provided research and context from their uploaded documents.

If the answer is not contained in the context, tell the user politely that you don't have that information in your knowledge base yet.

Context from Documents:
{context}

Rules:
1. Use only the provided context.
2. Be concise but thorough.
3. Cite the source name if available.
4. If the question is general and not related to the context, remind the user you are here to help with their documents."""

def chat_kb(query: str) -> Dict:
    """Answer a query using retrieved context from the Knowledge Base."""
    logger.info(f"KB Chat: Answering query '{query[:50]}...'")
    
    # 1. Retrieve context
    results = search(query, k=5)
    
    if not results:
        return {
            "answer": "I couldn't find any relevant information in your Knowledge Base. Please try uploading more documents or rephrasing your question.",
            "sources": []
        }
    
    # 2. Formulate context string
    context_str = "\n\n".join([
        f"--- Source: {res['source']} ---\n{res['content']}" 
        for res in results
    ])
    
    # 3. Call LLM
    prompt = f"User Question: {query}"
    system = SYSTEM_PROMPT.format(context=context_str)
    
    # Use call_llm but since it expects JSON, we need to adapt it or use a simpler helper
    # For simplicity, we'll use a version that expects a 'response' field
    chat_system = system + "\n\nReturn your answer in a JSON object: {\"answer\": \"your explanation here\"}"
    
    try:
        response = call_llm(chat_system, prompt)
        answer = response.get("answer", "I encountered an error formulating the answer.")
    except Exception as e:
        logger.error(f"Chat KB LLM error: {e}")
        answer = "I'm sorry, I had trouble processing that request via the AI."

    return {
        "answer": answer,
        "sources": list(set([res['source'] for res in results]))
    }
