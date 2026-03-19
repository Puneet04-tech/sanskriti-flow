"""
Localization API Endpoints
Handles video localization requests
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.schemas import (
    LocalizationRequest,
    JobResponse,
    JobStatus,
    LanguageCode,
)
from app.core.logger import logger
from app.workers.tasks import localize_video_task
from app.workers.celery_app import celery_app
import uuid
import os

router = APIRouter()


@router.post("/", response_model=JobResponse)
async def create_localization_job(request: LocalizationRequest):
    """
    Create a new video localization job

    This endpoint accepts a video URL or file and queues it for localization
    with the specified target language and features.

    **Features:**
    - Neural Hinglish Engine (preserves technical terms)
    - Zero-Shot Voice Cloning
    - Vision-Sync Overlays (optional)
    - Neural Mirroring/Lip-Sync (optional)
    - Interactive Quiz Generation (optional)
    - Swar Assistive Audio (optional)
    - Drishti Rural Mode (optional)
    """
    try:
        # Validate input
        if not request.video_url and not request.video_file:
            raise HTTPException(
                status_code=400,
                detail="Either video_url or video_file must be provided",
            )

        # Generate unique job ID
        job_id = str(uuid.uuid4())

        logger.info(
            f"Created localization job {job_id} for language {request.target_language}"
        )

        # Prepare job options
        options = {
            "enable_quiz": request.enable_quiz,
            "enable_vision_sync": request.enable_vision_sync,
            "enable_lip_sync": request.enable_lip_sync,
            "enable_voice_clone": request.enable_voice_clone,
            "enable_explainer": request.enable_explainer,
            "enable_swar": request.enable_swar,
            "enable_drishti": request.enable_drishti,
            "preserve_technical_terms": True,
        }

        # Convert URL to string for JSON serialization
        video_url_str = str(request.video_url) if request.video_url else request.video_file

        # Permanent queue control for local single-user workflow:
        # clear stale pending jobs so fresh requests don't get blocked behind old backlog.
        if request.clear_pending_queue:
            try:
                purged_count = celery_app.control.purge() or 0
                if purged_count > 0:
                    logger.warning(
                        f"Purged {purged_count} pending queued task(s) before enqueuing new job {job_id}"
                    )
            except Exception as purge_error:
                logger.warning(f"Queue purge skipped due to error: {purge_error}")

        # Queue job to Celery worker
        task = localize_video_task.apply_async(
            args=[
                job_id,
                video_url_str,
                request.target_language.value,
                options,
            ],
            task_id=job_id,
        )

        logger.info(f"Job {job_id} queued with Celery task ID: {task.id}")

        return JobResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            message=f"Job queued for processing. Target language: {request.target_language.value}",
        )

    except Exception as e:
        logger.error(f"Error creating localization job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=JobResponse)
async def upload_and_localize(
    file: UploadFile = File(...),
    target_language: LanguageCode = Form(...),
    enable_quiz: bool = Form(True),
    enable_vision_sync: bool = Form(True),
    enable_lip_sync: bool = Form(False),
):
    """
    Upload a video file and create localization job

    Accepts video file upload directly instead of URL.
    """
    try:
        # Validate file type
        if not file.content_type.startswith("video/"):
            raise HTTPException(
                status_code=400, detail="File must be a video format"
            )

        # Generate unique job ID
        job_id = str(uuid.uuid4())

        logger.info(f"Uploaded video for job {job_id}, size: {file.size} bytes")

        # TODO: Save file and queue job
        return JobResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            message=f"Video uploaded and queued. Target language: {target_language.value}",
        )

    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
