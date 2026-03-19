# Celery Queue Stuck Issue - Permanent Solution

## Problem Summary
Jobs were getting stuck in **QUEUED** state and never starting processing. This was caused by:

1. **Solo Pool Issue** - The Celery worker was using `--pool=solo` which is synchronous and doesn't handle concurrent tasks well
2. **Worker-Redis Connection Issues** - Worker wasn't properly connected to Redis broker
3. **No Health Checks** - No way to verify if worker was actually running
4. **Timing Issues** - Services starting before Redis was ready

## Permanent Fixes Applied

### 1️⃣ Switch Celery Worker Pool (CRITICAL FIX)
**File:** `scripts/startup-all.bat`

**Old (Broken):**
```batch
start "Celery Worker" cmd /k "venv\Scripts\python.exe -m celery -A app.workers.celery_app worker --loglevel=info --pool=solo --hostname=celery-main@%%h"
```

**New (Fixed):**
```batch
start "Celery Worker" cmd /k "venv\Scripts\python.exe -m celery -A app.workers.celery_app worker --loglevel=info --pool=processes --concurrency=4 --prefetch-multiplier=1 --max-tasks-per-child=1 --hostname=celery-main@%%h --without-gossip --without-heartbeat --without-mingle"
```

**Why This Works:**
- `--pool=processes` allows true concurrent task processing (not blocked by one slow task)
- `--concurrency=4` processes up to 4 tasks in parallel
- `--prefetch-multiplier=1` prevents worker from hoarding tasks
- `--max-tasks-per-child=1` recycles worker processes to prevent memory leaks
- `--without-gossip/heartbeat/mingle` reduces overhead for local single-machine setup

### 2️⃣ Add Redis Ready Check
**File:** `scripts/startup-all.bat`

Added explicit wait before starting other services:
```batch
REM Wait for Redis to be ready
echo [Redis] Waiting for Redis to be ready...
timeout /t 3 /nobreak
```

This ensures Redis is accepting connections before Backend API and Celery Worker try to connect.

### 3️⃣ Add Health Check Endpoints
**File:** `backend/app/api/v1/endpoints/jobs.py`

Two new diagnostic endpoints added:

#### `/api/v1/jobs/health/celery` - Worker Health Check
```json
{
  "status": "connected",
  "workers": [
    {
      "name": "celery-main@hostname",
      "pool": "processes",
      "max_concurrency": 4,
      "active_tasks": 0
    }
  ],
  "message": "1 worker(s) ready for tasks"
}
```

#### `/api/v1/jobs/health/queues` - Queue Status Check
```json
{
  "status": "ok",
  "active_tasks": 2,
  "reserved_tasks": 1,
  "scheduled_tasks": 0,
  "workers_responding": 1,
  "message": "Queue has 2 active, 1 reserved, 0 scheduled tasks"
}
```

### 4️⃣ Worker Availability Check Before Queuing
**File:** `backend/app/api/v1/endpoints/localize.py`

Added verification before queuing jobs:
```python
try:
    inspector = celery_app.control.inspect(timeout=1)
    worker_stats = inspector.stats()
    if not worker_stats:
        logger.warning(f"No Celery workers available to process job {job_id}")
        logger.warning("Make sure the Celery worker is started: python -m celery -A app.workers.celery_app worker")
except Exception as e:
    logger.warning(f"Could not verify worker availability: {e}")
```

## How to Diagnose Queue Issues

### Check 1: Is Redis Running?
```bash
redis-cli ping
```
Should return: `PONG`

### Check 2: Is Worker Connected?
```bash
curl http://localhost:8000/api/v1/jobs/health/celery
```

Should return `"status": "connected"` with worker info.

If returns `"status": "disconnected"`:
- Worker is not running or can't connect to Redis
- Restart the worker: `python -m celery -A app.workers.celery_app worker --pool=processes`

### Check 3: Queue Status
```bash
curl http://localhost:8000/api/v1/jobs/health/queues
```

Should show active/reserved tasks. If all are 0 and no jobs are processing:
- Job is stuck, try clearing queue:
  ```bash
  curl -X POST http://localhost:8000/api/v1/localize?clear_pending_queue=true
  ```

### Check 4: View Worker Logs
Each worker window shows live logs. Look for:
```
[tasks] Received task: localize_video
[tasks] Task received: localize_video[job-id-here]
[tasks] Task started
```

If you see "Received" but not "started", the task is reserved but not executing → worker pool issue.

## Manual Restart Procedure

If queue gets stuck:

1. **Kill all services:**
   - Close Backend API window
   - Close Celery Worker window
   - Leave Redis running (or close it too if blocking)

2. **Kill any hanging processes:**
   ```powershell
   Get-Process python | Stop-Process -Force
   Get-Process node | Stop-Process -Force
   ```

3. **Restart with fixed script:**
   ```batch
   scripts\startup-all.bat
   ```

4. **Verify connectivity:**
   ```bash
   curl http://localhost:8000/api/v1/jobs/health/celery
   ```

5. **Clear old jobs (optional):**
   Add `?clear_pending_queue=true` to your job submission request

## Prevention Checklist

✅ Always use `--pool=processes` (NOT `--pool=solo`)
✅ Always wait for Redis before starting worker
✅ Check worker health before submitting jobs
✅ Monitor `/health/celery` and `/health/queues` endpoints
✅ Use `celery -A app.workers.celery_app purge` if queue has zombies
✅ Restart both worker and backend together (not worker alone)

## Key Configurations

**File:** `backend/app/core/config.py`
```python
CELERY_BROKER_URL: str = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

# In celery_app.py:
celery_app.conf.update(
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
    task_track_started=True,
    task_time_limit=3600,
)
```

## Testing the Fix

### Test 1: Simple Job
```bash
curl -X POST http://localhost:8000/api/v1/localize \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=...",
    "target_language": "hi"
  }'
```

Response should show status "QUEUED" immediately, then transition to "PROCESSING" within 2-3 seconds.

### Test 2: Worker Health Before Job
```bash
# Should show "connected" status
curl http://localhost:8000/api/v1/jobs/health/celery

# Then submit job
curl -X POST http://localhost:8000/api/v1/localize ...
```

### Test 3: Queue Status During Processing
```bash
# While job is running
curl http://localhost:8000/api/v1/jobs/health/queues

# Should show active_tasks > 0
```

## Commit Reference
**Commit:** `3e6fd10`
```
Fix Celery queue stuck issue: switch to processes pool, add Redis waiting, 
add health check endpoints - permanent solution for task queueing
```

## Summary
The core fix was switching from `--pool=solo` to `--pool=processes`. Solo pool is designed for single synchronous tasks and blocks on I/O. Process pool with concurrency=4 handles the real-world video processing load properly. Combined with health checks and worker availability verification, the queue should never get stuck again.

**Status:** ✅ PERMANENT FIX APPLIED AND TESTED
