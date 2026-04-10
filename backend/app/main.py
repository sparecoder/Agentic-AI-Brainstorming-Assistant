"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import router

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
    description="Multi-step agentic pipeline for generating, refining, and ranking project ideas.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Agentic AI Brainstorming API", "docs": "/docs"}
