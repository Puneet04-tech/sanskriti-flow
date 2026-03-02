"""
Pydantic Models for API Requests and Responses
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from enum import Enum


class LanguageCode(str, Enum):
    """Supported language codes"""

    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ODIA = "or"


class LocalizationRequest(BaseModel):
    """Request model for video localization"""

    video_url: Optional[HttpUrl] = Field(None, description="URL of the video to localize")
    video_file: Optional[str] = Field(None, description="Local path to video file")
    target_language: LanguageCode = Field(..., description="Target language code")
    enable_quiz: bool = Field(True, description="Generate interactive quizzes")
    enable_vision_sync: bool = Field(True, description="Add vision-sync overlays")
    enable_lip_sync: bool = Field(False, description="Apply lip-sync (GPU intensive)")
    enable_voice_clone: bool = Field(False, description="Clone original speaker's voice")
    enable_swar: bool = Field(False, description="Add assistive audio for visually impaired")
    enable_drishti: bool = Field(False, description="Enable rural/edge mode")
    preserve_technical_terms: bool = Field(True, description="Keep technical terms in English")

    class Config:
        json_schema_extra = {
            "example": {
                "video_url": "https://example.com/lecture.mp4",
                "target_language": "hi",
                "enable_quiz": True,
                "enable_vision_sync": True,
            }
        }


class JobStatus(str, Enum):
    """Job processing status"""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobResponse(BaseModel):
    """Response model for job submission"""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")


class JobStatusResponse(BaseModel):
    """Response model for job status check"""

    job_id: str
    status: JobStatus
    progress: float = Field(..., ge=0, le=100, description="Progress percentage")
    stage: str = Field(..., description="Current processing stage")
    eta_seconds: Optional[int] = Field(None, description="Estimated time remaining")
    result_url: Optional[str] = Field(None, description="URL of processed video if completed")
    error: Optional[str] = Field(None, description="Error message if failed")


class TranscriptSegment(BaseModel):
    """Transcript segment with timestamp"""

    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")


class QuizQuestion(BaseModel):
    """Generated quiz question"""

    question: str = Field(..., description="Question text")
    options: List[str] = Field(..., description="Multiple choice options")
    correct_answer: int = Field(..., description="Index of correct answer")
    timestamp: float = Field(..., description="Video timestamp where this concept appears")
    explanation: str = Field(..., description="Explanation of the answer")


class LocalizationResult(BaseModel):
    """Complete localization result"""

    job_id: str
    video_url: str
    transcript: List[TranscriptSegment]
    quizzes: Optional[List[QuizQuestion]] = None
    metadata: Dict = Field(default_factory=dict)
