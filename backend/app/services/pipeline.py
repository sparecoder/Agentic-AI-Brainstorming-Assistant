"""
Agentic Pipeline — Multi-step idea generation using Groq LLM.

Steps:
  1. Extract context (domain, complexity, timeline, users)
  2. Generate 7 raw ideas
  3. Deduplicate against DB history
  4. Refine top 3 + rank by feasibility/novelty/impact
"""

import json
import logging
from typing import Optional, List, Tuple
from difflib import SequenceMatcher

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from sqlalchemy.orm import Session as DBSession

from app.config import get_settings
from app.models import Idea

logger = logging.getLogger(__name__)

# ── LLM Client ──────────────────────────────────────────────────────────────

_llm = None

def _get_llm() -> ChatGroq:
    """Lazily create and cache the Groq LLM client."""
    global _llm
    if _llm is None:
        s = get_settings()
        _llm = ChatGroq(api_key=s.groq_api_key, model=s.groq_model,
                        temperature=0.8, max_tokens=4096)
    return _llm


def _call_llm(system: str, user: str) -> dict:
    """Call Groq in JSON mode and parse the response."""
    llm = _get_llm()
    msgs = [SystemMessage(content=system), HumanMessage(content=user)]
    resp = llm.bind(response_format={"type": "json_object"}).invoke(msgs)
    text = resp.content
    logger.info(f"LLM response: {len(text)} chars")

    # Parse JSON, handling markdown code fences
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text.strip())

# ── Prompt Templates ────────────────────────────────────────────────────────

EXTRACT_PROMPT = """You are an expert project consultant. Analyze the user's brainstorming request and extract structured context.

Return a JSON object with exactly these fields:
{
  "domain": "The primary domain/field (e.g., Healthcare, Education, Finance)",
  "complexity": "Simple / Moderate / Complex",
  "timeline": "Short-term (days-weeks) / Medium-term (months) / Long-term (6+ months)",
  "target_users": "Who would use these projects (e.g., Students, Doctors, General Public)",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}"""

GENERATE_PROMPT = """You are a creative AI project ideation expert. Generate diverse and innovative project ideas based on the provided context.

Return a JSON object:
{
  "ideas": [
    {"title": "Short catchy title", "one_liner": "One sentence description", "category": "e.g. NLP, Computer Vision"}
  ]
}

Generate exactly 7 diverse ideas. Be creative and practical."""

REFINE_PROMPT = """You are a senior technical advisor. Create detailed structured proposals for the given ideas, then rank them.

Return a JSON object:
{
  "ideas": [
    {
      "title": "Project Title",
      "problem_statement": "2-3 sentence problem description",
      "solution_overview": "2-3 sentence solution description",
      "key_features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
      "tech_stack": ["Tech 1", "Tech 2", "Tech 3"],
      "difficulty_level": "Beginner / Intermediate / Advanced",
      "mvp_scope": "2-3 sentences on MVP",
      "future_scope": "2-3 sentences on future enhancements",
      "feasibility_score": 8.5,
      "novelty_score": 7.0,
      "impact_score": 9.0,
      "category": "Category name",
      "rank": 1
    }
  ]
}

Rank 1 (best) to N. Scores 1-10. Provide exactly 3 ideas."""

# ── Pipeline Steps ──────────────────────────────────────────────────────────

def _extract_context(prompt: str, difficulty: Optional[str],
                     timeline: Optional[str], tech_pref: Optional[str]) -> dict:
    """Step 1: Extract structured context from user prompt."""
    logger.info("Step 1: Extracting context...")
    user_msg = f"User prompt: {prompt}"
    if difficulty: user_msg += f"\nDifficulty: {difficulty}"
    if timeline:   user_msg += f"\nTimeline: {timeline}"
    if tech_pref:  user_msg += f"\nTech preference: {tech_pref}"
    return _call_llm(EXTRACT_PROMPT, user_msg)


def _generate_ideas(context: dict, prompt: str) -> List[dict]:
    """Step 2: Generate 7 raw ideas."""
    logger.info("Step 2: Generating ideas...")
    user_msg = (f"Original prompt: {prompt}\n\n"
                f"Context:\n"
                f"- Domain: {context.get('domain', 'General')}\n"
                f"- Complexity: {context.get('complexity', 'Moderate')}\n"
                f"- Timeline: {context.get('timeline', 'Medium-term')}\n"
                f"- Target: {context.get('target_users', 'General')}\n"
                f"- Keywords: {', '.join(context.get('keywords', []))}")
    return _call_llm(GENERATE_PROMPT, user_msg).get("ideas", [])


def _deduplicate(ideas: List[dict], db: DBSession) -> List[dict]:
    """Step 3: Remove ideas too similar to past generations."""
    logger.info("Step 3: Deduplicating...")
    past = [t for (t,) in db.query(Idea.title).all()]
    if not past:
        return ideas

    filtered = []
    for idea in ideas:
        title = idea.get("title", "").lower()
        if not any(SequenceMatcher(None, title, p.lower()).ratio() > 0.6 for p in past):
            filtered.append(idea)

    return filtered if len(filtered) >= 3 else ideas[:5]


def _refine_and_rank(ideas: List[dict], context: dict, prompt: str,
                     difficulty: Optional[str], timeline: Optional[str],
                     tech_pref: Optional[str]) -> List[dict]:
    """Step 4-5: Refine top ideas and rank them."""
    logger.info("Step 4: Refining & ranking...")
    top = ideas[:4]
    ideas_text = "\n".join(f"- {i.get('title')}: {i.get('one_liner', '')}" for i in top)

    user_msg = (f"Prompt: {prompt}\n\n"
                f"Context: {context.get('domain')} / {context.get('complexity')} / "
                f"{context.get('timeline')} / {context.get('target_users')}\n\n"
                f"Preferences: difficulty={difficulty or 'Any'}, "
                f"timeline={timeline or 'Any'}, tech={tech_pref or 'Any'}\n\n"
                f"Ideas to refine:\n{ideas_text}\n\nProvide exactly 3 ranked ideas.")

    result = _call_llm(REFINE_PROMPT, user_msg).get("ideas", [])
    result.sort(key=lambda x: x.get("rank", 99))
    for i, idea in enumerate(result):
        idea["rank"] = i + 1
    return result

# ── Public API ──────────────────────────────────────────────────────────────

def run_pipeline(prompt: str, difficulty: Optional[str], timeline: Optional[str],
                 tech_preference: Optional[str], db: DBSession) -> Tuple[dict, List[dict]]:
    """Run the full 4-step agentic pipeline. Returns (context, ideas)."""
    context = _extract_context(prompt, difficulty, timeline, tech_preference)
    raw = _generate_ideas(context, prompt)
    unique = _deduplicate(raw, db)
    refined = _refine_and_rank(unique, context, prompt, difficulty, timeline, tech_preference)
    return context, refined
