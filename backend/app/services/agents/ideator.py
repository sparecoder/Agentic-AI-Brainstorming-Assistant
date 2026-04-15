"""Ideator Agent — Generates elite, diverse ideas using multi-dimensional context.

Domain-agnostic: works for tech projects, brick-and-mortar business, social
impact, and scientific research. Prioritizes 'Innovation Archetypes'.
"""

import logging
from typing import List
from app.services.llm import call_llm, MODEL_SMART

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a visionary innovation strategist and venture architect. Your goal is to generate ideas that are not just 'creative', but technically feasible, economically viable, and strategically bold.

You work across ALL domains: Software (SaaS, Apps), Hardware, Physical Services, Retail, Community Initiatives, and Scientific Research.

Based on the provided context and research, generate exactly 7 diverse ideas.

Return a JSON object:
{
  "ideas": [
    {
      "title": "Short, bold title",
      "one_liner": "Single compelling sentence description",
      "category": "Archetype (e.g., Physical Infrastructure, Digital Platform, Operational Innovation, Community Event, Specialty Retail, Hardware Gadget)",
      "innovation_angle": "The specific 'unfair advantage' or novel twist (e.g., use of unused space, community-driven scale, logic inversion, tech-enabled efficiency)"
    }
  ]
}

CRITICAL DIVERSITY CONSTRAINTS:
1. NO CLONES: Every idea must approach the problem from a totally different angle. (e.g., if Idea 1 is a marketplace, Idea 2 MUST NOT be a marketplace).
2. Archetype Variety: You must include at least 4 distinct category archetypes (e.g., Mix of Service, Product, Tech, and Community).
3. Offline Priority: At least 3 ideas must have a significant physical/offline component that operates primarily in the real world (not on a screen).
4. Research Grounding: If research brief is provided, translate those insights into 2-3 specific ideas that couldn't have been generated without that data.
5. Lateral Thinking: Use logic from other industries (e.g., 'What if a hair salon operated like a subscription SaaS?' or 'What if an e-commerce brand had a physical traveling caravan?').

Tone: professional, high-impact, and visionary."""


def run(context: dict, prompt: str, research_brief: str) -> List[dict]:
    """Generate 7 elite ideas using the smart 70b-versatile model."""
    logger.info("Ideator Agent: Generating high-quality ideas...")

    domain = context.get("domain", "General")
    idea_type = context.get("idea_type", "Project")
    target = context.get("target_users", "General audience")

    user_msg = (
        f"Objective: {prompt}\n\n"
        f"--- CONTEXT ---\n"
        f"Primary Domain: {domain}\n"
        f"Sub-Domains: {', '.join(context.get('sub_domains', []))}\n"
        f"Innovation Focus: {context.get('innovation_focus', 'General')}\n"
        f"Complexity: {context.get('complexity', 'Moderate')}\n"
        f"Timeline: {context.get('timeline', 'Medium-term')}\n"
        f"Target Audience: {target}\n"
        f"--- END CONTEXT ---\n\n"
        f"--- RESEARCH BRIEF ---\n{research_brief}\n"
        f"--- END RESEARCH ---\n\n"
        f"Generate exactly 7 diverse '{idea_type}' ideas that solve the core problem described."
    )

    ideas = call_llm(SYSTEM_PROMPT, user_msg, model_id=MODEL_SMART).get("ideas", [])
    logger.info(f"Ideator Agent: Successfully generated {len(ideas)} ideas.")
    return ideas
