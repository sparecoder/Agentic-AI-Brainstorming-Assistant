# Agentic AI Idea Brainstorming Assistant

A full-stack web app that uses a **multi-step AI reasoning pipeline** (not a simple chatbot) to generate, refine, and rank project ideas.

## How It Works

The backend runs **3 sequential LLM calls** via Groq:

1. **Extract Context** — Analyzes your prompt to identify domain, complexity, users
2. **Generate Ideas** — Creates 7 diverse project concepts
3. **Deduplicate** — Filters out ideas too similar to past sessions
4. **Refine & Rank** — Develops top 3 ideas with detailed structure + scores

## Tech Stack

| Layer    | Technologies                           |
| -------- | -------------------------------------- |
| Frontend | React, Vite, Tailwind CSS v4           |
| Backend  | FastAPI, SQLAlchemy, SQLite             |
| AI       | Groq (LLaMA 3.3 70B via langchain-groq)|

## Quick Start

```bash
# Backend
cd backend
cp .env.example .env    # Add your GROQ_API_KEY
pip3 install -r requirements.txt
python3 -m uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173**

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + CORS
│   │   ├── config.py         # Environment settings
│   │   ├── database.py       # SQLite + SQLAlchemy
│   │   ├── models.py         # ORM models (Session, Idea)
│   │   ├── schemas.py        # Pydantic request/response models
│   │   ├── routes.py         # API endpoints
│   │   └── services/
│   │       └── pipeline.py   # Agentic pipeline + LLM calls
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main layout + results
│   │   ├── useIdeas.js       # Data hook + API calls
│   │   ├── index.css         # Design system
│   │   └── components/
│   │       ├── InputForm.jsx
│   │       ├── IdeaCard.jsx
│   │       ├── LoadingPipeline.jsx
│   │       └── HistoryPanel.jsx
│   ├── index.html
│   └── vite.config.js
└── README.md
```
