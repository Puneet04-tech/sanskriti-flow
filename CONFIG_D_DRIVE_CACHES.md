# Sanskriti-Flow D Drive Cache Configuration

## Overview
This document explains how all ML model caches and temporary files are configured to use the D drive instead of the C drive, preventing C drive space issues.

## Problem Statement
- **Before Fix**: HuggingFace models, PyTorch caches, and system temp files were storing on C:\Users\{user}\.cache
- **Space Impact**: Models consume 2.5-3 GB
- **C Drive Status**: Going from 13 GB free → 2.76 GB free (losing ~10 GB)
- **Solution**: Force ALL caches to D drive with absolute paths and system-level environment variables

## Configuration Applied

### 1. Backend Code Changes (`app/core/config.py`)

**Absolute D Drive Paths** (not relative):
```python
TEMP_DIR: str = "d:\\sanskriti-flow\\backend\\data\\temp"
OUTPUT_DIR: str = "d:\\sanskriti-flow\\backend\\data\\output"
CACHE_DIR: str = "d:\\sanskriti-flow\\backend\\data\\cache"
TMP_DIR: str = "d:\\sanskriti-flow\\backend\\data\\cache\\tmp"

# ML Cache Directories
HF_HOME: str = "d:\\sanskriti-flow\\backend\\data\\cache\\huggingface"
TRANSFORMERS_CACHE: str = "d:\\sanskriti-flow\\backend\\data\\cache\\huggingface\\transformers"
TORCH_HOME: str = "d:\\sanskriti-flow\\backend\\data\\cache\\torch"
XDG_CACHE_HOME: str = "d:\\sanskriti-flow\\backend\\data\\cache"
```

**Environment Variables** (forced at Python startup):
```python
os.environ["HF_HOME"] = "d:\\sanskriti-flow\\backend\\data\\cache\\huggingface"
os.environ["TRANSFORMERS_CACHE"] = "d:\\sanskriti-flow\\backend\\data\\cache\\huggingface\\transformers"
os.environ["TORCH_HOME"] = "d:\\sanskriti-flow\\backend\\data\\cache\\torch"
os.environ["XDG_CACHE_HOME"] = "d:\\sanskriti-flow\\backend\\data\\cache"
os.environ["TMPDIR"] = "d:\\sanskriti-flow\\backend\\data\\cache\\tmp"
os.environ["TEMP"] = "d:\\sanskriti-flow\\backend\\data\\cache\\tmp"
os.environ["TMP"] = "d:\\sanskriti-flow\\backend\\data\\cache\\tmp"
os.environ["PIP_CACHE_DIR"] = "d:\\sanskriti-flow\\backend\\data\\cache\\pip"
os.environ["MPLCONFIGDIR"] = "d:\\sanskriti-flow\\backend\\data\\cache\\matplotlib"
```

### 2. Environment Variable Enforcement

**System Level** (Windows):
```batch
setx HF_HOME "d:\sanskriti-flow\backend\data\cache\huggingface"
setx TRANSFORMERS_CACHE "d:\sanskriti-flow\backend\data\cache\huggingface\transformers"
setx TORCH_HOME "d:\sanskriti-flow\backend\data\cache\torch"
setx XDG_CACHE_HOME "d:\sanskriti-flow\backend\data\cache"
setx TMPDIR "d:\sanskriti-flow\backend\data\cache\tmp"
setx TMP "d:\sanskriti-flow\backend\data\cache\tmp"
setx TEMP "d:\sanskriti-flow\backend\data\cache\tmp"
setx PIP_CACHE_DIR "d:\sanskriti-flow\backend\data\cache\pip"
setx MPLCONFIGDIR "d:\sanskriti-flow\backend\data\cache\matplotlib"
```

### 3. Startup Scripts

