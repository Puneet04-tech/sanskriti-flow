@echo off
REM Sanskriti-Flow Setup Script for Windows
REM This script automates the setup process

echo ==================================
echo Sanskriti-Flow Setup Script
echo FOSS Hack 2026
echo ==================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.10+
    exit /b 1
)
echo √ Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo X Node.js not found. Please install Node.js 18+
    exit /b 1
)
echo √ Node.js found

REM Check Redis (Memurai on Windows)
echo ! Please ensure Redis/Memurai is installed and running

echo.
echo Setting up Backend...
cd backend

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

REM Download spaCy model
python -m spacy download en_core_web_sm

REM Create directories
if not exist "data\temp" mkdir data\temp
if not exist "data\output" mkdir data\output
if not exist "data\cache" mkdir data\cache
if not exist "models" mkdir models

REM Create .env file
if not exist ".env" (
    copy .env.example .env
    echo √ Created .env file
)

cd ..

echo.
echo Setting up Frontend...
cd frontend

REM Install dependencies
call npm install

REM Create .env.local file
if not exist ".env.local" (
    copy .env.local.example .env.local
    echo √ Created .env.local file
)

cd ..

echo.
echo ==================================
echo √ Setup Complete!
echo ==================================
echo.
echo To start the application:
echo.
echo 1. Start Redis (Memurai)
echo.
echo 2. Start Backend (Terminal 1):
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn main:app --reload
echo.
echo 3. Start Worker (Terminal 2):
echo    cd backend
echo    venv\Scripts\activate
echo    celery -A app.workers.celery_app worker --loglevel=info
echo.
echo 4. Start Frontend (Terminal 3):
echo    cd frontend
echo    npm run dev
echo.
echo Access the application at: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.

pause
