# Project Report

## AI-Based Customer Support Auto-Responder Using Large Language Models for Automated Query Handling

### 1. Abstract
This project implements a full-stack, production-style AI customer support system that automatically classifies customer intent and sentiment, retrieves relevant knowledge-base context, and generates grounded responses — escalating to a human agent when model confidence is low. It combines classical ML (TF-IDF + Logistic Regression) for fast real-time inference with an optional Retrieval-Augmented Generation (RAG) layer and pluggable LLM backends (OpenAI / Ollama).

### 2. Objectives
- Automate first-line customer query handling across 6 intent categories
- Detect customer sentiment to prioritize and route escalations
- Ground AI replies in a real FAQ knowledge base via semantic retrieval (RAG)
- Provide a full admin dashboard for operational visibility (volume, sentiment, intents, response time, escalation rate)
- Ship a system that runs entirely offline/self-hosted, with optional cloud-LLM upgrade

### 3. Dataset
A synthetic dataset of **10,500 customer queries** was generated programmatically (`dataset/generate_dataset.py`), covering:
- 6 intents: Complaint, Refund, Technical Issue, Account Issue, Order Status, General Inquiry
- 3 sentiments: Positive, Neutral, Negative
- Realistic product/order-id/day/amount slot-filling across dozens of templates per intent×sentiment combination
- A companion 15-entry FAQ knowledge base for RAG grounding

### 4. Modeling & Evaluation
Three model families were prepared for comparison:

| Model | Status | Notes |
|---|---|---|
| TF-IDF + Logistic Regression | **Trained & deployed** | `models/train_logistic_regression.py`. Accuracy/Precision/Recall/F1 all ≈1.0 on the held-out 20% split (metrics in `models/saved/metrics_logistic_regression.json`) — expected given the templated dataset's clean class separability. Powers live inference (<50ms). |
| DistilBERT (fine-tuned) | Script ready (`models/train_distilbert.py`) | Not executed as part of this delivery — fine-tuning is a GPU-recommended, multi-minute-to-hour job. Run it directly to produce comparable metrics. |
| BERT (fine-tuned) | Script ready (`models/train_bert.py`) | Same as above, larger model. |

`models/compare_models.py` aggregates whichever metrics files exist into a single comparison table/CSV, so once DistilBERT/BERT are trained, a full three-way comparison is one command away.

**Design decision:** shipping a fast classical model for the live API (rather than a transformer) keeps latency low and the whole application runnable without a GPU — appropriate for a customer-support auto-responder where p50/p95 latency matters as much as raw accuracy.

### 5. System Architecture
See `docs/ARCHITECTURE.md` for the full diagram. In short: React/Vite/Tailwind SPA ⇄ FastAPI REST API ⇄ SQLAlchemy/SQLite ⇄ AI pipeline (intent classifier → sentiment analyzer → RAG retriever → reply generator with human-escalation logic).

### 6. Key Features Delivered
- JWT authentication (register/login), role-based access (customer/admin)
- Real-time chat with typing animation, conversation history, suggested questions, dark mode
- Multi-turn context memory (last 10 messages fed back into the pipeline)
- RAG-grounded FAQ retrieval (FAISS + SentenceTransformers, with automatic TF-IDF fallback)
- Confidence scoring and automatic escalation to a human agent
- Admin dashboard: conversation browser with search/date/escalation filters, full analytics (intent/sentiment breakdowns, daily volume, response time, escalation rate), CSV export, user management (promote/demote, activate/deactivate, delete)
- Thumbs up/down feedback capture per AI reply

### 7. Testing
18 automated tests across 4 suites (`tests/`) covering unit-level AI predictions, auth, chat pipeline, and full integration flows (customer journey + admin workflow + authorization checks) — all passing against an isolated in-memory test database.

### 8. Deployment
Supports local (`uvicorn` + `vite`), Docker Compose (two containers, healthchecked), and static hosting on Render/Railway (see `docs/INSTALLATION.md` and root `README.md`).

### 9. Limitations & Future Work
- The synthetic dataset's template-based generation yields near-perfect classifier accuracy; a production deployment should retrain on real anonymized transcripts for a more realistic accuracy ceiling.
- DistilBERT/BERT fine-tuning was not executed in this delivery (compute/time); scripts are complete and tested for import correctness.
- FAISS-based RAG requires downloading a SentenceTransformer model on first run; offline/air-gapped environments automatically fall back to TF-IDF retrieval.
- Streaming token-by-token LLM responses (SSE) is not yet wired up; the current typing animation is client-side over a single JSON response — a natural next step when `USE_OPENAI`/`USE_OLLAMA` streaming is enabled.
