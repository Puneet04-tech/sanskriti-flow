"""
Video Processing Utilities
FFmpeg-based video manipulation
"""

import ffmpeg
import subprocess
from pathlib import Path
from app.core.logger import logger
from app.core.config import settings
from typing import Optional, Tuple
import os


class VideoProcessor:
    """
    Utility class for video processing operations
    
    Features:
    - Audio extraction
    - Video encoding/decoding
    - Frame extraction
    - Audio/video merging
    - Format conversion
    """

    @staticmethod
    def extract_audio(video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            output_path: Output audio file path (optional)
        
        Returns:
            Path to extracted audio file
        """
        try:
            if output_path is None:
                output_path = str(Path(video_path).with_suffix('.wav'))
            
            logger.info(f"Extracting audio: {video_path} -> {output_path}")
            
            (
                ffmpeg
                .input(video_path)
                .output(
                    output_path,
                    acodec='pcm_s16le',
                    ac=1,
                    ar='16k',
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info("Audio extraction complete")
            return output_path
            
        except ffmpeg.Error as e:
            logger.error(f"Audio extraction failed: {e.stderr.decode() if e.stderr else str(e)}")
            raise

    @staticmethod
    def merge_audio_video(
        video_path: str,
        audio_path: str,
        output_path: str,
        preserve_video_audio: bool = False,
    ) -> str:
        """
        Merge audio with video
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Output file path
            preserve_video_audio: Mix with original audio instead of replacing
        
        Returns:
            Path to output file
        """
        try:
            logger.info(f"Merging audio and video: {output_path}")
            
            video = ffmpeg.input(video_path)
            audio = ffmpeg.input(audio_path)
            
            if preserve_video_audio:
                # Mix both audio tracks
                (
                    ffmpeg
                    .concat(video, audio, v=1, a=1)
                    .output(output_path)
                    .overwrite_output()
                    .run(quiet=True)
                )
            else:
                # Replace audio
                (
                    ffmpeg
                    .output(
                        video.video,
                        audio.audio,
                        output_path,
                        vcodec='copy',
                        acodec='aac',
                    )
                    .overwrite_output()
                    .run(quiet=True)
                )
            
            logger.info("Audio/video merge complete")
            return output_path
            
        except ffmpeg.Error as e:
            logger.error(f"Audio/video merge failed: {e.stderr.decode() if e.stderr else str(e)}")
            raise

    @staticmethod
    def extract_frames(
        video_path: str,
        output_dir: str,
        fps: Optional[int] = None,
    ) -> list:
        """
        Extract frames from video
        
        Args:
            video_path: Path to video file
            output_dir: Directory to save frames
            fps: Frames per second to extract (None = all frames)
        
        Returns:
            List of frame file paths
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"Extracting frames: {video_path}")
            
            output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')
            
            stream = ffmpeg.input(video_path)
            
            if fps:
                stream = stream.filter('fps', fps=fps)
            
            stream.output(output_pattern).overwrite_output().run(quiet=True)
            
            # Get list of extracted frames
            frames = sorted([
                os.path.join(output_dir, f)
                for f in os.listdir(output_dir)
                if f.startswith('frame_')
            ])
            
            logger.info(f"Extracted {len(frames)} frames")
            return frames
            
        except ffmpeg.Error as e:
            logger.error(f"Frame extraction failed: {e.stderr.decode() if e.stderr else str(e)}")
            raise

    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """
        Get video metadata
        
        Args:
            video_path: Path to video file
        
        Returns:
            Dictionary with video information
        """
        try:
            probe = ffmpeg.probe(video_path)
            
            video_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'video'),
                None
            )
            audio_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'audio'),
                None
            )
            
            info = {
                'duration': float(probe['format']['duration']),
                'size': int(probe['format']['size']),
                'bitrate': int(probe['format']['bit_rate']),
            }
            
            if video_stream:
                info.update({
                    'width': int(video_stream['width']),
                    'height': int(video_stream['height']),
                    'fps': eval(video_stream['r_frame_rate']),
                    'codec': video_stream['codec_name'],
                })
            
            if audio_stream:
                info.update({
                    'audio_codec': audio_stream['codec_name'],
                    'sample_rate': int(audio_stream['sample_rate']),
                    'channels': int(audio_stream['channels']),
                })
            
            return info
            
        except ffmpeg.Error as e:
            logger.error(f"Failed to get video info: {str(e)}")
            raise

    @staticmethod
    def compress_video(
        input_path: str,
        output_path: str,
        crf: int = 23,
        preset: str = 'medium',
    ) -> str:
        """
        Compress video (for Drishti mode)
        
        Args:
            input_path: Input video path
            output_path: Output video path
            crf: Constant Rate Factor (0-51, lower = better quality)
            preset: Encoding preset (ultrafast, fast, medium, slow, veryslow)
        
        Returns:
            Output path
        """
        try:
            logger.info(f"Compressing video: {input_path}")
            
            (
                ffmpeg
                .input(input_path)
                .output(
                    output_path,
                    vcodec='libx264',
                    crf=crf,
                    preset=preset,
                    acodec='aac',
                    audio_bitrate='64k',
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info("Video compression complete")
            return output_path
            
        except ffmpeg.Error as e:
            logger.error(f"Video compression failed: {e.stderr.decode() if e.stderr else str(e)}")
            raise


def download_video(url: str, output_path: str) -> str:
    """
    Download video from URL
    
    Args:
        url: Video URL
        output_path: Output file path
    
    Returns:
        Path to downloaded video
    """
    try:
        logger.info(f"Downloading video: {url}")
        
        # Use yt-dlp or wget/curl
        cmd = f'curl -L "{url}" -o "{output_path}"'
        subprocess.run(cmd, shell=True, check=True)
        
        logger.info("Video download complete")
        return output_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Video download failed: {str(e)}")
        raise
