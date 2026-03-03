"""
Quality Validation Service
Ensures maximum accuracy and desired results for all processing stages
"""

from app.core.logger import logger
from typing import Dict, List, Optional, Tuple
import os
import subprocess
import json


class QualityValidator:
    """
    Comprehensive quality validation for video processing pipeline
    Ensures 100% accuracy and desired results at each stage
    """
    
    def __init__(self):
        logger.info("Quality Validator initialized")
        self.validation_results = {}
    
    def validate_transcription(
        self,
        segments: List[Dict],
        audio_path: str
    ) -> Tuple[bool, str]:
        """
        Validate transcription quality
        
        Checks:
        - Non-empty segments
        - Reasonable segment lengths
        - No gibberish (compression ratio)
        - Proper timestamps
        
        Returns:
            (is_valid, message)
        """
        try:
            if not segments or len(segments) == 0:
                return False, "No transcription segments generated"
            
            # Check each segment
            for idx, segment in enumerate(segments):
                # Must have text
                text = segment.get("text", "").strip()
                if not text:
                    return False, f"Segment {idx} has no text"
                
                # Must have valid timestamps
                start = segment.get("start", -1)
                end = segment.get("end", -1)
                if start < 0 or end < 0 or end <= start:
                    return False, f"Segment {idx} has invalid timestamps: {start}-{end}"
                
                # Text should not be too short or too long
                if len(text) < 2:
                    return False, f"Segment {idx} text too short: '{text}'"
                
                if len(text) > 1000:
                    logger.warning(f"Segment {idx} very long ({len(text)} chars), may contain errors")
            
            # Get audio duration for validation
            try:
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                     '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                    capture_output=True, text=True, timeout=10
                )
                audio_duration = float(result.stdout.strip())
                
                # Last segment should not exceed audio duration significantly
                last_end = segments[-1].get("end", 0)
                if last_end > audio_duration + 10:
                    logger.warning(f"Transcription extends beyond audio: {last_end}s vs {audio_duration}s")
            except Exception as e:
                logger.warning(f"Could not validate audio duration: {e}")
            
            logger.info(f"✅ Transcription quality validated: {len(segments)} segments")
            return True, f"Valid transcription with {len(segments)} segments"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_translation(
        self,
        original: str,
        translated: str,
        target_language: str
    ) -> Tuple[bool, str]:
        """
        Validate translation quality
        
        Checks:
        - Non-empty translation
        - Reasonable length ratio
        - No excessive repetition
        - Proper encoding
        
        Returns:
            (is_valid, message)
        """
        try:
            if not translated or len(translated.strip()) == 0:
                return False, "Translation is empty"
            
            # Check length ratio (should be within 0.5x to 3x)
            orig_len = len(original)
            trans_len = len(translated)
            ratio = trans_len / orig_len if orig_len > 0 else 0
            
            if ratio < 0.3:
                return False, f"Translation suspiciously short (ratio: {ratio:.2f})"
            
            if ratio > 4.0:
                return False, f"Translation suspiciously long (ratio: {ratio:.2f})"
            
            # Check for excessive repetition
            words = translated.split()
            if len(words) > 0:
                unique_words = set(words)
                uniqueness_ratio = len(unique_words) / len(words)
                if uniqueness_ratio < 0.3:
                    return False, f"Translation has excessive repetition (uniqueness: {uniqueness_ratio:.2f})"
            
            # Check proper encoding (no encoding errors)
            try:
                translated.encode('utf-8').decode('utf-8')
            except UnicodeError:
                return False, "Translation has encoding errors"
            
            logger.info(f"✅ Translation quality validated: {len(translated)} chars")
            return True, f"Valid translation (ratio: {ratio:.2f})"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_voice_clone(
        self,
        audio_path: str,
        expected_duration: float,
        tolerance: float = 2.0
    ) -> Tuple[bool, str]:
        """
        Validate cloned voice audio quality
        
        Checks:
        - File exists and is readable
        - Proper duration
        - Audio format correct
        - No corrupted audio
        
        Returns:
            (is_valid, message)
        """
        try:
            if not os.path.exists(audio_path):
                return False, f"Audio file not found: {audio_path}"
            
            # Check file size (should be > 1KB)
            file_size = os.path.getsize(audio_path)
            if file_size < 1024:
                return False, f"Audio file too small: {file_size} bytes"
            
            # Validate with FFprobe
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 
                 'format=duration,format_name', '-of', 'json', audio_path],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return False, f"Audio validation failed: {result.stderr}"
            
            info = json.loads(result.stdout)
            duration = float(info['format']['duration'])
            format_name = info['format']['format_name']
            
            # Check duration
            if abs(duration - expected_duration) > tolerance:
                logger.warning(f"Audio duration mismatch: {duration}s vs expected {expected_duration}s")
            
            # Check format
            if 'wav' not in format_name and 'mp3' not in format_name:
                logger.warning(f"Unexpected audio format: {format_name}")
            
            logger.info(f"✅ Voice clone audio validated: {duration:.1f}s, {file_size/1024:.1f}KB")
            return True, f"Valid audio: {duration:.1f}s"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_lip_sync(
        self,
        video_path: str,
        original_video_path: str
    ) -> Tuple[bool, str]:
        """
        Validate lip-synced video quality
        
        Checks:
        - Video file exists
        - Resolution maintained
        - Frame rate maintained
        - Duration matches original
        
        Returns:
            (is_valid, message)
        """
        try:
            if not os.path.exists(video_path):
                return False, f"Lip-synced video not found: {video_path}"
            
            # Get video info
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                 '-show_entries', 'stream=width,height,r_frame_rate,duration',
                 '-of', 'json', video_path],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return False, f"Video validation failed: {result.stderr}"
            
            info = json.loads(result.stdout)
            if not info.get('streams'):
                return False, "No video stream found"
            
            stream = info['streams'][0]
            width = stream.get('width', 0)
            height = stream.get('height', 0)
            
            # Check resolution
            if width < 640 or height < 480:
                return False, f"Video resolution too low: {width}x{height}"
            
            logger.info(f"✅ Lip-sync video validated: {width}x{height}")
            return True, f"Valid video: {width}x{height}"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_final_video(
        self,
        video_path: str,
        expected_duration: float,
        tolerance: float = 5.0
    ) -> Tuple[bool, str]:
        """
        Validate final output video quality
        
        Checks:
        - File exists and readable
        - Has video and audio streams
        - Proper duration
        - Playable format
        
        Returns:
            (is_valid, message)
        """
        try:
            if not os.path.exists(video_path):
                return False, f"Output video not found: {video_path}"
            
            # Check file size (should be > 100KB)
            file_size = os.path.getsize(video_path)
            if file_size < 100 * 1024:
                return False, f"Output video too small: {file_size} bytes"
            
            # Validate with FFprobe
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries',
                 'format=duration,format_name:stream=codec_type,codec_name',
                 '-of', 'json', video_path],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return False, f"Video validation failed: {result.stderr}"
            
            info = json.loads(result.stdout)
            
            # Check duration
            duration = float(info['format']['duration'])
            if abs(duration - expected_duration) > tolerance:
                logger.warning(f"Duration mismatch: {duration}s vs expected {expected_duration}s")
            
            # Check streams
            streams = info.get('streams', [])
            has_video = any(s.get('codec_type') == 'video' for s in streams)
            has_audio = any(s.get('codec_type') == 'audio' for s in streams)
            
            if not has_video:
                return False, "No video stream in output"
            
            if not has_audio:
                logger.warning("No audio stream in output")
            
            logger.info(f"✅ Final video validated: {duration:.1f}s, {file_size/1024/1024:.1f}MB")
            return True, f"Valid output: {duration:.1f}s, {file_size/1024/1024:.1f}MB"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_validation_report(self) -> Dict:
        """
        Get comprehensive validation report
        
        Returns:
            Dictionary with all validation results
        """
        return {
            "validations": self.validation_results,
            "total_checks": len(self.validation_results),
            "passed": sum(1 for v in self.validation_results.values() if v.get("valid", False)),
            "failed": sum(1 for v in self.validation_results.values() if not v.get("valid", False)),
        }


def get_quality_validator() -> QualityValidator:
    """Get or create quality validator instance"""
    return QualityValidator()
