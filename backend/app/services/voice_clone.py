"""
Voice Cloning & TTS Service
Uses gTTS (Google Text-to-Speech) for generating Hindi audio

Features:
- Multi-language TTS (Hindi, Tamil, Telugu, etc.)
- Natural-sounding speech synthesis
- Automatic audio timing alignment
- Support for Hinglish (technical terms preserved)
"""

from app.core.logger import logger
from app.core.config import settings
from typing import Optional, List, Dict
from gtts import gTTS
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import tempfile


class VoiceCloneService:
    """
    Service for TTS generation and audio synthesis
    
    Features:
    - Hindi/Hinglish TTS using Google Text-to-Speech
    - Segment-by-segment audio generation
    - Automatic timing alignment
    - High-quality audio output (MP3)
    """

    # Language code mapping for gTTS
    GTTS_LANG_MAP = {
        "hi": "hi",  # Hindi
        "ta": "ta",  # Tamil
        "te": "te",  # Telugu
        "bn": "bn",  # Bengali
        "mr": "mr",  # Marathi
        "gu": "gu",  # Gujarati
        "kn": "kn",  # Kannada
        "ml": "ml",  # Malayalam
        "pa": "pa",  # Punjabi
        "en": "en",  # English
    }

    def __init__(self):
        """Initialize TTS service"""
        logger.info("Initializing TTS Service (gTTS)")
        self.available = True

    def generate_speech_from_segments(
        self,
        segments: List[Dict],
        output_path: str,
        language: str = "hi",
        slow: bool = False
    ) -> str:
        """
        Generate speech audio from translated text segments
        
        Args:
            segments: List of dicts with 'text', 'start', 'end' keys
            output_path: Output audio file path
            language: Target language code (default: hi for Hindi)
            slow: Whether to use slower speech speed
        
        Returns:
            Path to generated audio file
        """
        try:
            logger.info(f"Generating TTS audio for {len(segments)} segments in language: {language}")
            
            # Get appropriate language code for gTTS
            gtts_lang = self.GTTS_LANG_MAP.get(language, "hi")
            
            # Combine all text with pauses
            full_text = ". ".join([seg.get("translated", seg.get("text", "")) for seg in segments])
            
            # Generate TTS audio
            tts = gTTS(text=full_text, lang=gtts_lang, slow=slow)
            
            # Save to temporary MP3 file first
            temp_mp3 = output_path.replace('.wav', '_temp.mp3')
            tts.save(temp_mp3)
            
            # Convert MP3 to WAV for better ffmpeg compatibility
            audio = AudioSegment.from_mp3(temp_mp3)
            audio.export(output_path, format="wav")
            
            # Clean up temp file
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
            
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(f"Generated TTS audio: {file_size:.2f} MB")
            
            return output_path
            
        except Exception as e:
            logger.error(f"TTS generation failed: {str(e)}")
            raise

    def generate_speech_segments(
        self,
        segments: list,
        reference_audio: str,
        output_dir: str,
        language: str = "hi",
    ) -> list:
        """
        Generate speech for multiple segments
        
        Args:
            segments: List of text segments with timestamps
            reference_audio: Reference audio for cloning
            output_dir: Output directory
            language: Target language
        
        Returns:
            List of generated audio file paths
        """
        logger.warning("Batch voice cloning not implemented.")
        
        os.makedirs(output_dir, exist_ok=True)
        
        audio_files = []
        # TODO: Implement batch processing
        
        return audio_files


# Singleton instance
_voice_clone_service: Optional[VoiceCloneService] = None


def get_voice_clone_service() -> VoiceCloneService:
    """Get or create voice cloning service instance"""
    global _voice_clone_service
    if _voice_clone_service is None:
        _voice_clone_service = VoiceCloneService()
    return _voice_clone_service
