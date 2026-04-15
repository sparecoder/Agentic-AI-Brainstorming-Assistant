"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import router
from app.routes_rag import router as rag_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    logger.info("Starting up — initializing database...")
    init_db()
    logger.info("Database initialized successfully")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Agentic AI Idea Brainstorming Assistant",
    description="Multi-agent pipeline with RAG for generating, refining, and ranking ideas across any domain.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for production flexibility (essential for Vercel + HF)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
app.include_router(rag_router)


@app.get("/")
def root():
    return {"message": "Agentic AI Brainstorming API v2.0", "docs": "/docs"}
