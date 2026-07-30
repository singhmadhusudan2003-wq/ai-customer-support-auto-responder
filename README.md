# 🤖 AI-Based Customer Support Auto-Responder

**Using Large Language Models for Automated Query Handling**

A complete, production-style full-stack application that automatically classifies customer intent and sentiment, retrieves grounded answers from a knowledge base (RAG), generates helpful replies, and escalates to a human agent when confidence is low — with a full admin analytics dashboard.

> Runs entirely locally/offline out of the box (no API keys required). Optionally powered by OpenAI or a local Ollama LLM for richer generated replies.

---

## ✨ Features

**Customer**
- ChatGPT-style chat UI with typing animation
- Real-time AI responses, streamed-feel typing
- Conversation history, suggested starter questions
- File upload (PDF/TXT) attachment in chat
- Dark / light mode, fully responsive

**Admin Dashboard**
- Secure JWT login
- All-conversations browser (search, date filter, escalation filter)
- Analytics: intent breakdown, sentiment breakdown, daily volume, avg response time, avg confidence, escalation rate
- CSV export
- Delete conversations
- User management (promote/demote, activate/deactivate, delete)

**AI**
- Intent classification (6 classes): Complaint, Refund, Technical Issue, Account Issue, Order Status, General Inquiry
- Sentiment analysis: Positive, Neutral, Negative
- Retrieval-Augmented Generation (RAG) over an FAQ knowledge base (FAISS + SentenceTransformers, with automatic TF-IDF fallback)
- Multi-turn context memory
- Confidence scoring with automatic human escalation
- Optional OpenAI / Ollama (Llama 3, Mistral) generative replies

---

## 🧱 Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, React Router, Axios, Recharts, Lucide Icons |
| Backend | FastAPI, SQLAlchemy, SQLite, JWT (python-jose + passlib) |
| AI/ML | scikit-learn (TF-IDF + Logistic Regression, live), HuggingFace Transformers (DistilBERT/BERT, scripts included), Sentence-Transformers + FAISS (RAG), LangChain-ready |
| Optional LLMs | OpenAI API, Ollama (Llama 3 / Mistral) |
| DevOps | Docker, Docker Compose, pytest |

---

## 🚀 Quick Start

### Option 1 — One command
```bash
# macOS/Linux
bash run_project.sh

# Windows
run_project.bat
```

### Option 2 — Manual
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# → http://localhost:8000  (docs: /docs)

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Option 3 — Docker
```bash
docker-compose up --build
```

Then open **http://localhost:3000** in your browser.

**Default admin login:** `admin@example.com` / `Admin@123`
(seeded automatically on first backend startup — change it via `.env` before deploying)

The SQLite database is created automatically on first run — no manual migration step needed.

📖 Full setup details: [`docs/INSTALLATION.md`](docs/INSTALLATION.md)

---

## 📁 Project Structure

```
project/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── ai/              # intent classifier, sentiment analyzer, RAG engine, response generator
│   │   ├── routers/         # auth, chat, history, analytics, admin, feedback
│   │   ├── utils/           # logging
│   │   ├── main.py          # FastAPI app factory + startup (DB create, admin seed)
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── auth.py / security.py / config.py / database.py
│   ├── main.py               # entrypoint (python main.py / uvicorn main:app)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React + Vite + Tailwind SPA
│   ├── src/
│   │   ├── pages/            # Login, Register, Chat, History, Settings, Dashboard, Analytics, Conversations, Users
│   │   ├── components/       # Sidebar, Navbar, ChatBubble, TypingIndicator, StatCard, Layout, ProtectedRoute
│   │   ├── context/           # AuthContext, ThemeContext
│   │   ├── api/                # axios client
│   ├── package.json
│   └── Dockerfile
├── dataset/                  # generate_dataset.py, customer_support_dataset.csv (10,500 rows), faq.csv
├── models/                   # train_logistic_regression.py (trained), train_distilbert.py, train_bert.py,
│                              # compare_models.py, saved/ (trained model artifacts + metrics)
├── notebooks/                # EDA.ipynb
├── docs/                     # INSTALLATION.md, API_DOCUMENTATION.md, ARCHITECTURE.md, PROJECT_REPORT.md
├── screenshots/               # add UI screenshots here
├── tests/                    # pytest: unit, API, and integration tests
├── docker/                   # docker-compose override example + notes
├── requirements.txt           # root convenience copy of backend/requirements.txt
├── README.md                  # you are here
├── Dockerfile                  # root convenience alias for the backend image
├── docker-compose.yml
├── .env.example
├── pytest.ini
├── run_project.bat
└── run_project.sh
```

---

## 🧠 Machine Learning

The dataset (10,500 synthetic customer queries) is generated by `dataset/generate_dataset.py`. Model training:

```bash
cd models
python3 train_logistic_regression.py   # fast — trains + saves the live production model
python3 train_distilbert.py            # optional, heavier — GPU recommended
python3 train_bert.py                  # optional, heavier — GPU recommended
python3 compare_models.py              # aggregates metrics from whichever models were trained
```

The app ships with a **pre-trained** TF-IDF + Logistic Regression model (`models/saved/`) achieving very high accuracy/precision/recall/F1 on the held-out split (see `models/saved/metrics_logistic_regression.json`) and powering real-time inference with sub-50ms latency. DistilBERT/BERT scripts are complete and ready to run when you want to fine-tune and benchmark transformer models — see [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) for the full comparison methodology and rationale.

---

## 🧪 Testing

```bash
pip install -r requirements.txt
pytest tests/ -v
```
18 tests covering AI unit predictions, auth, chat pipeline, and full integration (customer + admin) flows, run against an isolated in-memory database.

---

## 🌐 Deployment

| Target | How |
|---|---|
| Localhost | `run_project.sh` / `run_project.bat` |
| Docker | `docker-compose up --build` |
| Render | Backend: Python web service (`uvicorn main:app --host 0.0.0.0 --port $PORT`). Frontend: Static Site (`npm run build`, publish `frontend/dist`) |
| Railway | Same as Render — one service per Dockerfile (`backend/Dockerfile`, `frontend/Dockerfile`) |
| Streamlit (optional) | `app/ai/*` modules are framework-agnostic and importable directly into a Streamlit script for a lightweight demo |

---

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Project Report](docs/PROJECT_REPORT.md)

---

## ⚙️ Configuration

Copy `.env.example` to `.env` (project root or `backend/.env`) to customize secrets, the confidence-escalation threshold, or enable OpenAI/Ollama. Sensible defaults are used if omitted.

---

## 📄 License

This project is provided as an educational/portfolio reference implementation. Adapt freely for your own use.
