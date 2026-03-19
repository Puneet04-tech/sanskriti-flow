@echo off
REM Sanskriti-Flow Cache Cleanup Script
REM Removes all C drive caches and enforces D drive usage

echo ========================================
echo  CACHE CLEANUP & D-DRIVE ENFORCEMENT
echo ========================================
echo.

setlocal enabledelayedexpansion

REM Function to safely delete directory
echo [1/5] Cleaning C:\Users\%USERNAME% caches...

set "cache_dirs[0]=C:\Users\%USERNAME%\.cache"
set "cache_dirs[1]=C:\Users\%USERNAME%\.torch"
set "cache_dirs[2]=C:\Users\%USERNAME%\.transformers"
set "cache_dirs[3]=C:\Users\%USERNAME%\AppData\Local\torch"
set "cache_dirs[4]=C:\Users\%USERNAME%\AppData\Local\huggingface"
set "cache_dirs[5]=C:\Users\%USERNAME%\AppData\Local\pip\cache"
set "cache_dirs[6]=C:\Users\%USERNAME%\AppData\Local\Temp\hf_*"

for /L %%i in (0,1,6) do (
    if defined cache_dirs[%%i] (
        set "dir=!cache_dirs[%%i]!"
        if exist "!dir!" (
            echo    Removing: !dir!
            rmdir /s /q "!dir!" 2>nul
        )
    )
)

echo    ✓ C drive user caches cleaned

REM Clean system temp that might have model files
echo.
echo [2/5] Cleaning system TEMP directories...
for /d %%d in (C:\Windows\Temp\*hf* C:\Windows\Temp\*torch* C:\Windows\Temp\*transformers*) do (
    if exist "%%d" (
        echo    Removing: %%d
        rmdir /s /q "%%d" 2>nul
    )
)

for /d %%d in (C:\Users\%USERNAME%\AppData\Local\Temp\*hf* C:\Users\%USERNAME%\AppData\Local\Temp\*torch* C:\Users\%USERNAME%\AppData\Local\Temp\*transformers*) do (
    if exist "%%d" (
        echo    Removing: %%d
        rmdir /s /q "%%d" 2>nul
    )
)

echo    ✓ Temp directories cleaned

REM Verify D drive cache structure exists
echo.
echo [3/5] Ensuring D drive cache structure exists...

set "required_dirs[0]=d:\sanskriti-flow\backend\data\cache"
set "required_dirs[1]=d:\sanskriti-flow\backend\data\cache\huggingface"
set "required_dirs[2]=d:\sanskriti-flow\backend\data\cache\huggingface\transformers"
set "required_dirs[3]=d:\sanskriti-flow\backend\data\cache\torch"
set "required_dirs[4]=d:\sanskriti-flow\backend\data\cache\pip"
set "required_dirs[5]=d:\sanskriti-flow\backend\data\cache\matplotlib"
set "required_dirs[6]=d:\sanskriti-flow\backend\data\cache\tmp"
set "required_dirs[7]=d:\sanskriti-flow\backend\data\temp"
set "required_dirs[8]=d:\sanskriti-flow\backend\data\output"
set "required_dirs[9]=d:\sanskriti-flow\backend\data\cache\npm"
set "required_dirs[10]=d:\sanskriti-flow\backend\data\cache\playwright"
set "required_dirs[11]=d:\sanskriti-flow\backend\data\cache\yarn"
set "required_dirs[12]=d:\sanskriti-flow\backend\data\cache\pnpm"

for /L %%i in (0,1,12) do (
    if defined required_dirs[%%i] (
        set "dir=!required_dirs[%%i]!"
        if not exist "!dir!" (
            echo    Creating: !dir!
            mkdir "!dir!" 2>nul
        )
    )
)

echo    ✓ D drive cache directories ready

REM Set system environment variables (permanent)
echo.
echo [4/5] Setting Windows Environment Variables (permanent)...
echo    Note: Some changes may require admin privileges
echo.

setx HF_HOME "d:\sanskriti-flow\backend\data\cache\huggingface" >nul 2>&1
setx TRANSFORMERS_CACHE "d:\sanskriti-flow\backend\data\cache\huggingface\transformers" >nul 2>&1
setx TORCH_HOME "d:\sanskriti-flow\backend\data\cache\torch" >nul 2>&1
setx XDG_CACHE_HOME "d:\sanskriti-flow\backend\data\cache" >nul 2>&1
setx TMPDIR "d:\sanskriti-flow\backend\data\cache\tmp" >nul 2>&1
setx TEMP "d:\sanskriti-flow\backend\data\cache\tmp" >nul 2>&1
setx TMP "d:\sanskriti-flow\backend\data\cache\tmp" >nul 2>&1
setx PIP_CACHE_DIR "d:\sanskriti-flow\backend\data\cache\pip" >nul 2>&1
setx MPLCONFIGDIR "d:\sanskriti-flow\backend\data\cache\matplotlib" >nul 2>&1
setx NPM_CONFIG_CACHE "d:\sanskriti-flow\backend\data\cache\npm" >nul 2>&1
setx PLAYWRIGHT_BROWSERS_PATH "d:\sanskriti-flow\backend\data\cache\playwright" >nul 2>&1
setx YARN_CACHE_FOLDER "d:\sanskriti-flow\backend\data\cache\yarn" >nul 2>&1
setx PNPM_STORE_PATH "d:\sanskriti-flow\backend\data\cache\pnpm" >nul 2>&1
setx PUPPETEER_CACHE_DIR "d:\sanskriti-flow\backend\data\cache\playwright" >nul 2>&1

echo    ✓ Environment variables set
echo    Note: CMD windows may need to be restarted to see changes

REM Show final status
echo.
echo [5/5] Verification...
echo.
echo C Drive caches to be removed:
echo    - C:\Users\%USERNAME%\.cache (HuggingFace default)
echo    - C:\Users\%USERNAME%\.torch (PyTorch default)
echo    - C:\Users\%USERNAME%\AppData\Local\pip (pip cache)
echo    - System TEMP directories
echo.
echo D Drive caches (ACTIVE):
echo    - d:\sanskriti-flow\backend\data\cache\huggingface (HF_HOME)
echo    - d:\sanskriti-flow\backend\data\cache\torch (TORCH_HOME)
echo    - d:\sanskriti-flow\backend\data\cache\pip (PIP_CACHE_DIR)
echo    - d:\sanskriti-flow\backend\data\cache\tmp (TEMP/TMP/TMPDIR)
echo.

echo ========================================
echo  CLEANUP COMPLETE
echo ========================================
echo.
echo NEXT STEPS:
echo   1. Restart your terminal/PowerShell windows
echo   2. Run: startup-all.bat (in d:\sanskriti-flow\scripts\)
echo   3. All services will start with D drive caches only
echo.

pause