**Location**: `d:\sanskriti-flow\scripts\`

**Files**:
- `startup-all.bat` - Launches all 4 services with D drive env vars pre-set
- `cleanup-cache.bat` - Removes C drive caches and enforces D drive setup

## Directory Structure

```
D:\sanskriti-flow\backend\data\
├── cache/
│   ├── huggingface/          ← HuggingFace models (facebook/nllb-200, etc)
│   │   └── transformers/     ← Transformers library cache
│   ├── torch/                ← PyTorch models and cache
│   ├── pip/                  ← Pip package cache
│   ├── matplotlib/           ← Matplotlib config
│   └── tmp/                  ← Temporary files (TEMP, TMP, TMPDIR)
├── temp/                     ← Video processing temporary files
└── output/                   ← Final localized video output
```

## Verification

### Check D Drive Usage
```powershell
Get-ChildItem "d:\sanskriti-flow\backend\data\cache" -Recurse | Measure-Object
```

### Check C Drive (should be empty)
```powershell
Test-Path "C:\Users\rupes\.cache"  # Should return False
```

### Verify Environment Variables
```powershell
$env:HF_HOME
$env:TORCH_HOME
$env:TEMP
```

## Startup Instructions

### Option 1: Batch Script (Recommended)
```batch
cd d:\sanskriti-flow\scripts
startup-all.bat
```

### Option 2: Manual Startup with Env Vars

**PowerShell**:
```powershell
# Set environment variables
$env:HF_HOME = "d:\sanskriti-flow\backend\data\cache\huggingface"
$env:TRANSFORMERS_CACHE = "d:\sanskriti-flow\backend\data\cache\huggingface\transformers"
$env:TORCH_HOME = "d:\sanskriti-flow\backend\data\cache\torch"
$env:TMPDIR = "d:\sanskriti-flow\backend\data\cache\tmp"
$env:TEMP = "d:\sanskriti-flow\backend\data\cache\tmp"
$env:TMP = "d:\sanskriti-flow\backend\data\cache\tmp"

# Start services
Set-Location "d:\sanskriti-flow\backend"
& ".\venv\Scripts\python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Key Points

✅ **Absolute Paths**: Using `d:\...` prevents relative path resolution to C drive
✅ **Multi-Level Enforcement**: Environment vars set in:
   1. `config.py` (Python level)
   2. System environment (Windows level)
   3. Batch scripts (subprocess level)

✅ **All Tools Covered**:
   - HuggingFace Transformers → `HF_HOME`
   - PyTorch → `TORCH_HOME`
   - Pip → `PIP_CACHE_DIR`
   - System Temp → `TEMP`, `TMP`, `TMPDIR`
   - Matplotlib → `MPLCONFIGDIR`

✅ **Permanent**: Changes persist across restarts and new terminal windows

## Cleanup Commands

**Remove C drive caches (one-time)**:
```batch
rmdir /s /q "C:\Users\%USERNAME%\.cache" 2>nul
rmdir /s /q "C:\Users\%USERNAME%\.torch" 2>nul
```

Or use the provided script:
```batch
cd d:\sanskriti-flow\scripts
cleanup-cache.bat
```

## Expected Space Usage

### D Drive (Expected)
- HuggingFace models: ~2.5 GB
- PyTorch cache: ~100-200 MB
- Processing videos: Variable (per job)
- Pip cache: ~50-100 MB

### C Drive
- After cleanup: Minimal (0 MB for project)
- No model cache storage

## Monitoring

To monitor where caches are being written:
```powershell
# Watch HF cache
Get-ChildItem "d:\sanskriti-flow\backend\data\cache\huggingface" -Recurse | Select-Object -Last 20

# Check if anything sneaks to C drive
Get-ChildItem "C:\Users\rupes" -Include ".cache", ".torch", ".transformers" -Recurse -Hidden
```

## Troubleshooting

**Problem**: Files still appearing on C drive
**Solution**: 
1. Kill all Python processes
2. Run `cleanup-cache.bat`
3. Restart services using `startup-all.bat`

**Problem**: "Permission denied" when removing C drive cache
**Solution**: Run Command Prompt/PowerShell as Administrator

**Problem**: Environment variable not taking effect
**Solution**:
1. Restart all terminal windows
2.veRify with `echo %HF_HOME%` (CMD) or `$env:HF_HOME` (PowerShell)
3. Check `app/core/config.py` is printing config on startup

## Last Configuration Date
**2026-03-16** - Updated with absolute D drive paths and comprehensive enforcement

---

**Remember**: Always start services using the scripts in `d:\sanskriti-flow\scripts\` to ensure D drive caches are active!
