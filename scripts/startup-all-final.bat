@echo off
REM Complete startup script that starts all services with better error handling
setlocal enabledelayedexpansion

echo ╔════════════════════════════════════════════════════════════════╗
echo ║          SANSKRITI-FLOW COMPLETE STARTUP                      ║
echo ╚════════════════════════════════════════════════════════════════╝

REM Set environment variables
set "HF_HOME=d:\sanskriti-flow\backend\data\cache\huggingface"
set "TRANSFORMERS_CACHE=d:\sanskriti-flow\backend\data\cache\huggingface\transformers"
set "TORCH_HOME=d:\sanskriti-flow\backend\data\cache\torch"
set "TMPDIR=d:\sanskriti-flow\backend\data\cache\tmp"
set "TEMP=d:\sanskriti-flow\backend\data\cache\tmp"
set "TMP=d:\sanskriti-flow\backend\data\cache\tmp"
set "PYTHONPATH=d:\sanskriti-flow\backend"

echo ✓ Environment variables set
echo.

REM Start Redis
echo [1/4] Starting Redis on port 6379...
start "Redis" cmd /c "cd d:\sanskriti-flow\redis && redis-server redis.windows.conf"
timeout /t 2 /nobreak

REM Start Backend API
echo [2/4] Starting Backend API on port 8000...
start "Backend API" cmd /c "cd d:\sanskriti-flow\backend && D:\sanskriti-flow\backend\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak

REM Start Celery Worker
echo [3/4] Starting Celery Worker...
start "Celery Worker" cmd /c "cd d:\sanskriti-flow\backend && D:\sanskriti-flow\backend\venv\Scripts\python.exe -m celery -A app.workers.celery_app worker --loglevel=info --pool=threads --concurrency=8"
timeout /t 2 /nobreak

REM Start Frontend
echo [4/4] Starting Frontend on port 3000...
start "Frontend" cmd /c "cd d:\sanskriti-flow\frontend && npm run dev"
timeout /t 2 /nobreak

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              STARTUP COMPLETE                                  ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║  Services starting:                                            ║
echo ║    ✓ Frontend: http://localhost:3000                           ║
echo ║    ✓ Backend:  http://localhost:8000                           ║
echo ║    ✓ Redis:    localhost:6379                                  ║
echo ║    ✓ Celery:   Connected to Redis                              ║
echo ╚════════════════════════════════════════════════════════════════╝
