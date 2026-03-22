@echo off
cd /d d:\sanskriti-flow\backend
set "HF_HOME=d:\sanskriti-flow\backend\data\cache\huggingface"
set "TRANSFORMERS_CACHE=d:\sanskriti-flow\backend\data\cache\huggingface\transformers"
set "TORCH_HOME=d:\sanskriti-flow\backend\data\cache\torch"
set "PYTHONPATH=d:\sanskriti-flow\backend"
echo [Backend] Starting on port 8000 (Quick Mode)...
D:\sanskriti-flow\backend\venv\Scripts\python.exe -m uvicorn main_working:app --host 0.0.0.0 --port 8000
