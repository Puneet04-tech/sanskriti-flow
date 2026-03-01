# Sanskriti-Flow Setup Guide

Complete setup instructions for FOSS Hack 2026 submission.

## Prerequisites

### Required Software
- Python 3.10 or higher
- Node.js 18 or higher
- Redis 5.0 or higher
- FFmpeg 4.0 or higher
- Git

### Optional (for GPU acceleration)
- CUDA 11.8 or higher
- cuDNN 8.0 or higher
- NVIDIA GPU with 8GB+ VRAM

---

## Installation Methods

### Native Setup (Recommended)

**Best for local development and compatibility!**

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/sanskriti-flow.git
cd sanskriti-flow
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create environment file
copy .env.example .env

# Create data directories
mkdir data\temp data\output data\cache models

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Redis Setup

**Windows (using Memurai):**
```bash
# Download from https://www.memurai.com/
# Install and start service
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

#### 4. Celery Worker

Open a new terminal:
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

celery -A app.workers.celery_app worker --loglevel=info
```

#### 5. Frontend Setup

Open a new terminal:
```bash
cd frontend

# Install dependencies
npm install

# Create environment file
copy .env.local.example .env.local

# Start development server
npm run dev
```

---

## Model Installation

### Required Models

**1. Faster-Whisper**
```bash
# Automatically downloaded on first use
# Models: tiny, base, small, medium, large-v2
```

**2. NLLB-200**
```bash
# Automatically downloaded from HuggingFace
# Model: facebook/nllb-200-distilled-600M
```

**3. Llama 3.1 (Optional - for quiz generation)**
```bash
# Download from HuggingFace or Meta
# Place in: backend/models/llama-3.1-8b-instruct.gguf
```

**4. Moondream2 (Optional - for vision-sync)**
```bash
# Automatically downloaded from HuggingFace
# Model: vikhyatk/moondream2
```

### Model Storage

Default locations:
- Whisper: `~/.cache/huggingface/`
- Transformers: `~/.cache/huggingface/hub/`
- Custom: `backend/models/`

---

## Configuration

### Backend (.env)
```env
ENVIRONMENT=development
REDIS_HOST=localhost
REDIS_PORT=6379
WHISPER_MODEL=base
USE_GPU=false  # Set to true if CUDA available
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Verification

### Check Backend
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","environment":"development"}
```

### Check Frontend
Open browser: http://localhost:3000

### Check Worker
Look for:
```
celery@hostname ready.
```

---

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Redis Connection Failed
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### GPU Not Detected
```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Should return: True
```

### Model Download Errors
```bash
# Clear cache
rm -rf ~/.cache/huggingface/

# Try manual download
huggingface-cli download facebook/nllb-200-distilled-600M
```

---

## Development Workflow

### 1. Start Services
```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate
uvicorn main:app --reload

# Terminal 2: Worker
cd backend
venv\Scripts\activate
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3: Frontend
cd frontend
npm run dev
```

### 2. Make Changes
- Edit code in your favorite editor
- Changes auto-reload (except Celery worker)

### 3. Test
```bash
# Backend tests
pytest backend/tests/

# Frontend tests
npm test
```

### 4. Commit
```bash
git add -A
git commit -m "feat: add new feature"
git push
```

---

## Production Deployment

### Environment Setup
```bash
# Backend
ENVIRONMENT=production
USE_GPU=true
LOG_LEVEL=WARNING

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Build Frontend
```bash
cd frontend
npm run build
npm start
```

### Use Gunicorn (Backend)
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Setup Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

---

## Support

- **Documentation**: `/docs` folder
- **Issues**: GitHub Issues
- **Community**: (TBD)

---

## Next Steps

1. ✅ Complete setup
2. 📖 Read [ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. 🔧 Check [API.md](docs/API.md)
4. 🤝 See [CONTRIBUTING.md](CONTRIBUTING.md)
5. 🚀 Start building!

---

**Ready to make education accessible! 🎓**
