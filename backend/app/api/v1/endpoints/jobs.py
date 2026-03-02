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
