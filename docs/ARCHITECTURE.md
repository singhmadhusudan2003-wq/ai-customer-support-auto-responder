# Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              BROWSER (Client)                             │
│   React 18 + Vite + Tailwind CSS + React Router + Recharts + Axios        │
│   Pages: Login · Register · Chat · History · Settings                     │
│          Dashboard · Analytics · Conversations · Users  (admin)           │
│                         http://localhost:3000                             │
└───────────────────────────────┬────────────────────────────────────────--┘
                                 │  REST/JSON over HTTPS (Axios, JWT Bearer)
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND (Python)                          │
│                         http://localhost:8000                            │
│                                                                            │
│  ┌────────────┐  ┌────────────┐  ┌───────────┐  ┌────────────────────┐   │
│  │ auth router│  │ chat router│  │  history  │  │ analytics / admin  │   │
│  │ (JWT)      │  │            │  │  router   │  │  routers           │   │
│  └─────┬──────┘  └─────┬──────┘  └─────┬─────┘  └──────────┬─────────┘   │
│        │               │               │                    │            │
│        ▼               ▼               ▼                    ▼            │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │                     SQLAlchemy ORM Layer                          │   │
│  │      Users · Conversations · Messages · Feedback · Logs           │   │
│  └───────────────────────────────┬─────────────────────────────────--┘   │
│                                   ▼                                       │
│                          SQLite Database (support.db)                     │
│                   (auto-created on first run; swappable for               │
│                    Postgres/MySQL via DATABASE_URL)                       │
└──────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼  (chat router calls the AI pipeline)
┌──────────────────────────────────────────────────────────────────────────┐
│                            AI PIPELINE (app/ai/)                          │
│                                                                            │
│   1. intent_classifier.py   — TF-IDF + Logistic Regression                │
│                                (6 classes; DistilBERT/BERT swappable)      │
│   2. sentiment_analyzer.py  — TF-IDF + Logistic Regression                │
│                                (Positive / Neutral / Negative)             │
│   3. rag_engine.py          — SentenceTransformer embeddings + FAISS      │
│                                (falls back to TF-IDF cosine similarity)    │
│                                over dataset/faq.csv                       │
│   4. response_generator.py  — orchestrates 1-3, optionally calls          │
│                                OpenAI or Ollama for generative replies,   │
│                                else uses template replies grounded by RAG │
│                                context; computes confidence score and     │
│                                escalates to a human agent when low        │
└──────────────────────────────────────────────────────────────────────────┘
```

## Request Lifecycle: sending a chat message

1. User types a message in the React chat UI (`Chat.jsx`) → `POST /api/chat` with JWT.
2. `chat.py` router creates/loads the `Conversation`, stores the user `Message`.
3. Recent message history (last 10) is fetched for multi-turn context memory.
4. `response_generator.generate_response()`:
   - `intent_classifier.predict()` → intent + confidence
   - `sentiment_analyzer.predict()` → sentiment + confidence
   - `rag_engine.retrieve()` → top-k relevant FAQ entries
   - reply generated via OpenAI/Ollama (if enabled) or a template grounded by the FAQ context
   - overall confidence = avg(intent_conf, sentiment_conf); if below threshold (or negative+complaint combo), `escalated = True`
5. AI `Message` is stored with `intent`, `sentiment`, `confidence`, `response_time_ms`, `escalated`.
6. Response streamed back to the UI; typing animation displays it progressively.

## Data Model (ER overview)

```
User (1) ───────< Conversation (1) ───────< Message (1) ───────< Feedback
  id                id                        id                   id
  name              user_id (FK)              conversation_id (FK) message_id (FK)
  email              title                      sender               rating
  hashed_password    escalated                  content              comment
  role                                           intent
  is_active                                      sentiment
                                                  confidence
                                                  response_time_ms
                                                  escalated

Log (standalone audit table: level, source, message, created_at)
```

## Why TF-IDF + Logistic Regression powers live inference

The project trains and compares three model families (Logistic Regression, DistilBERT, BERT — see `models/`). For the **live, real-time API path**, the app ships with the TF-IDF + Logistic Regression model because it:
- Requires no GPU and loads in milliseconds
- Achieves near-perfect accuracy on this task's vocabulary (see `models/saved/metrics_logistic_regression.json`)
- Keeps the whole stack runnable on any laptop, in Docker, or on free-tier hosting

The DistilBERT/BERT training scripts are fully implemented and ready to run (`models/train_distilbert.py`, `models/train_bert.py`) for teams that want to fine-tune a transformer and swap it in — `intent_classifier.py` and `sentiment_analyzer.py` are the only two files that would need a new loading branch.

## Deployment Topologies

- **Local dev:** `uvicorn --reload` + `vite dev` (hot reload both sides)
- **Docker Compose:** two containers (`backend`, `frontend` via nginx), one network, healthchecks
- **Render / Railway:** backend as a Python web service (`uvicorn main:app --host 0.0.0.0 --port $PORT`), frontend as a static site build (`npm run build` → serve `dist/`)
- **Streamlit (optional/alternative):** the AI pipeline modules (`app/ai/*`) are framework-agnostic and can be imported directly into a Streamlit script for a lightweight demo UI
