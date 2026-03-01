"""
Transcription Service
Uses Faster-Whisper for high-accuracy, local speech-to-text
"""

from faster_whisper import WhisperModel
from app.core.config import settings
from app.core.logger import logger
from typing import List, Dict, Optional
import os


class TranscriptionService:
    """
    Service for transcribing audio from videos using Faster-Whisper
    
    Features:
    - Local processing (no API calls)
    - GPU acceleration support
    - Multiple model sizes
    - Language detection
    - Timestamp extraction
    """

    def __init__(self, model_size: Optional[str] = None):
        """
        Initialize transcription service
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large-v2)
        """
        self.model_size = model_size or settings.WHISPER_MODEL
        self.device = "cuda" if settings.USE_GPU else "cpu"
        self.compute_type = "float16" if settings.USE_GPU else "int8"
        
        logger.info(
            f"Initializing Whisper model: {self.model_size} on {self.device}"
        )
        
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> Dict:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Language code (None for auto-detection)
            task: "transcribe" or "translate"
        
        Returns:
            Dictionary with segments, language, and metadata
        """
        try:
            logger.info(f"Transcribing: {audio_path}")
            
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                beam_size=5,
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(
                    min_silence_duration_ms=500
                ),
            )
            
            # Convert generator to list
            segments_list = []
            for segment in segments:
                segments_list.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "avg_logprob": segment.avg_logprob,
                    "no_speech_prob": segment.no_speech_prob,
                })
            
            result = {
                "segments": segments_list,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
            }
            
            logger.info(
                f"Transcription complete: {len(segments_list)} segments, "
                f"language: {info.language}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise

    def extract_full_text(self, transcription_result: Dict) -> str:
        """
        Extract full text from transcription result
        
        Args:
            transcription_result: Output from transcribe()
        
        Returns:
            Concatenated text
        """
        return " ".join(
            segment["text"] for segment in transcription_result["segments"]
        )

    def get_segments_by_timerange(
        self,
        transcription_result: Dict,
        start_time: float,
        end_time: float,
    ) -> List[Dict]:
        """
        Get segments within a time range
        
        Args:
            transcription_result: Output from transcribe()
            start_time: Start time in seconds
            end_time: End time in seconds
        
        Returns:
            List of segments within the time range
        """
        return [
            segment
            for segment in transcription_result["segments"]
            if segment["start"] >= start_time and segment["end"] <= end_time
        ]


# Singleton instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """Get or create transcription service instance"""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service
