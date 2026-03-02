"""
Celery Tasks for Video Localization Pipeline
"""

from app.workers.celery_app import celery_app
from app.core.config import settings
from app.core.logger import logger
from app.services.transcription import get_transcription_service
from app.services.translation import get_translation_service
from app.services.quiz_generator import get_quiz_service
from app.services.vision_sync import get_vision_sync_service
from app.services.voice_clone import get_voice_clone_service
from app.services.lip_sync import get_lip_sync_service
from app.utils.video_utils import VideoProcessor
from celery import Task
from typing import Dict
import os


class LocalizationTask(Task):
    """Base task with service initialization"""

    def __init__(self):
        super().__init__()
        self._transcription = None
        self._translation = None
        self._quiz = None
        self._vision = None

    @property
    def transcription(self):
        if self._transcription is None:
            self._transcription = get_transcription_service()
        return self._transcription

    @property
    def translation(self):
        if self._translation is None:
            self._translation = get_translation_service()
        return self._translation

    @property
    def quiz(self):
        if self._quiz is None:
            self._quiz = get_quiz_service()
        return self._quiz

    @property
    def vision(self):
        if self._vision is None:
            self._vision = get_vision_sync_service()
        return self._vision


@celery_app.task(bind=True, base=LocalizationTask, name="localize_video")
def localize_video_task(
    self,
    job_id: str,
    video_path: str,
    target_language: str,
    options: Dict,
) -> Dict:
    """
    Main video localization pipeline task
    
    Pipeline:
    1. Extract audio from video
    2. Transcribe audio (Faster-Whisper)
    3. Translate transcript (NLLB-200 + Hinglish Engine)
    4. Generate quiz questions (Llama 3.1) - optional
    5. Add vision-sync overlays - optional
    6. Generate cloned voice audio (CosyVoice2) - optional
    7. Apply lip-sync (LatentSync) - optional
    8. Merge everything and export
    """
    import time
    
    try:
        logger.info(f"Starting localization job: {job_id}")
        self.update_state(state="PROCESSING", meta={"stage": "Initializing", "progress": 0})
        time.sleep(1)

        # Create temp directory for this job
        job_dir = os.path.join(settings.TEMP_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)

        # Stage 1: Downloading video
        logger.info(f"[{job_id}] Stage 1: Downloading video")
        self.update_state(state="PROCESSING", meta={"stage": "Downloading video", "progress": 10})
        time.sleep(2)

        # Stage 2: Extracting audio
        logger.info(f"[{job_id}] Stage 2: Extracting audio")
        self.update_state(state="PROCESSING", meta={"stage": "Extracting audio", "progress": 25})
        time.sleep(2)

        # Stage 3: Transcribing
        logger.info(f"[{job_id}] Stage 3: Transcribing")
        self.update_state(state="PROCESSING", meta={"stage": "Transcribing audio", "progress": 40})
        time.sleep(3)

        # Stage 4: Translating
        logger.info(f"[{job_id}] Stage 4: Translating")
        self.update_state(state="PROCESSING", meta={"stage": "Translating transcript", "progress": 60})
        # Stage 4: Translating
        logger.info(f"[{job_id}] Stage 4: Translating")
        self.update_state(state="PROCESSING", meta={"stage": "Translating transcript", "progress": 60})
        time.sleep(3)
        
        # Simulate translation
        translated_segments = [
            {"start": 0.0, "end": 5.0, "text": f"[Translated to {target_language}] Sample segment 1"},
            {"start": 5.0, "end": 10.0, "text": f"[Translated to {target_language}] Sample segment 2"},
        ]

        # Stage 5: Generate quizzes (optional)
        quizzes = []
        if options.get("enable_quiz", True):
            logger.info(f"[{job_id}] Stage 5: Generating quizzes")
            self.update_state(state="PROCESSING", meta={"stage": "Generating quizzes", "progress": 75})
            time.sleep(2)
            quizzes = [{"question": "Sample quiz question?", "options": ["A", "B", "C", "D"], "answer": "A"}]

        # Stage 6: Adding overlays (optional)
        if options.get("enable_vision_sync", True):
            logger.info(f"[{job_id}] Stage 6: Adding vision overlays")
            self.update_state(state="PROCESSING", meta={"stage": "Adding overlays", "progress": 85})
            time.sleep(2)

        # Stage 7: Finalizing
        logger.info(f"[{job_id}] Stage 7: Finalizing")
        self.update_state(state="PROCESSING", meta={"stage": "Finalizing", "progress": 95})
        time.sleep(2)
        # Stage 7: Finalizing
        logger.info(f"[{job_id}] Stage 7: Finalizing")
        self.update_state(state="PROCESSING", meta={"stage": "Finalizing", "progress": 95})
        time.sleep(2)
        
        # Create output directory if it doesn't exist
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(settings.OUTPUT_DIR, f"{job_id}.mp4")
        
        # Create a dummy output file (in production this would be the processed video)
        with open(output_path, 'w') as f:
            f.write(f"Localized video for job {job_id}\n")
            f.write(f"Target language: {target_language}\n")
            f.write(f"Options: {options}\n")

        logger.info(f"[{job_id}] Localization complete!")

        return {
            "job_id": job_id,
            "status": "completed",
            "output_path": output_path,
            "translated_segments": translated_segments,
            "quizzes": quizzes,
            "metadata": {
                "target_language": target_language,
                "num_segments": len(translated_segments),
                "num_quizzes": len(quizzes),
            },
        }

    except Exception as e:
        logger.error(f"[{job_id}] Localization failed: {str(e)}")
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise


@celery_app.task(name="extract_audio_task")
def extract_audio_task(video_path: str, output_path: str) -> str:
    """Extract audio from video"""
    return VideoProcessor.extract_audio(video_path, output_path)


@celery_app.task(name="transcribe_task")
def transcribe_task(audio_path: str) -> Dict:
    """Transcribe audio"""
    service = get_transcription_service()
    return service.transcribe(audio_path)


@celery_app.task(name="translate_task")
def translate_task(text: str, target_lang: str) -> str:
    """Translate text"""
    service = get_translation_service()
    return service.translate(text, target_lang)
