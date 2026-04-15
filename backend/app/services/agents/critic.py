"""Critic Agent — Evaluates ideas with scores, confidence, and reasoning.

Provides objective evaluation across feasibility, scalability, and impact,
with written explanations for each score and overall confidence.
"""

import logging
from typing import List
from app.services.llm import call_llm, MODEL_SMART

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a rigorous, fair evaluator of ideas across all domains — from small local markets and physical products to massive digital ecosystems and scientific breakthroughs. 

You assess ideas objectively based on feasibility, scalability, and impact. You are not biased towards technology; a highly efficient offline physical service can be more impactful than a mediocre app.

For each idea, provide:
1. Feasibility score (1-10): How realistic is this to implement given today's technology and market logic?
2. Scalability score (1-10): How well can this grow? For digital, think users/infrastructure. For offline, think franchise, replication, or operational efficiency.
3. Impact score (1-10): How significant is the potential outcome/value created?
4. Confidence (0.0-1.0): Your certainty in this evaluation.
5. Score explanation: Specific reasoning for these scores, explicitly mentioning why it is feasible/scalable/impactful in its specific digital or physical context. 

Return a JSON object:
{
  "evaluations": [
    {
      "title": "Idea title (must match input exactly)",
      "feasibility_score": 8.5,
      "scalability_score": 7.0,
      "impact_score": 9.0,
      "confidence": 0.85,
      "score_explanation": "High feasibility because... Novel due to... Impactful since...",
      "strengths": ["Strength 1", "Strength 2"],
      "weaknesses": ["Weakness 1"],
      "overall_rank": 1
    }
  ]
}

Rules:
- Evaluate ALL ideas provided
- Be honest — don't inflate scores
- Rank from 1 (best) to N (worst) based on combined scores
- Consider the target domain and user when scoring"""


def run(ideas: List[dict], context: dict) -> List[dict]:
    """Evaluate and rank ideas with detailed reasoning using the smart model."""
    logger.info(f"Critic Agent: Evaluating {len(ideas)} ideas...")

    ideas_text = "\n".join(
        f"- {i.get('title', 'Untitled')}: {i.get('one_liner', '')}"
        f" [Category: {i.get('category', 'General')}]"
        for i in ideas
    )

    user_msg = (
        f"Domain: {context.get('domain', 'General')}\n"
        f"Idea Type: {context.get('idea_type', 'Project')}\n"
        f"Target Users: {context.get('target_users', 'General')}\n"
        f"Complexity Preference: {context.get('complexity', 'Moderate')}\n\n"
        f"Ideas to evaluate:\n{ideas_text}"
    )

    result = call_llm(SYSTEM_PROMPT, user_msg, model_id=MODEL_SMART).get("evaluations", [])
    result.sort(key=lambda x: x.get("overall_rank", 99))
    logger.info(f"Critic Agent: Ranked {len(result)} ideas")
    return result
