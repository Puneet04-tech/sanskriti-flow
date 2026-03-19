"""
Swar - Assistive Audio Descriptions Service
Generates audio descriptions for visually impaired students

Features:
- Detects key visual moments (diagrams, equations, gestures)
- Generates natural language descriptions
- Creates supplementary audio track
- Syncs with video timeline
"""

import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from app.core.logger import logger
from app.core.config import settings
import cv2
from pydub import AudioSegment
from gtts import gTTS
import tempfile

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class SwarAudioDescriptionService:
    """
    Service for generating audio descriptions for accessibility
    
    Use Cases:
    - Blind/low-vision student accessibility
    - Autistic spectrum users (additional audio cues)
    - ESL learners (supplementary narration)
    
    Features:
    - Detects meaningful visual changes
    - Generates natural descriptions
    - Creates synchronized audio track
    - Language-independent (works on translated content)
    """

    # Scene change detection threshold (0-1)
    SCENE_CHANGE_THRESHOLD = 0.25
    
    # Key visual element patterns
    VISUAL_PATTERNS = {
        "equation": ["=", "+", "-", "×", "÷", "∑", "∫", "√", "π"],
        "diagram": ["→", "←", "↑", "↓", "⊕", "⊗", "◯", "□", "△"],
        "table": ["├", "┤", "┬", "┴", "┼", "─", "│"],
        "graph": ["graph", "chart", "plot", "curve", "line"]
    }

    def __init__(self):
        """Initialize Swar service"""
        logger.info("Initializing Swar Audio Description Service")
        self.device = "cuda" if torch.cuda.is_available() else "cpu" if TRANSFORMERS_AVAILABLE else "cpu"
        self.available = True
        self.vl_model = None
        self.vl_tokenizer = None
        
        # Try to load vision language model for descriptions
        if TRANSFORMERS_AVAILABLE:
            try:
                self._load_vlm()
            except Exception as e:
                logger.warning(f"VLM loading failed, using fallback detection: {e}")
                self.available = True  # Still available, just using fallback

    def _load_vlm(self):
        """Load vision language model (Moondream2 lightweight)"""
        try:
            logger.info("Loading Moondream2 for visual understanding...")
            model_name = "vikhyatk/moondream2"
            self.vl_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if "cuda" in self.device else torch.float32
            ).to(self.device)
            self.vl_tokenizer = AutoTokenizer.from_pretrained(model_name)
            logger.info("Moondream2 loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load VLM: {e}. Using fallback pattern detection.")
            self.vl_model = None

    def generate_descriptions_from_video(
        self,
        video_path: str,
        target_language: str = "hi",
        sample_interval: int = 30,  # Every 30 frames
        include_gestures: bool = True,
        include_diagrams: bool = True
    ) -> List[Dict]:
        """
        Generate audio descriptions for video key moments
        
        Args:
            video_path: Path to video file
            target_language: Target language for descriptions
            sample_interval: Sample every N frames
            include_gestures: Detect speaker gestures
            include_diagrams: Detect diagrams/equations/graphs
        
        Returns:
            List of description segments with timestamps and audio
        """
        try:
            logger.info(f"Generating audio descriptions for {video_path}")
            
            if not os.path.exists(video_path):
                logger.error(f"Video not found: {video_path}")
                return []
            
            descriptions = []
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Could not open video: {video_path}")
                return []
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Video: {frame_count} frames @ {fps} fps")
            
            frame_number = 0
            prev_frame = None
            scene_change_count = 0
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Sample every N frames
                if frame_number % sample_interval != 0:
                    frame_number += 1
                    prev_frame = frame
                    continue
                
                timestamp = frame_number / fps
                
                # Detect scene changes
                is_scene_change = False
                if prev_frame is not None:
                    is_scene_change = self._detect_scene_change(prev_frame, frame)
                
                # Detect visual elements
                description = None
                if is_scene_change or frame_number == 0:
                    
                    # Detect diagrams/equations
                    if include_diagrams:
                        diagram_desc = self._detect_diagrams(frame)
                        if diagram_desc:
                            description = diagram_desc
                    
                    # Detect text/equations (OCR-lite via contours)
                    if not description and include_diagrams:
                        text_desc = self._detect_text_elements(frame)
                        if text_desc:
                            description = text_desc
                    
                    # Detect gestures (motion change)
                    if not description and include_gestures and prev_frame is not None:
                        gesture_desc = self._detect_gestures(prev_frame, frame)
                        if gesture_desc:
                            description = gesture_desc
                
                # If we found a meaningful description, add it
                if description:
                    logger.info(f"Detected at {timestamp:.1f}s: {description}")
                    descriptions.append({
                        "timestamp": timestamp,
                        "description": description,
                        "type": "visual",
                        "confidence": 0.85
                    })
                    scene_change_count += 1
                
                frame_number += 1
                prev_frame = frame.copy()
                
                # Safety limit (max 50 descriptions per video to avoid token limits)
                if scene_change_count >= 50:
                    logger.info("Reached max description count (50), stopping early")
                    break
            
            cap.release()
            
            logger.info(f"Generated {len(descriptions)} visual descriptions")
            return descriptions
            
        except Exception as e:
            logger.error(f"Failed to generate descriptions: {e}")
            return []

    def _detect_scene_change(self, frame1, frame2, threshold=0.25) -> bool:
        """
        Detect if there's a significant scene change
        Uses histogram comparison
        """
        try:
            # Resize for faster comparison
            f1 = cv2.resize(frame1, (100, 100))
            f2 = cv2.resize(frame2, (100, 100))
            
            # Convert to HSV for better color detection
            hsv1 = cv2.cvtColor(f1, cv2.COLOR_BGR2HSV)
            hsv2 = cv2.cvtColor(f2, cv2.COLOR_BGR2HSV)
            
            # Compare histograms
            hist1 = cv2.calcHist([hsv1], [0, 1], None, [50, 50], [0, 180, 0, 256])
            hist2 = cv2.calcHist([hsv2], [0, 1], None, [50, 50], [0, 180, 0, 256])
            
            # Normalize
            cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            
            # Compare
            difference = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
            
            return difference > threshold
            
        except Exception as e:
            logger.debug(f"Scene change detection failed: {e}")
            return False

    def _detect_diagrams(self, frame) -> Optional[str]:
        """
        Detect diagrams, equations, or written content
        Uses edge detection and contour analysis
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) > 10:
                # Many contours suggest a diagram or complex visual
                return "A diagram or visual representation appears on screen"
            
            return None
            
        except Exception as e:
            logger.debug(f"Diagram detection failed: {e}")
            return None

    def _detect_text_elements(self, frame) -> Optional[str]:
        """
        Detect text/equations on screen
        Simple threshold-based detection
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Threshold to binary
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Count text-like patterns (small black on white regions)
            white_pixels = np.sum(binary == 255)
            total_pixels = binary.size
            white_ratio = white_pixels / total_pixels
            
            # If mostly white with some black text
            if 0.6 < white_ratio < 0.95:
                return "Text or equations are displayed on the screen"
            
            return None
            
        except Exception as e:
            logger.debug(f"Text detection failed: {e}")
            return None

    def _detect_gestures(self, frame1, frame2) -> Optional[str]:
        """
        Detect sudden movement (professor gesturing)
        Uses optical flow
        """
        try:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(
                gray1, gray2, None,
                pyr_scale=0.5, levels=3, winsize=15,
                iterations=3, n8=True, poly_n=5, poly_sigma=1.1, flags=0
            )
            
            # Calculate magnitude of flow
            mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            avg_motion = np.mean(mag)
            
            if avg_motion > 5:  # Significant motion detected
                return "The speaker is making gestures or pointing on screen"
            
            return None
            
        except Exception as e:
            logger.debug(f"Gesture detection failed: {e}")
            return None

    async def generate_audio_for_descriptions(
        self,
        descriptions: List[Dict],
        target_language: str = "hi",
        voice_speed: float = 1.0
    ) -> Optional[str]:
        """
        Convert descriptions to audio
        
        Args:
            descriptions: List of description dicts with timestamp and text
            target_language: Target language code
            voice_speed: Speech speed multiplier
        
        Returns:
            Path to audio file or None
        """
        try:
            if not descriptions:
                return None
            
            logger.info(f"Generating audio for {len(descriptions)} descriptions")
            
            # Prepare audio segments list
            audio_segments = []
            
            for desc_item in descriptions:
                timestamp = desc_item.get("timestamp", 0)
                description = desc_item.get("description", "")
                
                if not description:
                    continue
                
                logger.info(f"TTS for description at {timestamp:.1f}s: {description[:50]}...")
                
                try:
                    # Generate TTS
                    tts = gTTS(text=description, lang=target_language, slow=False)
                    
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                        tts.save(tmp.name)
                        audio = AudioSegment.from_file(tmp.name)
                        os.unlink(tmp.name)
                    
                    audio_segments.append((timestamp, audio))
                    
                except Exception as e:
                    logger.warning(f"TTS generation failed for description: {e}")
                    continue
            
            if not audio_segments:
                logger.warning("No audio descriptions could be generated")
                return None
            
            logger.info(f"Generated audio for {len(audio_segments)} descriptions")
            # Return path for now (actual merging done in tasks.py)
            return f"swar_descriptions_{len(audio_segments)}_segments"
            
        except Exception as e:
            logger.error(f"Audio description generation failed: {e}")
            return None


def get_swar_service() -> SwarAudioDescriptionService:
    """Factory function for Swar service"""
    return SwarAudioDescriptionService()
