"""API routes for idea generation and history."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models import Session, Idea
from app.schemas import (
    GenerateRequest, GenerateResponse, IdeaResponse,
    ExtractedContext, HistorySessionResponse, SessionDetailResponse,
)
from app.services.pipeline import run_pipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


def _idea_to_response(idea: Idea) -> IdeaResponse:
    """Convert an Idea ORM object to a response model."""
    return IdeaResponse(
        id=idea.id, title=idea.title,
        problem_statement=idea.problem_statement,
        solution_overview=idea.solution_overview,
        key_features=idea.key_features, tech_stack=idea.tech_stack,
        difficulty_level=idea.difficulty_level,
        mvp_scope=idea.mvp_scope, future_scope=idea.future_scope,
        feasibility_score=idea.feasibility_score,
        novelty_score=idea.novelty_score, impact_score=idea.impact_score,
        category=idea.category, rank=idea.rank,
    )


@router.post("/generate-ideas", response_model=GenerateResponse)
def generate_ideas(request: GenerateRequest, db: DBSession = Depends(get_db)):
    """Run the agentic pipeline and persist results."""
    logger.info(f"Generating ideas for: {request.prompt[:80]}...")

    try:
        context, refined_ideas = run_pipeline(
            prompt=request.prompt, difficulty=request.difficulty,
            timeline=request.timeline, tech_preference=request.tech_preference, db=db,
        )

        # Save session
        session = Session(
            prompt=request.prompt, difficulty=request.difficulty,
            timeline=request.timeline, tech_preference=request.tech_preference,
            extracted_context=context,
        )
        db.add(session)
        db.flush()

        # Save ideas
        responses = []
        for data in refined_ideas:
            idea = Idea(
                session_id=session.id,
                title=data.get("title", "Untitled"),
                problem_statement=data.get("problem_statement", ""),
                solution_overview=data.get("solution_overview", ""),
                key_features=data.get("key_features", []),
                tech_stack=data.get("tech_stack", []),
                difficulty_level=data.get("difficulty_level", "Intermediate"),
                mvp_scope=data.get("mvp_scope", ""),
                future_scope=data.get("future_scope", ""),
                feasibility_score=float(data.get("feasibility_score", 5)),
                novelty_score=float(data.get("novelty_score", 5)),
                impact_score=float(data.get("impact_score", 5)),
                category=data.get("category"),
                rank=data.get("rank", 1),
            )
            db.add(idea)
            db.flush()
            responses.append(_idea_to_response(idea))

        db.commit()
        logger.info(f"Session {session.id}: {len(responses)} ideas saved")

        return GenerateResponse(
            session_id=session.id,
            context=ExtractedContext(**context),
            ideas=responses,
            created_at=session.created_at,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Idea generation failed: {str(e)}")


@router.get("/history", response_model=List[HistorySessionResponse])
def get_history(db: DBSession = Depends(get_db)):
    """Return all past sessions, newest first."""
    return [
        HistorySessionResponse(
            id=s.id, prompt=s.prompt, difficulty=s.difficulty,
            timeline=s.timeline, tech_preference=s.tech_preference,
            idea_count=len(s.ideas), created_at=s.created_at,
        )
        for s in db.query(Session).order_by(Session.created_at.desc()).all()
    ]


@router.get("/history/{session_id}", response_model=SessionDetailResponse)
def get_session_detail(session_id: int, db: DBSession = Depends(get_db)):
    """Return a single session with all its ideas."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionDetailResponse(
        id=session.id, prompt=session.prompt,
        difficulty=session.difficulty, timeline=session.timeline,
        tech_preference=session.tech_preference,
        extracted_context=session.extracted_context,
        ideas=[_idea_to_response(i) for i in sorted(session.ideas, key=lambda i: i.rank)],
        created_at=session.created_at,
    )


@router.post("/regenerate/{session_id}", response_model=GenerateResponse)
def regenerate_ideas(session_id: int, db: DBSession = Depends(get_db)):
    """Re-run the pipeline for an existing session's prompt."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return generate_ideas(
        GenerateRequest(
            prompt=session.prompt, difficulty=session.difficulty,
            timeline=session.timeline, tech_preference=session.tech_preference,
        ), db,
    )
