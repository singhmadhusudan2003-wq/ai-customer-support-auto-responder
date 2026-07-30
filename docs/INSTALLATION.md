# Installation Guide

## Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- Git
- (Optional) Docker + Docker Compose
- (Optional) An OpenAI API key or a local Ollama installation, if you want LLM-generated replies instead of the built-in template engine

## Option A — Run Locally (recommended for development)

### 1. Clone / unzip the project
```bash
cd ai-customer-support-auto-responder
```

### 2. Generate the dataset (already included, but you can regenerate it)
```bash
cd dataset
python3 generate_dataset.py
cd ..
```

### 3. Train the ML models (already trained artifacts are included in `models/saved/`, but you can retrain)
```bash
cd models
python3 train_logistic_regression.py     # fast, ~1 second, always run this
# Optional, heavier, GPU-recommended:
python3 train_distilbert.py
python3 train_bert.py
python3 compare_models.py
cd ..
```

### 4. Backend setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env         # optional, defaults work out of the box
uvicorn main:app --reload
```
Backend runs at **http://localhost:8000** (interactive API docs at `/docs`).
The SQLite database (`support.db`) and a default admin account are created automatically on first run.

**Default admin login:** `admin@example.com` / `Admin@123`

### 5. Frontend setup (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at **http://localhost:3000** and proxies `/api` calls to the backend.

### 6. Open the app
Visit **http://localhost:3000** in your browser. Register a customer account, or log in as the seeded admin to view the dashboard.

## Option B — Run with Docker

```bash
docker-compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

To run in the background:
```bash
docker-compose up -d --build
```

To stop:
```bash
docker-compose down
```

## Option C — One-command scripts

- **Windows:** double-click `run_project.bat` (or run it from a terminal)
- **macOS/Linux:** `bash run_project.sh`

Both scripts install dependencies (if needed) and start the backend and frontend together.

## Enabling a real LLM (optional)

By default the app uses a fast template + RAG reply engine that works fully offline. To use a real LLM:

**OpenAI:**
```
USE_OPENAI=true
OPENAI_API_KEY=sk-...
```

**Ollama (local Llama 3 / Mistral):**
```
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```
Set these in `backend/.env` (or as environment variables for Docker) and restart the backend.

## Running Tests
```bash
pip install -r requirements.txt   # from project root, or backend/requirements.txt
pytest tests/ -v
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | Run `uvicorn` from inside the `backend/` directory |
| Port 8000 or 3000 already in use | Stop the other process, or change the port in `vite.config.js` / `uvicorn --port` |
| `faiss` or `sentence-transformers` fails to install | The app automatically falls back to a TF-IDF retriever — this is not a blocking error |
| Frontend shows "Network Error" | Confirm the backend is running at port 8000 and CORS_ORIGINS includes your frontend URL |
