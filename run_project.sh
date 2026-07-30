#!/usr/bin/env bash
# ==============================================================
#  AI Customer Support Auto-Responder - macOS/Linux launcher
#  Installs dependencies (first run only) and starts both the
#  backend (http://localhost:8000) and frontend (http://localhost:3000)
# ==============================================================
set -e

echo ""
echo "=== AI Customer Support Auto-Responder ==="
echo ""

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Backend setup ---
cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

echo "Installing backend dependencies..."
pip install -q -r requirements.txt

echo "Starting backend on http://localhost:8000 ..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Starting frontend on http://localhost:3000 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000  (docs at /docs)"
echo "Frontend: http://localhost:3000"
echo "Default admin login: admin@example.com / Admin@123"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
