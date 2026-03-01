# Native Deployment Guide

This guide covers running Sanskriti-Flow without Docker, using native installations.

## Prerequisites Installation

### 1. Python 3.10+

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation
- Verify: `python --version`

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3-pip
```

**Mac:**
```bash
brew install python@3.10
```

### 2. Node.js 18+

**Windows:**
- Download from [nodejs.org](https://nodejs.org/)
- Install LTS version
- Verify: `node --version`

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Mac:**
```bash
brew install node@18
```

### 3. Redis / Memurai

**Windows (Memurai - Redis alternative):**
- Download from [memurai.com](https://www.memurai.com/)
- Install as Windows service
- Verify: Open Services and check "Memurai" is running
- Alternative: Use Redis in WSL2

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
# Verify
redis-cli ping  # Should return "PONG"
```

**Mac:**
```bash
brew install redis
brew services start redis
# Verify
redis-cli ping  # Should return "PONG"
```

### 4. FFmpeg

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Extract to `C:\ffmpeg`
- Add `C:\ffmpeg\bin` to System PATH
- Verify: `ffmpeg -version`

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

---

## Installation

### Automated Setup (Recommended)

**Windows:**
```bash
cd d:\sanskriti-flow
.\scripts\setup.bat
```

**Linux/Mac:**
```bash
cd ~/sanskriti-flow
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Installation

#### Backend Setup

1. **Navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**

*Windows PowerShell:*
```powershell
venv\Scripts\Activate.ps1
```

*Windows CMD:*
```cmd
venv\Scripts\activate.bat
```

*Linux/Mac:*
```bash
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Download spaCy model:**
```bash
python -m spacy download en_core_web_sm
```

6. **Create directories:**

*Windows:*
```powershell
New-Item -ItemType Directory -Force -Path data\temp, data\output, data\cache, models
```

*Linux/Mac:*
```bash
mkdir -p data/temp data/output data/cache models
```

7. **Setup environment:**

*Windows:*
```cmd
copy .env.example .env
```

*Linux/Mac:*
```bash
cp .env.example .env
```

8. **Edit `.env` file:**
```env
ENVIRONMENT=development
REDIS_HOST=localhost
REDIS_PORT=6379
USE_GPU=false  # Set to true if you have CUDA
```

#### Frontend Setup

1. **Navigate to frontend:**
```bash
cd ../frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Setup environment:**

*Windows:*
```cmd
copy .env.local.example .env.local
```

*Linux/Mac:*
```bash
cp .env.local.example .env.local
```

4. **Edit `.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running the Application

You need to run **3 services** in separate terminals:

### Terminal 1: Backend API

```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify:** Open http://localhost:8000/health

### Terminal 2: Celery Worker

```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

celery -A app.workers.celery_app worker --loglevel=info
```

**Expected output:**
```
-------------- celery@HOSTNAME v5.3.6
--- ***** -----
-- ******* ----
- *** --- * ---
- ** ----------
[tasks]
  . localize_video_task
  
celery@HOSTNAME ready.
```

**Note for Windows:** If you encounter issues, use:
```bash
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

### Terminal 3: Frontend

```bash
cd frontend
npm run dev
```

**Expected output:**
```
ready - started server on 0.0.0.0:3000
```

**Access:** http://localhost:3000

---

## Verification Checklist

- [ ] Python installed and in PATH
- [ ] Node.js installed and in PATH
- [ ] Redis/Memurai running
- [ ] FFmpeg installed and in PATH
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Backend API running (http://localhost:8000/health)
- [ ] Celery worker running (shows "ready")
- [ ] Frontend running (http://localhost:3000)

---

## Common Issues

### Issue: Redis Connection Failed

**Symptoms:**
```
ConnectionError: Error connecting to Redis
```

**Solutions:**

*Windows:*
1. Check Memurai service is running in Services
2. Or start Redis in WSL2: `sudo service redis-server start`

*Linux/Mac:*
```bash
sudo systemctl status redis
sudo systemctl start redis
```

### Issue: Celery Worker Won't Start (Windows)

**Symptoms:**
```
ValueError: not enough values to unpack
```

**Solution:**
Use solo pool:
```bash
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

### Issue: Port Already in Use

**Symptoms:**
```
OSError: [WinError 10048] Only one usage of each socket address
```

**Solutions:**

*Windows:*
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process
taskkill /PID <PID> /F
```

*Linux/Mac:*
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

### Issue: Module Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
Make sure virtual environment is activated:
```bash
# Check if (venv) appears in prompt
pip install -r requirements.txt
```

### Issue: spaCy Model Not Found

**Symptoms:**
```
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: FFmpeg Not Found

**Symptoms:**
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**Solution:**
- Ensure FFmpeg is installed
- Add to PATH
- Restart terminal
- Verify: `ffmpeg -version`

---

## Production Deployment

### Using Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Waitress (Windows)

```bash
pip install waitress
waitress-serve --port=8000 main:app
```

### Process Managers

**Supervisor (Linux):**
```ini
[program:sanskriti-backend]
command=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0
directory=/path/to/backend
autostart=true
autorestart=true
```

**PM2 (Cross-platform):**
```bash
npm install -g pm2
pm2 start ecosystem.config.js
```

### Reverse Proxy with Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Performance Tuning

### GPU Acceleration

If you have an NVIDIA GPU:

1. **Install CUDA Toolkit:**
   - Download from [nvidia.com/cuda](https://developer.nvidia.com/cuda-downloads)
   - Follow installation instructions

2. **Install PyTorch with CUDA:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. **Update `.env`:**
```env
USE_GPU=true
CUDA_VISIBLE_DEVICES=0
```

4. **Verify:**
```python
python -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

### Worker Scaling

Run multiple Celery workers:

```bash
# Worker 1 (Terminal 2)
celery -A app.workers.celery_app worker --loglevel=info -n worker1

# Worker 2 (Terminal 4)
celery -A app.workers.celery_app worker --loglevel=info -n worker2
```

---

## Monitoring

### Celery Flower (Web UI)

```bash
pip install flower
celery -A app.workers.celery_app flower
```

Access: http://localhost:5555

### Logs

Logs are output to console by default. To save logs:

**Backend:**
```bash
uvicorn main:app --log-config logging.conf
```

**Worker:**
```bash
celery -A app.workers.celery_app worker --logfile=worker.log
```

---

## Backup and Maintenance

### Backup Data

*Windows:*
```powershell
Compress-Archive -Path data\ -DestinationPath backup-$(Get-Date -Format yyyy-MM-dd).zip
```

*Linux/Mac:*
```bash
tar -czf backup-$(date +%Y-%m-%d).tar.gz data/
```

### Clear Cache

```bash
# Remove processed files
rm -rf data/temp/*
rm -rf data/cache/*
```

### Update Dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

---

## Support

- **Documentation:** [docs/](../docs/)
- **Issues:** GitHub Issues
- **Setup Guide:** [SETUP.md](SETUP.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Native deployment gives you full control and maximum compatibility!** 🚀
