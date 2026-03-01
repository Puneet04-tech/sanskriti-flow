"""
Job Management API Endpoints
Handles job status tracking and results retrieval
"""

from fastapi import APIRouter, HTTPException, Path
from app.models.schemas import JobStatusResponse, JobStatus
from app.core.logger import logger
from typing import Dict

router = APIRouter()

# Temporary in-memory job storage (will be replaced with Redis)
jobs_db: Dict[str, JobStatusResponse] = {}


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str = Path(..., description="Job ID to query")):
    """
    Get the status of a localization job

    Returns the current processing status, progress, and result URL when complete.
    """
    try:
        # TODO: Query actual job status from Celery/Redis
        # For now, return mock status
        if job_id in jobs_db:
            return jobs_db[job_id]

        # Mock response for demo
        return JobStatusResponse(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress=45.5,
            stage="Translating transcript",
            eta_seconds=120,
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
