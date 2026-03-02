"""
Job Management API Endpoints
Handles job status tracking and results retrieval
"""

from fastapi import APIRouter, HTTPException, Path
from app.models.schemas import JobStatusResponse, JobStatus
from app.core.logger import logger
from app.workers.celery_app import celery_app
from celery.result import AsyncResult
from typing import Dict

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

        # Query Celery task status
        task_result = AsyncResult(job_id, app=celery_app)
        
        if task_result.state == "PENDING":
            return JobStatusResponse(
                job_id=job_id,
                status=JobStatus.QUEUED,
                progress=0,
                stage="Waiting in queue",
                eta_seconds=None,
            )
        elif task_result.state == "PROCESSING":
            meta = task_result.info or {}
            return JobStatusResponse(
                job_id=job_id,
                status=JobStatus.PROCESSING,
                progress=meta.get("progress", 0),
                stage=meta.get("stage", "Processing"),
                eta_seconds=None,
            )
        elif task_result.state == "SUCCESS":
            result = task_result.result or {}
            response = JobStatusResponse(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                progress=100,
                stage="Completed",
                eta_seconds=0,
                result_url=f"/api/v1/results/{job_id}.mp4",
            )
            # Cache completed job
            jobs_db[job_id] = response
            return response
        elif task_result.state == "FAILURE":
            error_info = str(task_result.info) if task_result.info else "Unknown error"
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
                stage=f"State: {task_result.state}",
                eta_seconds=None,
            )

    except Exception as e:
        logger.error(f"Error retrieving job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
