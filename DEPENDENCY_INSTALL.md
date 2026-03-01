# Dependency Installation Status & Troubleshooting

## Installation Summary

### Frontend ✅
**Status:** Installing...
- Location: `d:\sanskriti-flow\frontend`
- Command: `npm install`
- Expected: All Next.js, React, and TypeScript dependencies

### Backend ⚠️
**Status:** Partial - 2 packages require additional setup
- Location: `d:\sanskriti-flow\backend`
- Virtual Environment: Created at `d:\sanskriti-flow\backend\venv`

## Backend Dependency Issues

### Issue 1: ` llama-cpp-python` (LLM Quiz Generation)
**Error:** Requires CMake and C++ compiler  
**Reason:** Needs to compile C++ code from source  
**Solutions:**

#### Option A: Install Microsoft Visual C++ (Recommended)
1. Download [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Run installer and select "Desktop development with C++"
3. After installation, restart PowerShell
4. Run: 
```powershell
cd d:\sanskriti-flow\backend
.\venv\Scripts\Activate.ps1
pip install llama-cpp-python==0.2.27
```

#### Option B: Use Pre-built Wheel
```powershell
pip install llama-cpp-python --prefer-binary
```

#### Option C: Skip (Disable Quiz Generation Feature)
- Quiz generation will not work without this package
- All other features will function normally
- Update `backend/app/services/quiz_generator.py` to check if package is available

### Issue 2: `av` (Video/Audio Processing - faster-whisper dependency)
**Error:** Path too long during wheel building  
**Reason:** Windows path length limitations + compilation requirements  
**Solutions:**

#### Option A: Install from Pre-built Wheel
```powershell
pip install av --prefera binary
```

#### Option B: Use Conda (Alternative)
```powershell
conda install av -c conda-forge
```

#### Option C: Manual Installation
1. Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Enable long paths in Windows:
   - Press `Win + R`, type `regedit`
   - Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
   - Set `LongPathsEnabled` to `1`
   - Restart computer
3. Try installation again:
```powershell
pip install av==11.0.0
```

## Working Installation Script

### For Backend (Without Problematic Packages)

```powershell
cd d:\sanskriti-flow\backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install core web framework
pip install fastapi==0.109.0
pip install "uvicorn[standard]==0.27.0"
pip install python-multipart==0.0.6
pip install pydantic==2.5.3
pip install pydantic-settings==2.1.0

# Install async & workers
pip install celery==5.3.6
pip install redis==5.0.1
pip install aiofiles==23.2.1

# Install AI/ML core (this will take time - large downloads)
pip install torch==2.1.2
pip install torchaudio==2.1.2
pip install torchvision==0.16.2
pip install transformers==4.37.0
pip install accelerate==0.26.1

# Install transcription & translation
pip install faster-whisper==0.10.0
pip install ctranslate2==4.0.0

# Install video processing
pip install opencv-python==4.9.0.80
pip install opencv-contrib-python==4.9.0.80
pip install ffmpeg-python==0.2.0
pip install moviepy==1.0.3

# Install vision models
pip install timm==0.9.12
pip install pillow==10.2.0

# Install LangChain (without llama-cpp-python)
pip install langchain==0.1.4
pip install langchain-community==0.0.16

# Install NLP
pip install spacy==3.7.2
python -m spacy download en_core_web_sm

# Install utilities
pip install python-dotenv==1.0.0
pip install python-jose==3.3.0
pip install passlib==1.7.4
pip install httpx==0.26.0
pip install tenacity==8.2.3
pip install pyyaml==6.0.1

# Install development tools
pip install pytest==7.4.4
pip install pytest-asyncio==0.23.3
pip install black==24.1.1
pip install flake8==7.0.0
pip install mypy==1.8.0
```

### For Frontend

```powershell
cd d:\sanskriti-flow\frontend
npm install
```

## Verification Commands

### Check Backend Installation
```powershell
cd d:\sanskriti-flow\backend
.\venv\Scripts\Activate.ps1
pip list | Select-String -Pattern "fastapi|torch|celery|transformers|spacy"
```

### Check Frontend Installation
```powershell
cd d:\sanskriti-flow\frontend
npm list --depth=0
```

## Feature Impact

### If `llama-cpp-python` is NOT installed:
- ❌ Quiz Generation (Llama 3.1) will not work
- ✅ Video Transcription works
- ✅ Translation works
- ✅ Vision-Sync works
- ✅ All other features work

### If `av` is NOT installed:
- ⚠️ faster-whisper may have reduced functionality
- ⚠️ Audio extraction from video may fall back to FFmpeg only
- ✅ Most transcription features still work via FFmpeg

## Recommended Action Plan

### Phase 1: Get Core Features Working (Do This First)
1. Install Microsoft Visual C++ Build Tools (15-20 minutes)
   - [Download here](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Select "Desktop development with C++" workload
   - Restart computer after installation

2. Enable Windows Long Paths
   - Run PowerShell as Administrator:
   ```powershell
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
   -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```
   - Restart computer

3. Install ALL backend dependencies:
   ```powershell
   cd d:\sanskriti-flow\backend
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

### Phase 2: Test Without Problematic Packages
1. Follow the "Working Installation Script" above (skips 2 packages)
2. Frontend is already installing
3. Test basic functionality
4. Add problematic packages later if needed

## System Requirements Check

Before installation, verify:
- [x] Python 3.10+ installed (`python --version`)
- [x] Node.js 18+ installed (`node --version`)
- [ ] Visual C++ Build Tools (for full feature set)
- [ ] FFmpeg in PATH (`ffmpeg -version`)
- [ ] Redis or Memurai running (`redis-cli ping`)

## Quick Test After Installation

```powershell
# Terminal 1 - Backend
cd d:\sanskriti-flow\backend
.\venv\Scripts\Activate.ps1
python -c "import fastapi, torch, transformers, spacy; print('Core packages OK')"
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Worker
cd d:\sanskriti-flow\backend
.\venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker --loglevel=info --pool=solo

# Terminal 3 - Frontend  
cd d:\sanskriti-flow\frontend
npm run dev
```

## Support Resources

- **Visual C++ Build Tools:** https://visualstudio.microsoft.com/visual-cpp-build-tools/
- **FFmpeg Installation:** https://ffmpeg.org/download.html#build-windows
- **Memurai (Redis for Windows):** https://www.memurai.com/get-memurai
- **PyTorch Installation:** https://pytorch.org/get-started/ locally/

## Notes

- **Installation Time:** 
  - Frontend: ~2-3 minutes
  - Backend (without build tools): ~15-20 minutes
  - Backend (full with C++ packages): ~30-40 minutes
  
- **Disk Space Required:**
  - Frontend: ~400 MB
  - Backend: ~5-8 GB (PyTorch models are large)
  - AI Models (downloaded at runtime): ~10-15 GB

- **Alternatives:**
  - Can use CPU-only PyTorch (remove CUDA dependencies)
  - Can disable specific features if dependencies fail
  - Can use Docker if laptop supports it (but you mentioned incompatibility)
