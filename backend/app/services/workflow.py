"""LangGraph Workflow — Orchestrates the multi-agent brainstorming pipeline.

Flow: Planner → Researcher → Ideator → Dedup → Critic → Refiner
"""

import logging
from typing import Optional, List, Tuple, TypedDict, Annotated
from difflib import SequenceMatcher

from langgraph.graph import StateGraph, START, END
from sqlalchemy.orm import Session as DBSession

from app.models import Idea
from app.services.agents import planner, researcher, ideator, critic, refiner

logger = logging.getLogger(__name__)

# Lazy import to avoid circular deps / slow startup
_vectorstore = None


def _get_vectorstore():
    """Lazily import and return the RAG vector store."""
    global _vectorstore
    if _vectorstore is None:
        try:
            from app.services.rag.vectorstore import search
            _vectorstore = search
        except Exception:
            logger.warning("Vector store not available — RAG disabled")
            _vectorstore = lambda *a, **kw: []
    return _vectorstore


# ── Workflow State ──────────────────────────────────────────────────────────

class WorkflowState(TypedDict):
    """State carried through the LangGraph pipeline."""
    prompt: str
    difficulty: Optional[str]
    timeline: Optional[str]
    tech_preference: Optional[str]
    context: dict
    research_brief: str
    rag_results: list
    raw_ideas: list
    unique_ideas: list
    evaluations: list
    refined_ideas: list
    past_titles: list


# ── Graph Nodes ─────────────────────────────────────────────────────────────

def plan_node(state: WorkflowState) -> dict:
    """Node 1: Extract context via Planner Agent."""
    ctx = planner.run(
        state["prompt"], state.get("difficulty"),
        state.get("timeline"), state.get("tech_preference"),
    )
    return {"context": ctx}


def research_node(state: WorkflowState) -> dict:
    """Node 2: Retrieve RAG knowledge + compile research brief."""
    ctx = state["context"]
    search_fn = _get_vectorstore()

    # Build search query from context
    query = f"{ctx.get('domain', '')} {' '.join(ctx.get('keywords', []))}"
    rag_results = []
    
    try:
        # Avoid searching if query is too weak
        if len(query.strip()) > 3:
            rag_results = search_fn(query, k=5)
    except Exception as e:
        logger.error(f"RAG search critical failure: {e}")
        # Continue with empty results to avoid blocking
        rag_results = []

    brief = researcher.run(ctx, rag_results)
    return {"rag_results": rag_results, "research_brief": brief}


def ideate_node(state: WorkflowState) -> dict:
    """Node 3: Generate raw ideas via Ideator Agent."""
    ideas = ideator.run(state["context"], state["prompt"], state["research_brief"])
    return {"raw_ideas": ideas}


def dedup_node(state: WorkflowState) -> dict:
    """Node 4: Remove ideas too similar to past generations."""
    ideas = state["raw_ideas"]
    past = state.get("past_titles", [])

    if not past:
        return {"unique_ideas": ideas}

    filtered = []
    for idea in ideas:
        title = idea.get("title", "").lower()
        if not any(SequenceMatcher(None, title, p.lower()).ratio() > 0.6 for p in past):
            filtered.append(idea)

    result = filtered if len(filtered) >= 3 else ideas[:5]
    logger.info(f"Dedup: {len(ideas)} → {len(result)} ideas")
    return {"unique_ideas": result}


def critic_node(state: WorkflowState) -> dict:
    """Node 5: Evaluate ideas via Critic Agent."""
    evals = critic.run(state["unique_ideas"], state["context"])
    return {"evaluations": evals}


def refine_node(state: WorkflowState) -> dict:
    """Node 6: Refine top ideas via Refiner Agent."""
    refined = refiner.run(
        state["unique_ideas"], state["evaluations"], state["context"],
        state["prompt"], state.get("difficulty"),
        state.get("timeline"), state.get("tech_preference"),
    )
    return {"refined_ideas": refined}


# ── Build Graph ─────────────────────────────────────────────────────────────

def _build_graph() -> StateGraph:
    """Construct the LangGraph state graph."""
    g = StateGraph(WorkflowState)

    g.add_node("plan", plan_node)
    g.add_node("research", research_node)
    g.add_node("ideate", ideate_node)
    g.add_node("dedup", dedup_node)
    g.add_node("critic", critic_node)
    g.add_node("refine", refine_node)

    g.add_edge(START, "plan")
    g.add_edge("plan", "research")
    g.add_edge("research", "ideate")
    g.add_edge("ideate", "dedup")
    g.add_edge("dedup", "critic")
    g.add_edge("critic", "refine")
    g.add_edge("refine", END)

    return g.compile()


_compiled_graph = None


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph()
    return _compiled_graph


# ── Public API ──────────────────────────────────────────────────────────────

def run_pipeline(prompt: str, difficulty: Optional[str], timeline: Optional[str],
                 tech_preference: Optional[str], db: DBSession) -> Tuple[dict, List[dict]]:
    """Run the full multi-agent pipeline. Returns (context, refined_ideas).

    Backwards-compatible signature with the old pipeline.py.
    """
    logger.info(f"Starting multi-agent pipeline for: {prompt[:80]}...")

    # Gather past idea titles for deduplication
    past_titles = [t for (t,) in db.query(Idea.title).all()]

    # Build initial state
    initial_state: WorkflowState = {
        "prompt": prompt,
        "difficulty": difficulty,
        "timeline": timeline,
        "tech_preference": tech_preference,
        "context": {},
        "research_brief": "",
        "rag_results": [],
        "raw_ideas": [],
        "unique_ideas": [],
        "evaluations": [],
        "refined_ideas": [],
        "past_titles": past_titles,
    }

    # Execute the graph
    graph = _get_graph()
    final_state = graph.invoke(initial_state)

    context = final_state.get("context", {})
    ideas = final_state.get("refined_ideas", [])

    logger.info(f"Pipeline complete: {len(ideas)} refined ideas")
    return context, ideas
