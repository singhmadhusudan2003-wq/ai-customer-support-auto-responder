@echo off
REM ============================================================
REM  AI Customer Support Auto-Responder - Windows launcher
REM  Installs dependencies (first run only) and starts both the
REM  backend (http://localhost:8000) and frontend (http://localhost:3000)
REM ============================================================

echo.
echo === AI Customer Support Auto-Responder ===
echo.

REM --- Backend setup ---
cd backend
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

echo Installing backend dependencies...
pip install -r requirements.txt

echo Starting backend on http://localhost:8000 ...
start "Backend - FastAPI" cmd /k "call venv\Scripts\activate.bat && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

cd ..

REM --- Frontend setup ---
cd frontend
if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)

echo Starting frontend on http://localhost:3000 ...
start "Frontend - Vite" cmd /k "npm run dev"

cd ..

echo.
echo Backend:  http://localhost:8000  (docs at /docs)
echo Frontend: http://localhost:3000
echo Default admin login: admin@example.com / Admin@123
echo.
pause
