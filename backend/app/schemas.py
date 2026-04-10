from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Request Models ──────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    """Request body for /generate-ideas."""
    prompt: str = Field(..., min_length=3, max_length=1000, description="The brainstorming prompt")
    difficulty: Optional[str] = Field(None, description="Beginner / Intermediate / Advanced")
    timeline: Optional[str] = Field(None, description="Hackathon / Semester / Long-term")
    tech_preference: Optional[str] = Field(None, description="e.g. Python, Web, ML")


# ── Response Models ─────────────────────────────────────────────────────────

class ExtractedContext(BaseModel):
    """Context extracted from the user prompt in Step 1."""
    domain: str
    complexity: str
    timeline: str
    target_users: str
    keywords: List[str]


class IdeaResponse(BaseModel):
    """A single structured idea."""
    id: Optional[int] = None
    title: str
    problem_statement: str
    solution_overview: str
    key_features: List[str]
    tech_stack: List[str]
    difficulty_level: str
    mvp_scope: str
    future_scope: str
    feasibility_score: float = Field(..., ge=1, le=10)
    novelty_score: float = Field(..., ge=1, le=10)
    impact_score: float = Field(..., ge=1, le=10)
    category: Optional[str] = None
    rank: int


class GenerateResponse(BaseModel):
    """Response from /generate-ideas."""
    session_id: int
    context: ExtractedContext
    ideas: List[IdeaResponse]
    created_at: datetime


class HistorySessionResponse(BaseModel):
    """A past session for the history list."""
    id: int
    prompt: str
    difficulty: Optional[str]
    timeline: Optional[str]
    tech_preference: Optional[str]
    idea_count: int
    created_at: datetime


class SessionDetailResponse(BaseModel):
    """Full session detail with ideas."""
    id: int
    prompt: str
    difficulty: Optional[str]
    timeline: Optional[str]
    tech_preference: Optional[str]
    extracted_context: Optional[ExtractedContext]
    ideas: List[IdeaResponse]
    created_at: datetime
