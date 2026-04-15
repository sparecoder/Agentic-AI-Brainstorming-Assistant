"""API routes for idea generation, refinement, history, and bookmarks."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models import Session, Idea, Bookmark
from app.schemas import (
    GenerateRequest, GenerateResponse, IdeaResponse,
    ExtractedContext, HistorySessionResponse, SessionDetailResponse,
    RefineRequest, BookmarkRequest, BookmarkResponse,
)
from app.services.workflow import run_pipeline
from app.services.agents.refiner import refine_idea

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
        scalability_score=idea.scalability_score, impact_score=idea.impact_score,
        confidence=idea.confidence, score_explanation=idea.score_explanation,
        category=idea.category, rank=idea.rank,
        is_bookmarked=idea.is_bookmarked,
    )


# ── Generate ────────────────────────────────────────────────────────────────

@router.post("/generate-ideas", response_model=GenerateResponse)
def generate_ideas(request: GenerateRequest, db: DBSession = Depends(get_db)):
    """Run the multi-agent pipeline and persist results."""
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
                scalability_score=float(data.get("scalability_score", 5)),
                impact_score=float(data.get("impact_score", 5)),
                confidence=float(data.get("confidence", 0.7)),
                score_explanation=data.get("score_explanation", ""),
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
            context=ExtractedContext(**{k: context.get(k) for k in
                ['domain', 'sub_domains', 'complexity', 'timeline', 'target_users',
                 'keywords', 'constraints', 'research_questions', 'idea_type']
                if context.get(k) is not None}),
            ideas=responses,
            rag_sources=0,
            created_at=session.created_at,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Idea generation failed: {str(e)}")


# ── Refine ──────────────────────────────────────────────────────────────────

@router.post("/refine-idea/{idea_id}", response_model=IdeaResponse)
def refine_idea_endpoint(idea_id: int, request: RefineRequest,
                         db: DBSession = Depends(get_db)):
    """Iteratively refine a single idea with natural-language instructions."""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Build dict from current idea
    current = {
        "title": idea.title, "problem_statement": idea.problem_statement,
        "solution_overview": idea.solution_overview, "key_features": idea.key_features,
        "tech_stack": idea.tech_stack, "difficulty_level": idea.difficulty_level,
        "mvp_scope": idea.mvp_scope, "future_scope": idea.future_scope,
        "feasibility_score": idea.feasibility_score, "scalability_score": idea.scalability_score,
        "impact_score": idea.impact_score, "category": idea.category, "rank": idea.rank,
    }

    try:
        refined = refine_idea(current, request.instruction)

        # Update the idea in the database
        idea.title = refined.get("title", idea.title)
        idea.problem_statement = refined.get("problem_statement", idea.problem_statement)
        idea.solution_overview = refined.get("solution_overview", idea.solution_overview)
        idea.key_features = refined.get("key_features", idea.key_features)
        idea.tech_stack = refined.get("tech_stack", idea.tech_stack)
        idea.difficulty_level = refined.get("difficulty_level", idea.difficulty_level)
        idea.mvp_scope = refined.get("mvp_scope", idea.mvp_scope)
        idea.future_scope = refined.get("future_scope", idea.future_scope)
        idea.feasibility_score = float(refined.get("feasibility_score", idea.feasibility_score))
        idea.scalability_score = float(refined.get("scalability_score", idea.scalability_score))
        idea.impact_score = float(refined.get("impact_score", idea.impact_score))
        idea.confidence = float(refined.get("confidence", idea.confidence or 0.7))
        idea.score_explanation = refined.get("score_explanation", idea.score_explanation)

        db.commit()
        db.refresh(idea)

        resp = _idea_to_response(idea)
        resp.refinement_note = refined.get("refinement_note", "")
        return resp
    except Exception as e:
        db.rollback()
        logger.error(f"Refinement failed: {e}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")


# ── Bookmarks ───────────────────────────────────────────────────────────────

@router.post("/bookmark/{idea_id}", response_model=BookmarkResponse)
def toggle_bookmark(idea_id: int, request: BookmarkRequest = None,
                    db: DBSession = Depends(get_db)):
    """Add or update a bookmark for an idea."""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Check if already bookmarked
    existing = db.query(Bookmark).filter(Bookmark.idea_id == idea_id).first()
    if existing:
        # Remove bookmark (toggle off)
        idea.is_bookmarked = False
        db.delete(existing)
        db.commit()
        # Return a response indicating removal by re-creating a temporary response
        raise HTTPException(status_code=200, detail="Bookmark removed")

    # Create bookmark
    note = request.note if request else None
    bm = Bookmark(idea_id=idea_id, note=note)
    idea.is_bookmarked = True
    db.add(bm)
    db.commit()
    db.refresh(bm)

    return BookmarkResponse(
        id=bm.id, idea_id=idea_id, idea=_idea_to_response(idea),
        note=bm.note, created_at=bm.created_at,
    )


@router.delete("/bookmark/{idea_id}")
def remove_bookmark(idea_id: int, db: DBSession = Depends(get_db)):
    """Remove a bookmark from an idea."""
    bm = db.query(Bookmark).filter(Bookmark.idea_id == idea_id).first()
    if not bm:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if idea:
        idea.is_bookmarked = False

    db.delete(bm)
    db.commit()
    return {"message": "Bookmark removed"}


@router.get("/bookmarks", response_model=List[BookmarkResponse])
def get_bookmarks(db: DBSession = Depends(get_db)):
    """List all bookmarked ideas."""
    bookmarks = db.query(Bookmark).order_by(Bookmark.created_at.desc()).all()
    return [
        BookmarkResponse(
            id=bm.id, idea_id=bm.idea_id, idea=_idea_to_response(bm.idea),
            note=bm.note, created_at=bm.created_at,
        )
        for bm in bookmarks
    ]


# ── History ─────────────────────────────────────────────────────────────────

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
