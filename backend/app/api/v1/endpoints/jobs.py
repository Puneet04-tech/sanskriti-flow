"""
Job Management API Endpoints
Handles job status tracking and results retrieval
"""

from fastapi import APIRouter, HTTPException, Path
from app.models.schemas import JobStatusResponse, JobStatus
from app.core.logger import logger
from app.core.config import settings
from app.workers.celery_app import celery_app
from celery.result import AsyncResult
from typing import Dict
import os
import json

router = APIRouter()

# Temporary in-memory job storage for completed jobs
jobs_db: Dict[str, JobStatusResponse] = {}


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str = Path(..., description="Job ID to query")):
    """
    Get the status of a localization job

    Returns the current processing status, progress, and result URL when complete.
    """
    try:
        # Check if job is in completed cache
        if job_id in jobs_db:
            return jobs_db[job_id]
        
        # Check if output file exists (job completed but not in cache)
        output_file = os.path.join(settings.OUTPUT_DIR, f"{job_id}.mp4")
        if os.path.exists(output_file):
            logger.info(f"Found completed job file for {job_id}")
            
            # Try to retrieve quizzes and metadata from Celery result
            quizzes = []
            metadata = {}
            try:
                task_result = AsyncResult(job_id, app=celery_app)
                if task_result.state == "SUCCESS":
                    result = task_result.result or {}
                    quizzes = result.get("quizzes", [])
                    metadata = result.get("metadata", {})
            except Exception as e:
                logger.warning(f"Could not retrieve quiz data for {job_id}: {e}")

            # Fallback: read persisted metadata from sidecar JSON
            if not quizzes and not metadata:
                try:
                    result_meta_path = os.path.join(settings.OUTPUT_DIR, f"{job_id}.json")
                    if os.path.exists(result_meta_path):
                        with open(result_meta_path, "r", encoding="utf-8") as result_file:
                            persisted = json.load(result_file)
                        quizzes = persisted.get("quizzes", [])
                        metadata = persisted.get("metadata", {})
                except Exception as e:
                    logger.warning(f"Could not read persisted metadata for {job_id}: {e}")
            
            response = JobStatusResponse(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                progress=100,
                stage="Completed",
                eta_seconds=0,
                result_url=f"{settings.BACKEND_URL}/api/v1/results/{job_id}.mp4",
                quizzes=quizzes,
                metadata=metadata,
            )
            jobs_db[job_id] = response
            return response

        # Query Celery task status
        task_result = AsyncResult(job_id, app=celery_app)
        
        # Safely get task state
        try:
            task_state = task_result.state
        except Exception:
            # Task doesn't exist or can't get state
            return JobStatusResponse(
                job_id=job_id,
                status=JobStatus.QUEUED,
                progress=0,
                stage="Status unavailable",
                eta_seconds=None,
            )
        
        # Check if task exists at all (PENDING could mean non-existent or queued)
        # If PENDING and no output file, might be truly non-existent
        if task_state == "PENDING":
            # Try to check if task was ever registered
            # PENDING is Celery's default state for unknown tasks
            return JobStatusResponse(
                job_id=job_id,
                status=JobStatus.QUEUED,
                progress=0,
                stage="Waiting in queue",
                eta_seconds=None,
            )
        elif task_state == "PROCESSING":
            try:
                meta = task_result.info or {}
            except Exception:
                meta = {}
            return JobStatusResponse(
                job_id=job_id,
                status=JobStatus.PROCESSING,
                progress=meta.get("progress", 0),
                stage=meta.get("stage", "Processing"),
                eta_seconds=None,
            )
        elif task_state == "SUCCESS":
            try:
                result = task_result.result or {}
            except Exception:
                result = {}
            
            # Extract quizzes and metadata from task result
            quizzes = result.get("quizzes", [])
            metadata = result.get("metadata", {})
            
            response = JobStatusResponse(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                progress=100,
                stage="Completed",
                eta_seconds=0,
                result_url=f"{settings.BACKEND_URL}/api/v1/results/{job_id}.mp4",
                quizzes=quizzes,
                metadata=metadata,
            )
            # Cache completed job
            jobs_db[job_id] = response
            return response
        elif task_state == "FAILURE":
            try:
                error_info = str(task_result.info) if task_result.info else "Unknown error"
            except Exception:
                error_info = "Task failed with unparseable error"
            return JobStatusResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                progress=0,
                stage="Failed",
                eta_seconds=0,
                error=error_info,
            )
        else:
            # Unknown state
            return JobStatusResponse(
                job_id=job_id,
                status=JobStatus.QUEUED,
                progress=0,
                stage=f"State: {task_state}",
                eta_seconds=None,
            )

    except Exception as e:
        try:
            error_message = str(e)
        except Exception:
            error_message = f"{type(e).__name__}: Unable to get error details"
        logger.error(f"Error retrieving job status for {job_id}: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)


@router.delete("/{job_id}")
async def cancel_job(job_id: str = Path(..., description="Job ID to cancel")):
    """
    Cancel a running localization job

    Stops the processing and cleans up resources.
    """
    try:
        # TODO: Implement job cancellation
        logger.info(f"Cancel requested for job {job_id}")

        return {"job_id": job_id, "status": "cancelled", "message": "Job cancelled"}

    except Exception as e:
        logger.error(f"Error cancelling job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))






@router.get("/health/celery")
async def health_check_celery():
    """
    Check if Celery worker is connected and ready to process tasks
    
    Returns active workers and their status
    """
    try:
        # Ping workers to see if they're responding
        inspector = celery_app.control.inspect(timeout=2)  # 2 second timeout
        
        # Check active workers
        stats = inspector.stats()
        active_workers = inspector.active()
        
        if not stats or not active_workers:
            logger.warning("No Celery workers connected")
            return {
                "status": "disconnected",
                "workers": [],
                "message": "No active Celery workers found. Worker may not be started yet.",
            }
        
        worker_info = []
        for worker_name, worker_stats in stats.items():
            worker_info.append({
                "name": worker_name,
                "pool": worker_stats.get("pool", {}).get("implementation", "unknown"),
                "max_concurrency": worker_stats.get("pool", {}).get("max-concurrency", 1),
                "active_tasks": len(active_workers.get(worker_name, [])),
            })
        
        logger.info(f"Celery health check: {len(worker_info)} workers connected")
        
        return {
            "status": "connected",
            "workers": worker_info,
            "message": f"{len(worker_info)} worker(s) ready for tasks",
        }
    
    except Exception as e:
        logger.warning(f"Celery health check failed: {str(e)}")
        return {
            "status": "error",
            "workers": [],
            "message": f"Failed to connect to Celery workers: {str(e)}",
        }

@router.get("/health/queues")
async def health_check_queues():
    """
    Diagnostic endpoint: Check queue status and stuck tasks
    
    Returns information about queued and active tasks
    """
    try:
        inspector = celery_app.control.inspect(timeout=2)
        
        # Get queues with reserved tasks and active tasks
        active_tasks = inspector.active() or {}
        reserved_tasks = inspector.reserved() or {}
        scheduled_tasks = inspector.scheduled() or {}
        
        total_active = sum(len(v) for v in active_tasks.values())
        total_reserved = sum(len(v) for v in reserved_tasks.values())
        total_scheduled = sum(len(v) for v in scheduled_tasks.values())
        
        logger.info(f"Queue status - Active: {total_active}, Reserved: {total_reserved}, Scheduled: {total_scheduled}")
        
        return {
            "status": "ok",
            "active_tasks": total_active,
            "reserved_tasks": total_reserved,
            "scheduled_tasks": total_scheduled,
            "workers_responding": len(active_tasks),
            "message": f"Queue has {total_active} active, {total_reserved} reserved, {total_scheduled} scheduled tasks",
        }
    
    except Exception as e:
        logger.warning(f"Queue health check failed: {str(e)}")
        return {
            "status": "error",
            "active_tasks": 0,
            "reserved_tasks": 0,
            "scheduled_tasks": 0,
            "workers_responding": 0,
            "message": str(e),
        }




@router.get("/")
async def list_jobs():
    """
    List all jobs (for admin/debugging)

    Returns a list of all jobs with their current status.
    """
    try:
        # TODO: Query all jobs from database
        return {"jobs": list(jobs_db.values()), "total": len(jobs_db)}

    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
