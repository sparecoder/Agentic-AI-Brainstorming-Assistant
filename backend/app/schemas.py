from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime


# ── Request Models ──────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    """Request body for /generate-ideas."""
    prompt: str = Field(..., min_length=3, max_length=1000, description="The brainstorming prompt")
    difficulty: Optional[str] = Field(None, description="Beginner / Intermediate / Advanced")
    timeline: Optional[str] = Field(None, description="Hackathon / Semester / Long-term")
    tech_preference: Optional[str] = Field(None, description="e.g. Python, Web, ML")


class RefineRequest(BaseModel):
    """Request body for /refine-idea."""
    instruction: str = Field(..., min_length=3, max_length=500,
                             description="e.g. 'Make it more scalable' or 'Target students instead'")


class BookmarkRequest(BaseModel):
    """Request body for bookmarking an idea."""
    note: Optional[str] = Field(None, max_length=500, description="Optional personal note")


class KBChatRequest(BaseModel):
    """Request body for chatting with the Knowledge Base."""
    message: str = Field(..., min_length=2, max_length=1000)


# ── Response Models ─────────────────────────────────────────────────────────

class KBChatResponse(BaseModel):
    """Response from KB chat."""
    answer: str
    sources: List[str]


class ExtractedContext(BaseModel):
    """Context extracted from the user prompt by the Planner Agent."""
    domain: str
    sub_domains: Optional[List[str]] = None
    complexity: str
    timeline: str
    target_users: Union[str, List[str]]
    keywords: List[str]
    constraints: Optional[List[str]] = None
    research_questions: Optional[List[str]] = None
    idea_type: Optional[str] = None


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
    scalability_score: float = Field(..., ge=1, le=10)
    impact_score: float = Field(..., ge=1, le=10)
    confidence: Optional[float] = Field(None, ge=0, le=1)
    score_explanation: Optional[str] = None
    category: Optional[str] = None
    rank: int
    is_bookmarked: Optional[bool] = False
    refinement_note: Optional[str] = None


class GenerateResponse(BaseModel):
    """Response from /generate-ideas."""
    session_id: int
    context: ExtractedContext
    ideas: List[IdeaResponse]
    rag_sources: Optional[int] = 0
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


class BookmarkResponse(BaseModel):
    """A bookmarked idea."""
    id: int
    idea_id: int
    idea: IdeaResponse
    note: Optional[str]
    created_at: datetime


class DocumentResponse(BaseModel):
    """An uploaded RAG document."""
    id: int
    filename: str
    source_name: str
    file_size: Optional[int]
    total_chunks: Optional[int]
    uploaded_at: datetime


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document."""
    document: DocumentResponse
    message: str
