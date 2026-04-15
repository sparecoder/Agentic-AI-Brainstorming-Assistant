"""Researcher Agent — RAG-enabled knowledge retrieval.

Queries the ChromaDB vector store for relevant passages based on the
planner's research questions and domain context. Returns grounding
information that the Ideator can use to generate informed ideas.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


def run(context: dict, rag_results: List[dict] = None) -> str:
    """Compile research context from RAG retrieval results.

    Args:
        context: Structured context from the Planner Agent.
        rag_results: List of {"content": str, "source": str} dicts from vector search.

    Returns:
        A formatted research brief string to inject into the Ideator prompt.
    """
    logger.info("Researcher Agent: Compiling research context...")

    research_questions = context.get("research_questions", [])
    domain = context.get("domain", "General")
    keywords = context.get("keywords", [])

    # Build research brief
    sections = []
    sections.append(f"## Domain Analysis: {domain}")
    sections.append(f"Keywords: {', '.join(keywords)}")

    if context.get("sub_domains"):
        sections.append(f"Sub-domains: {', '.join(context['sub_domains'])}")

    if context.get("constraints"):
        sections.append(f"Constraints: {', '.join(context['constraints'])}")

    if research_questions:
        sections.append("\n## Research Questions")
        for i, q in enumerate(research_questions, 1):
            sections.append(f"{i}. {q}")

    # Inject RAG-retrieved knowledge if available
    if rag_results:
        sections.append(f"\n## Retrieved Knowledge ({len(rag_results)} passages)")
        for i, doc in enumerate(rag_results, 1):
            content = doc.get("content", "")[:500]  # Truncate long passages
            source = doc.get("source", "unknown")
            sections.append(f"\n### Passage {i} (from: {source})")
            sections.append(content)
        logger.info(f"Researcher Agent: Injected {len(rag_results)} RAG passages")
    else:
        sections.append("\n## Retrieved Knowledge")
        sections.append("No domain-specific documents uploaded yet. Using general knowledge.")
        logger.info("Researcher Agent: No RAG data available, using general knowledge")

    return "\n".join(sections)
