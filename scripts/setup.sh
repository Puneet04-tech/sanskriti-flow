#!/bin/bash

# Sanskriti-Flow Setup Script for Linux/Mac
# This script automates the setup process

set -e

echo "=================================="
echo "Sanskriti-Flow Setup Script"
echo "FOSS Hack 2026"
echo "=================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install redis
    else
        sudo apt-get install -y redis-server
    fi
fi
echo "✅ Redis found"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ffmpeg
    else
        sudo apt-get install -y ffmpeg
    fi
fi
echo "✅ FFmpeg found"

echo ""
echo "Setting up Backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create directories
mkdir -p data/temp data/output data/cache models

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
fi

cd ..

echo ""
echo "Setting up Frontend..."
cd frontend

# Install dependencies
npm install

# Create .env.local file
if [ ! -f .env.local ]; then
    cp .env.local.example .env.local
    echo "✅ Created .env.local file"
fi

cd ..

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Start Redis:"
echo "   redis-server"
echo ""
echo "2. Start Backend (Terminal 1):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload"
echo ""
echo "3. Start Worker (Terminal 2):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   celery -A app.workers.celery_app worker --loglevel=info"
echo ""
echo "4. Start Frontend (Terminal 3):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "Access the application at: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
