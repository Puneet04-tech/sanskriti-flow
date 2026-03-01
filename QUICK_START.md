# Quick Start Guide for Your Laptop

Since Docker is not compatible with your laptop, I've set up **native installation** which will work perfectly!

## ✅ What Was Changed

- ❌ Removed: Docker, Dockerfile.backend, Dockerfile.frontend, docker-compose.yml
- ✅ Added: Comprehensive native deployment guide
- ✅ Updated: All documentation to focus on native setup

## 🚀 Quick Start (3 Steps)

### Step 1: Install Prerequisites

You need these installed on your laptop:

1. **Python 3.10+** - [Download here](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download here](https://nodejs.org/)
3. **Redis/Memurai** - [Download Memurai for Windows](https://www.memurai.com/)
4. **FFmpeg** - [Download here](https://ffmpeg.org/download.html)

### Step 2: Run Setup Script

Open PowerShell in the `d:\sanskriti-flow` directory:

```powershell
.\scripts\setup.bat
```

This will:
- Create Python virtual environment
- Install all Python dependencies
- Install Node.js dependencies
- Create necessary directories
- Setup environment files

### Step 3: Start the Application

You need **3 separate terminals** (or PowerShell tabs):

**Terminal 1 - Backend API:**
```powershell
cd d:\sanskriti-flow\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```powershell
cd d:\sanskriti-flow\backend
.\venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

**Terminal 3 - Frontend:**
```powershell
cd d:\sanskriti-flow\frontend
npm run dev
```

## 🌐 Access the Application

- **Frontend Dashboard:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 📋 Installation Checklist

- [ ] Python 3.10+ installed and in PATH
- [ ] Node.js 18+ installed
- [ ] Memurai installed and running (check Windows Services)
- [ ] FFmpeg installed and in PATH
- [ ] Ran `.\scripts\setup.bat` successfully
- [ ] Backend API running on port 8000
- [ ] Celery worker running
- [ ] Frontend running on port 3000

## 🔧 Common Issues & Solutions

### Issue 1: Celery won't start on Windows

**Solution:** Use the `--pool=solo` flag:
```powershell
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

### Issue 2: Redis connection error

**Solution:** Make sure Memurai service is running:
1. Press `Win + R`
2. Type `services.msc`
3. Find "Memurai" and ensure it's "Running"
4. If not, right-click → Start

### Issue 3: Port 8000 already in use

**Solution:** Find and kill the process:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue 4: Module not found

**Solution:** Make sure virtual environment is activated (you should see `(venv)` in your prompt):
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📚 Detailed Documentation

- **Complete Setup:** [docs/NATIVE_DEPLOYMENT.md](docs/NATIVE_DEPLOYMENT.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **API Reference:** [docs/API.md](docs/API.md)
- **Setup Guide:** [docs/SETUP.md](docs/SETUP.md)

## 🎯 What This Gives You

**Native deployment is actually BETTER for development:**

✅ **More Control** - Direct access to all services  
✅ **Better Debugging** - See logs in real-time in each terminal  
✅ **Lower Resource Usage** - No Docker overhead  
✅ **Works Everywhere** - Compatible with any laptop  
✅ **Easier to Modify** - Change code and see results immediately  
✅ **Learning Friendly** - Understand exactly what each service does  

## 🎓 Testing Your Setup

Once all 3 terminals are running, test it:

1. Open http://localhost:3000
2. Enter a video URL (or use a sample URL)
3. Select target language (e.g., Hindi)
4. Enable quiz generation
5. Click "Start Localization"
6. You should get a Job ID

Check the worker terminal to see processing in action!

## 💡 Pro Tips

1. **Use PowerShell Tabs:** Instead of 3 separate windows, use tabs in Windows Terminal
2. **Keep Logs Visible:** Arrange terminals side-by-side to monitor all services
3. **GPU Acceleration:** If you have an NVIDIA GPU, set `USE_GPU=true` in `backend/.env`
4. **Auto-restart:** Changes to Python code auto-reload when using `--reload` flag

## 🚀 Next Steps

1. Complete the setup using `.\scripts\setup.bat`
2. Start all 3 services
3. Test the application at http://localhost:3000
4. Read [NATIVE_DEPLOYMENT.md](docs/NATIVE_DEPLOYMENT.md) for advanced features

## ❓ Need Help?

- Check [NATIVE_DEPLOYMENT.md](docs/NATIVE_DEPLOYMENT.md) for detailed troubleshooting
- Look at terminal output for error messages
- Ensure all prerequisites are properly installed

---

**You now have a fully functional, Docker-free setup!** 🎉

This is perfect for:
- Development on any laptop
- FOSS Hack 2026 submission
- Learning how the system works
- Contributing to the project
