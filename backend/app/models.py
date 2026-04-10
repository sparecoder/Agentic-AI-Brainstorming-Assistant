import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Session(Base):
    """Represents a single brainstorming session (one user prompt)."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    difficulty = Column(String(50), nullable=True)
    timeline = Column(String(50), nullable=True)
    tech_preference = Column(String(200), nullable=True)
    extracted_context = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ideas = relationship("Idea", back_populates="session", cascade="all, delete-orphan")


class Idea(Base):
    """A single generated idea belonging to a session."""

    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    title = Column(String(300), nullable=False)
    problem_statement = Column(Text, nullable=False)
    solution_overview = Column(Text, nullable=False)
    key_features = Column(JSON, nullable=False)  # list of strings
    tech_stack = Column(JSON, nullable=False)     # list of strings
    difficulty_level = Column(String(50), nullable=False)
    mvp_scope = Column(Text, nullable=False)
    future_scope = Column(Text, nullable=False)
    feasibility_score = Column(Float, nullable=False)
    novelty_score = Column(Float, nullable=False)
    impact_score = Column(Float, nullable=False)
    category = Column(String(100), nullable=True)
    rank = Column(Integer, nullable=False)

    session = relationship("Session", back_populates="ideas")
