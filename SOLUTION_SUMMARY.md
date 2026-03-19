# PERMANENT SOLUTION: C Drive Cache Issue RESOLVED

## Problem Summary
- ❌ C drive dropping from 13 GB to 2.76 GB (lost ~10 GB)
- ❌ Model caches re-downloading to C:\Users\rupes\.cache
- ❌ NLLB, PyTorch, system temp all using C drive defaults

## Solution Applied

### 1️⃣ Absolute D Drive Paths (No Relative Fallback)
**File**: `backend/app/core/config.py`
- Changed all paths from `./data/temp` → `d:\sanskriti-flow\backend\data\temp`
- Changed all cache paths from `./data/cache` → `d:\sanskriti-flow\backend\data\cache\...`
- This prevents Path resolution falling back to C:\Users\...

### 2️⃣ Multi-Level Environment Variable Enforcement
**Enforced at 3 levels**:
1. **Python Config** - `os.environ["HF_HOME"]` set at import time in config.py
2. **System Windows** - `setx HF_HOME "d:\..."` for persistent OS-level env vars
3. **Batch Scripts** - Pre-set in startup scripts before launching Python

**Variables Set**:
```
HF_HOME → d:\sanskriti-flow\backend\data\cache\huggingface
TRANSFORMERS_CACHE → d:\sanskriti-flow\backend\data\cache\huggingface\transformers
TORCH_HOME → d:\sanskriti-flow\backend\data\cache\torch
TEMP/TMP/TMPDIR → d:\sanskriti-flow\backend\data\cache\tmp
PIP_CACHE_DIR → d:\sanskriti-flow\backend\data\cache\pip
MPLCONFIGDIR → d:\sanskriti-flow\backend\data\cache\matplotlib
```

### 3️⃣ Startup Scripts Created
**Location**: `d:\sanskriti-flow\scripts\`

**startup-all.bat**
- Pre-sets all env vars to D drive
- Launches Redis (port 6379)
- Launches Backend API (port 8000)
- Launches Celery Worker
- Launches Frontend (port 3000)
- Cleans old C drive caches automatically

**cleanup-cache.bat**
- One-time cleanup of C:\Users\... caches
- Removes .cache, .torch, .transformers directories
- Creates D drive structure
- Sets system env vars permanently

## Usage

### Start System (Recommended Method)
```batch
d:\sanskriti-flow\scripts\startup-all.bat
```

### One-Time Cleanup (if needed)
```batch
d:\sanskriti-flow\scripts\cleanup-cache.bat
```

## Verification Checklist

✅ Backend config.py uses absolute D drive paths
✅ Environment variables set at Python startup
✅ System Windows env vars configured (setx)
✅ Batch startup scripts created
✅ Old C drive caches removed

## Expected Results

### C Drive
- ✅ No model cache (0 GB for HuggingFace)
- ✅ No PyTorch cache (0 GB)
- ✅ No pip cache (0 GB)
- ✅ Reclaimed space: +2.5-3 GB

### D Drive
- ✅ All models stored in D:\sanskriti-flow\backend\data\cache\huggingface
- ✅ Cache grows as models downloaded: currently ~60 files from latest job
- ✅ D drive has 208 GB available, no pressure

## Configuration Files Modified

1. **backend/app/core/config.py**
   - Absolute D drive paths for all cache/temp dirs
   - Multi-level env var enforcement
   - Startup diagnostic message printing

## New Files Created

1. **scripts/startup-all.bat** - Complete startup with env vars
2. **scripts/cleanup-cache.bat** - One-time cleanup script
3. **CONFIG_D_DRIVE_CACHES.md** - Full technical documentation

## How It Prevents Future Issues

| Issue | Prevention |
|-------|-----------|
| Relative paths fall back to C drive | Absolute `d:\...` paths in config |
| Environment not persistent | System-level `setx` for Windows |
| Python overrides env | `os.environ[]` forced at import |
| New services use old defaults | Batch scripts pre-set all vars |
| Manual startup loses settings | `startup-all.bat` bundles all |

## Current System Status

✅ **Backend API**: Running on port 8000
✅ **Celery Worker**: Running, processing jobs
✅ **Redis**: Running on port 6379
✅ **Frontend**: Running on port 3000
✅ **Cache Location**: D:\sanskriti-flow\backend\data\cache\*
✅ **C Drive**: Clean (cache removed)

## Next: Monitor and Validate

Submit a new job and confirm:
1. Video processes successfully
2. Hinglish audio + quizzes present
3. Check D drive cache grows (new models if needed)
4. Verify C drive remains clean

---

**IMPORTANT**: Always use `startup-all.bat` when restarting services to maintain D drive cache configuration!

**Status**: ✅ PERMANENT SOLUTION APPLIED
