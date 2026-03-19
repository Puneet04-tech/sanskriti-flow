"""
Drishti - Rural/Bandwidth Optimization Service
Optimizes videos for 2G/3G networks and low-bandwidth environments

Features:
- Aggressive video compression
- Audio-first mode (high quality audio, minimal video)
- Adaptive quality based on available bandwidth
- Thumbnail extraction for still-image previews
- Progressive loading strategies
"""

import os
import subprocess
from typing import Dict, Optional, Tuple
from app.core.logger import logger
from app.core.config import settings
import json


class DrishtiRuralModeService:
    """
    Service for optimizing videos for rural/low-bandwidth environments
    
    Scenarios:
    - 2G networks (400KB/s typical, 2-4 hour download for 10-min video)
    - 3G networks (1-3 MB/s typical, 30-60 min for 10-min video)
    - Spotty connectivity (automatic quality switching)
    - Data-limited users (focus on content, not visual quality)
    
    Strategy:
    1. Extract audio at high quality (128-192 kbps MP3)
    2. Reduce video to 240p-360p at 15fps
    3. Create thumbnail-based fallback
    4. Use adaptive bitrate delivery
    """

    # Quality presets for different bandwidth scenarios
    QUALITY_PRESETS = {
        "ultra_low": {
            "video_resolution": "240p",
            "video_bitrate": "300k",
            "fps": 15,
            "audio_bitrate": "64k",
            "description": "Ultra low bandwidth (2G/EDGE)"
        },
        "low": {
            "video_resolution": "360p",
            "video_bitrate": "500k",
            "fps": 15,
            "audio_bitrate": "96k",
            "description": "Low bandwidth (2G/3G)"
        },
        "medium": {
            "video_resolution": "480p",
            "video_bitrate": "1000k",
            "fps": 24,
            "audio_bitrate": "128k",
            "description": "Medium bandwidth (3G/4G)"
        },
        "audio_only": {
            "video_resolution": None,
            "video_bitrate": None,
            "fps": None,
            "audio_bitrate": "192k",
            "description": "Audio-only mode (just lectures, no video)"
        }
    }

    def __init__(self):
        """Initialize Drishti service"""
        logger.info("Initializing Drishti Rural Mode Service")
        self.available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"FFmpeg not available for Drishti: {e}")
            return False

    def optimize_for_rural_mode(
        self,
        input_video: str,
        output_path: str,
        quality_preset: str = "low",
        extract_audio_only: bool = False,
        create_thumbnail_grid: bool = True
    ) -> Tuple[bool, Dict]:
        """
        Optimize video for rural/low-bandwidth delivery
        
        Args:
            input_video: Path to input video
            output_path: Path for output video
            quality_preset: One of ultra_low, low, medium, audio_only
            extract_audio_only: Extract just audio MP3 (smallest size)
            create_thumbnail_grid: Create thumbnail preview grid
        
        Returns:
            (success, metadata_dict)
        """
        try:
            if not self.available:
                logger.error("Drishti service not available (ffmpeg missing)")
                return False, {"error": "ffmpeg not available"}
            
            if not os.path.exists(input_video):
                logger.error(f"Input video not found: {input_video}")
                return False, {"error": "Input video not found"}
            
            preset = self.QUALITY_PRESETS.get(quality_preset, self.QUALITY_PRESETS["low"])
            logger.info(f"Optimizing for Drishti mode: {preset['description']}")
            
            metadata = {
                "original_file": input_video,
                "output_file": output_path,
                "quality_preset": quality_preset,
                "preset_description": preset["description"],
                "optimizations_applied": []
            }
            
            # Audio-only mode (smallest size, good for lectures)
            if extract_audio_only or quality_preset == "audio_only":
                success = self._extract_audio_only(input_video, output_path, preset)
                if success:
                    metadata["optimizations_applied"].append("audio_only_extraction")
                    metadata["output_format"] = "mp3"
                    # Get file size
                    if os.path.exists(output_path):
                        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                        metadata["output_size_mb"] = round(file_size_mb, 2)
                return success, metadata
            
            # Video + Audio compression
            success = self._compress_video_and_audio(
                input_video,
                output_path,
                preset
            )
            
            if success:
                metadata["video_resolution"] = preset["video_resolution"]
                metadata["video_bitrate_kbps"] = preset["video_bitrate"]
                metadata["video_fps"] = preset["fps"]
                metadata["audio_bitrate_kbps"] = preset["audio_bitrate"]
                metadata["optimizations_applied"].extend([
                    "video_compression",
                    "resolution_reduction",
                    "fps_reduction",
                    "audio_optimization"
                ])
                
                # Get file size for reference
                if os.path.exists(output_path):
                    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    metadata["output_size_mb"] = round(file_size_mb, 2)
                    
                    # Estimate download time for various networks
                    metadata["estimated_download_times"] = {
                        "2g_50kbps": f"{file_size_mb * 8 / 50 / 60:.0f} min",
                        "2g_100kbps": f"{file_size_mb * 8 / 100 / 60:.0f} min",
                        "3g_500kbps": f"{file_size_mb * 8 / 500 / 60:.1f} min",
                        "3g_1mbps": f"{file_size_mb * 8 / 1000 / 60:.1f} min"
                    }
            
            # Create thumbnail grid if requested
            if create_thumbnail_grid and success:
                thumb_path = f"{output_path}.thumbnail.jpg"
                if self._create_thumbnail_grid(input_video, thumb_path):
                    metadata["thumbnail_grid"] = thumb_path
                    metadata["optimizations_applied"].append("thumbnail_generation")
            
            return success, metadata
            
        except Exception as e:
            logger.error(f"Drishti optimization failed: {e}")
            return False, {"error": str(e)}

    def _extract_audio_only(
        self,
        input_video: str,
        output_audio: str,
        preset: Dict
    ) -> bool:
        """
        Extract audio only (best for lectures)
        Results in ~10-30 MB audio file for 10-min lecture vs 200-500 MB video
        """
        try:
            audio_bitrate = preset["audio_bitrate"]
            logger.info(f"Extracting audio at {audio_bitrate} bitrate")
            
            cmd = [
                'ffmpeg',
                '-i', input_video,
                '-vn',  # No video
                '-acodec', 'libmp3lame',
                '-ab', audio_bitrate,
                '-ar', '22050',  # Lower sample rate for smaller file
                '-y',
                output_audio
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info(f"Audio extraction successful: {output_audio}")
                return True
            else:
                logger.error(f"Audio extraction failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Audio extraction error: {e}")
            return False

    def _compress_video_and_audio(
        self,
        input_video: str,
        output_video: str,
        preset: Dict
    ) -> bool:
        """
        Compress both video and audio for low bandwidth
        """
        try:
            resolution = preset["video_resolution"]
            video_bitrate = preset["video_bitrate"]
            fps = preset["fps"]
            audio_bitrate = preset["audio_bitrate"]
            
            logger.info(
                f"Compressing video: {resolution} @ {fps}fps, "
                f"{video_bitrate} video bitrate, {audio_bitrate} audio"
            )
            
            # Scale command
            if resolution == "240p":
                scale = "426:240"
            elif resolution == "360p":
                scale = "640:360"
            elif resolution == "480p":
                scale = "854:480"
            else:
                scale = "640:360"
            
            cmd = [
                'ffmpeg',
                '-i', input_video,
                '-vf', f"scale={scale}:force_original_aspect_ratio=decrease,pad={scale}:-1:-1:color=black",
                '-r', str(fps),
                '-b:v', video_bitrate,
                '-b:a', audio_bitrate,
                '-acodec', 'aac',
                '-ar', '22050',
                '-preset', 'ultrafast',  # Fast encoding for rural use
                '-y',
                output_video
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info(f"Video compression successful: {output_video}")
                return True
            else:
                logger.error(f"Video compression failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Video compression error: {e}")
            return False

    def _create_thumbnail_grid(
        self,
        input_video: str,
        output_thumb: str,
        grid_size: Tuple[int, int] = (4, 3)  # 4x3 grid = 12 thumbnails
    ) -> bool:
        """
        Create a grid of thumbnail images from the video
        Useful for progress tracking and preview
        """
        try:
            cols, rows = grid_size
            total_thumbs = cols * rows
            
            logger.info(f"Creating {cols}x{rows} thumbnail grid")
            
            # Get video duration
            duration_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                input_video
            ]
            result = subprocess.run(duration_cmd, capture_output=True, text=True, timeout=10)
            duration = float(result.stdout.strip())
            
            # Generate thumbnails at regular intervals
            interval = duration / (total_thumbs - 1) if total_thumbs > 1 else 0
            
            cmd = [
                'ffmpeg',
                '-i', input_video,
                '-vf', f"fps=1/{interval if interval > 0 else 1},scale=160:90,tile={cols}x{rows}",
                '-y',
                output_thumb
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"Thumbnail grid created: {output_thumb}")
                return True
            else:
                logger.warning(f"Thumbnail generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.warning(f"Thumbnail grid creation error: {e}")
            return False

    def get_bandwidth_recommendations(self, video_file_path: str) -> Dict:
        """
        Analyze video and recommend optimal quality preset
        Based on available bandwidth and file size
        """
        try:
            if not os.path.exists(video_file_path):
                return {"error": "File not found"}
            
            file_size_bytes = os.path.getsize(video_file_path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            recommendations = {
                "original_file_size_mb": round(file_size_mb, 2),
                "recommended_presets": {}
            }
            
            # Calculate sizes and times for each preset
            for preset_name, preset in self.QUALITY_PRESETS.items():
                if preset["video_bitrate"] is None:
                    # Audio-only estimate
                    estimated_size_mb = file_size_mb * 0.05  # ~5% of original
                else:
                    # Estimate based on bitrate reduction
                    estimated_size_mb = file_size_mb * 0.3  # Conservative estimate
                
                recommendations["recommended_presets"][preset_name] = {
                    "description": preset["description"],
                    "estimated_size_mb": round(estimated_size_mb, 2),
                    "download_times": {
                        "2g_100kbps": f"{estimated_size_mb * 8 / 100 / 60:.0f} min",
                        "3g_500kbps": f"{estimated_size_mb * 8 / 500 / 60:.1f} min",
                        "3g_1mbps": f"{estimated_size_mb * 8 / 1000 / 60:.1f} min"
                    }
                }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Bandwidth recommendation failed: {e}")
            return {"error": str(e)}


def get_drishti_service() -> DrishtiRuralModeService:
    """Factory function for Drishti service"""
    return DrishtiRuralModeService()
