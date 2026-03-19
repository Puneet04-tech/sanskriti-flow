@echo off
REM Sanskriti-Flow Complete Startup Script
REM Sets all environment variables and launches all 4 services

setlocal enabledelayedexpansion

echo ========================================
echo  SANSKRITI-FLOW STARTUP SCRIPT
echo ========================================

REM Set D drive cache paths AT SYSTEM LEVEL (before any Python process starts)
echo.
echo [1/4] Setting Environment Variables (D drive caches)...

set "HF_HOME=d:\sanskriti-flow\backend\data\cache\huggingface"
set "TRANSFORMERS_CACHE=d:\sanskriti-flow\backend\data\cache\huggingface\transformers"
set "TORCH_HOME=d:\sanskriti-flow\backend\data\cache\torch"
set "XDG_CACHE_HOME=d:\sanskriti-flow\backend\data\cache"
set "TMPDIR=d:\sanskriti-flow\backend\data\cache\tmp"
set "TEMP=d:\sanskriti-flow\backend\data\cache\tmp"
set "TMP=d:\sanskriti-flow\backend\data\cache\tmp"
set "PIP_CACHE_DIR=d:\sanskriti-flow\backend\data\cache\pip"
set "MPLCONFIGDIR=d:\sanskriti-flow\backend\data\cache\matplotlib"
set "NPM_CONFIG_CACHE=d:\sanskriti-flow\backend\data\cache\npm"
set "PLAYWRIGHT_BROWSERS_PATH=d:\sanskriti-flow\backend\data\cache\playwright"
set "YARN_CACHE_FOLDER=d:\sanskriti-flow\backend\data\cache\yarn"
set "PNPM_STORE_PATH=d:\sanskriti-flow\backend\data\cache\pnpm"
set "PUPPETEER_CACHE_DIR=d:\sanskriti-flow\backend\data\cache\playwright"

echo    HF_HOME=%HF_HOME%
echo    TORCH_HOME=%TORCH_HOME%
echo    TEMP/TMP/TMPDIR=%TEMP%

REM Create directories if they don't exist
echo.
echo [2/4] Creating cache directories...
if not exist "%HF_HOME%" mkdir "%HF_HOME%"
if not exist "%TRANSFORMERS_CACHE%" mkdir "%TRANSFORMERS_CACHE%"
if not exist "%TORCH_HOME%" mkdir "%TORCH_HOME%"
if not exist "%TMPDIR%" mkdir "%TMPDIR%"
if not exist "%PIP_CACHE_DIR%" mkdir "%PIP_CACHE_DIR%"
if not exist "%MPLCONFIGDIR%" mkdir "%MPLCONFIGDIR%"
if not exist "%NPM_CONFIG_CACHE%" mkdir "%NPM_CONFIG_CACHE%"
if not exist "%PLAYWRIGHT_BROWSERS_PATH%" mkdir "%PLAYWRIGHT_BROWSERS_PATH%"
if not exist "%YARN_CACHE_FOLDER%" mkdir "%YARN_CACHE_FOLDER%"
if not exist "%PNPM_STORE_PATH%" mkdir "%PNPM_STORE_PATH%"
echo    ✓ All cache directories created on D drive

REM Clean up any accidental C drive caches
echo.
echo [3/4] Cleaning C drive caches (removing old fallback caches)...

if exist "C:\Users\%USERNAME%\.cache" (
    echo    Found C:\Users\%USERNAME%\.cache - removing...
    rmdir /s /q "C:\Users\%USERNAME%\.cache" 2>nul
)

if exist "%USERPROFILE%\.cache\huggingface" (
    echo    Found %USERPROFILE%\.cache\huggingface - removing...
    rmdir /s /q "%USERPROFILE%\.cache\huggingface" 2>nul
)

if exist "%USERPROFILE%\.torch" (
    echo    Found %USERPROFILE%\.torch - removing...
    rmdir /s /q "%USERPROFILE%\.torch" 2>nul
)

echo    ✓ C drive caches cleaned

REM Start services
echo.
echo [4/4] Launching services...
echo.

REM Start Redis (if not already running)
echo [Redis] Starting on port 6379...
cd d:\sanskriti-flow\redis
start "Redis" redis-server redis.windows.conf >nul 2>&1

REM Start Backend API
echo [Backend API] Starting on port 8000...
cd d:\sanskriti-flow\backend
start "Backend API" cmd /k "venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a few seconds for API to start
timeout /t 3 /nobreak

REM Start Celery Worker
echo [Celery Worker] Starting...
start "Celery Worker" cmd /k "venv\Scripts\python.exe -m celery -A app.workers.celery_app worker --loglevel=info --pool=solo --hostname=celery-main@%%h"

REM Start Frontend
echo [Frontend] Starting on port 3000...
cd d:\sanskriti-flow\frontend
start "Frontend" cmd /k "npm run dev"

REM Summary
echo.
echo ========================================
echo  STARTUP COMPLETE
echo ========================================
echo.
echo Services:
echo   - Redis: http://localhost:6379
echo   - Backend API: http://localhost:8000
echo   - Frontend: http://localhost:3000
echo   - Celery Worker: Running in background
echo.
echo All caches configured to: D:\ drive
echo No C: drive usage for models or temp files
echo.
echo Close one of the terminal windows to stop all services.
echo ========================================

pause
