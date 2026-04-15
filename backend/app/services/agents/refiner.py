"""Refiner Agent — Expands ideas into detailed proposals.

Also handles iterative refinement: "make it cheaper", "target students",
"add mobile support", etc.
"""

import logging
from typing import List, Optional
from app.services.llm import call_llm, MODEL_SMART

logger = logging.getLogger(__name__)

REFINE_SYSTEM = """You are a senior strategic advisor. Create detailed, structured proposals for the given ideas and their evaluations.

Return a JSON object:
{
  "ideas": [
    {
      "title": "Idea Title",
      "problem_statement": "2-3 sentence problem description",
      "solution_overview": "2-3 sentence solution description",
      "key_features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
      "tech_stack": ["Approach/Tool 1", "Approach/Tool 2", "Approach/Tool 3"],
      "difficulty_level": "Beginner / Intermediate / Advanced",
      "mvp_scope": "2-3 sentences describing minimum viable version",
      "future_scope": "2-3 sentences on future enhancements",
      "feasibility_score": 8.5,
      "scalability_score": 7.0,
      "impact_score": 9.0,
      "confidence": 0.85,
      "score_explanation": "Brief reasoning for scores",
      "category": "Category name",
      "rank": 1
    }
  ]
}

Rules:
- Provide exactly 3 ideas (the top-ranked ones)
- Preserve scores and rankings from the critic evaluation
- tech_stack should be domain-appropriate (not always software — could be methodology, tools, equipment, etc.)
- Ranks must be 1, 2, 3"""

ITERATE_SYSTEM = """You are a senior strategic advisor. The user wants to refine an existing idea based on specific feedback.

Take the current idea and the user's refinement instruction, then produce an UPDATED version.

Return a JSON object with the SAME structure as the input idea, but modified according to the instruction:
{
  "title": "Updated Title (if needed)",
  "problem_statement": "Updated problem",
  "solution_overview": "Updated solution",
  "key_features": ["Updated features"],
  "tech_stack": ["Updated stack"],
  "difficulty_level": "Updated difficulty",
  "mvp_scope": "Updated MVP scope",
  "future_scope": "Updated future scope",
  "feasibility_score": 8.0,
  "scalability_score": 7.5,
  "impact_score": 8.5,
  "confidence": 0.8,
  "score_explanation": "Updated reasoning reflecting the changes",
  "category": "Category",
  "rank": 1,
  "refinement_note": "Brief summary of what was changed and why"
}

IMPORTANT: Only modify what the instruction asks for. Keep everything else intact."""


def run(ideas: List[dict], evaluations: List[dict], context: dict,
        prompt: str, difficulty: Optional[str] = None,
        timeline: Optional[str] = None, tech_pref: Optional[str] = None) -> List[dict]:
    """Refine top ideas into detailed proposals using the smart model."""
    logger.info("Refiner Agent: Expanding top ideas into proposals...")

    # Merge evaluation scores into idea objects
    eval_map = {e.get("title", "").lower(): e for e in evaluations}
    ranked_ideas = []
    for idea in ideas:
        title_lower = idea.get("title", "").lower()
        ev = eval_map.get(title_lower, {})
        merged = {**idea, **ev}
        ranked_ideas.append(merged)

    # Sort by critic rank and take top 4 (ask LLM to pick best 3)
    ranked_ideas.sort(key=lambda x: x.get("overall_rank", 99))
    top = ranked_ideas[:4]

    ideas_text = "\n".join(
        f"- {i.get('title')}: {i.get('one_liner', '')} "
        f"[Feasibility: {i.get('feasibility_score', '?')}, "
        f"Scalability: {i.get('scalability_score', '?')}, "
        f"Impact: {i.get('impact_score', '?')}]"
        for i in top
    )

    user_msg = (
        f"Original request: {prompt}\n\n"
        f"Domain: {context.get('domain')} / {context.get('idea_type', 'Project')}\n"
        f"Target: {context.get('target_users', 'General')}\n"
        f"Preferences: difficulty={difficulty or 'Any'}, "
        f"timeline={timeline or 'Any'}, approach={tech_pref or 'Any'}\n\n"
        f"Top ideas with critic scores:\n{ideas_text}\n\n"
        f"Provide exactly 3 detailed, ranked proposals."
    )

    result = call_llm(REFINE_SYSTEM, user_msg, model_id=MODEL_SMART).get("ideas", [])
    result.sort(key=lambda x: x.get("rank", 99))
    for i, idea in enumerate(result):
        idea["rank"] = i + 1
    logger.info(f"Refiner Agent: Produced {len(result)} detailed proposals")
    return result


def refine_idea(idea: dict, instruction: str) -> dict:
    """Iteratively refine a single idea using the smart model."""
    logger.info(f"Refiner Agent: Refining '{idea.get('title')}' — {instruction[:60]}...")

    import json
    user_msg = (
        f"Current idea:\n{json.dumps(idea, indent=2)}\n\n"
        f"User's refinement instruction: {instruction}"
    )

    result = call_llm(ITERATE_SYSTEM, user_msg, model_id=MODEL_SMART)
    logger.info(f"Refiner Agent: Refinement complete — {result.get('refinement_note', 'done')}")
    return result
