@echo off
cd /d d:\sanskriti-flow\backend
set "HF_HOME=d:\sanskriti-flow\backend\data\cache\huggingface"
set "TRANSFORMERS_CACHE=d:\sanskriti-flow\backend\data\cache\huggingface\transformers"
set "TORCH_HOME=d:\sanskriti-flow\backend\data\cache\torch"
set "PYTHONPATH=d:\sanskriti-flow\backend"
echo [Celery Worker] Starting with 8 concurrent tasks...
D:\sanskriti-flow\backend\venv\Scripts\python.exe -m celery -A app.workers.celery_app worker --loglevel=info --pool=threads --concurrency=8 --prefetch-multiplier=1
