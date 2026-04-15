"""Planner Agent — Analyzes user intent and extracts structured context.

Detects domain automatically, identifies sub-tasks, and generates research
questions. Works across ANY domain (tech, business, healthcare, education, etc.)
"""

import logging
from typing import Optional
from app.services.llm import call_llm, MODEL_FAST

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert strategic consultant who works across ALL domains — from cutting-edge technology to traditional brick-and-mortar retail, healthcare, education, social impact, research, startups, and offline services.

Analyze the user's brainstorming request and extract structured context. You must remain unbiased by technology; if a user asks for a business idea, consider both digital and physical/operational approaches.

Return a JSON object with exactly these fields:
{
  "domain": "The primary domain/field (e.g., Healthcare, Education, Retail, Manufacturing, Social Impact, Technology, Research, Business, Environment, Entertainment)",
  "sub_domains": ["sub-domain 1", "sub-domain 2"],
  "complexity": "Simple / Moderate / Complex",
  "timeline": "Short-term (days-weeks) / Medium-term (months) / Long-term (6+ months)",
  "target_users": "Who would benefit from these ideas (e.g., Students, Doctors, Entrepreneurs, Local Residents, General Public)",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "constraints": ["Any constraints mentioned or implied"],
  "research_questions": ["What should we research to generate better ideas?", "Question 2", "Question 3"],
  "idea_type": "Project / Product / Service / Brick-and-Mortar / Initiative / Research / Campaign"
}

Be thorough in extracting context. Ensure you identify if the user's intent leans towards an offline, service-based, or digital approach."""


def run(prompt: str, difficulty: Optional[str] = None,
        timeline: Optional[str] = None, tech_pref: Optional[str] = None) -> dict:
    """Extract structured context using the fast 8b model."""
    logger.info("Planner Agent: Analyzing user intent...")

    user_msg = f"User's brainstorming request: {prompt}"
    if difficulty:
        user_msg += f"\nPreferred difficulty/complexity: {difficulty}"
    if timeline:
        user_msg += f"\nPreferred timeline: {timeline}"
    if tech_pref:
        user_msg += f"\nTechnology/approach preference: {tech_pref}"

    # Use the fast model for extraction tasks
    result = call_llm(SYSTEM_PROMPT, user_msg, model_id=MODEL_FAST)
    logger.info(f"Planner Agent: Domain={result.get('domain')}, Type={result.get('idea_type')}")
    return result
