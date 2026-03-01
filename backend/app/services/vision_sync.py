"""
Vision-Sync Overlay Service
Uses VLM (Moondream2/YOLO) to detect visual elements and add translated labels
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import torch
from app.core.config import settings
from app.core.logger import logger
from typing import List, Dict, Optional, Tuple
import cv2
import numpy as np


class VisionSyncService:
    """
    Service for detecting visual elements and creating translated overlays
    
    Features:
    - Frame-by-frame analysis
    - Object/text detection in lectures
    - Diagram/formula recognition
    - Translated label generation
    - Overlay positioning
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize Vision-Sync service
        
        Args:
            model_name: VLM model identifier
        """
        self.model_name = model_name or settings.MOONDREAM_MODEL
        self.device = "cuda" if settings.USE_GPU and torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing VLM: {self.model_name} on {self.device}")
        
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
            ).to(self.device)
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
            )
            
            logger.info("VLM loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load VLM: {str(e)}")
            self.model = None
            self.tokenizer = None

    def analyze_frame(
        self,
        frame: np.ndarray,
        question: str = "What are the key visual elements in this frame?",
    ) -> str:
        """
        Analyze a video frame using VLM
        
        Args:
            frame: Video frame (numpy array)
            question: Question to ask about the frame
        
        Returns:
            Description of visual elements
        """
        if self.model is None:
            return "VLM not available"
        
        try:
            # Convert frame to PIL Image
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Encode image
            enc_image = self.model.encode_image(image)
            
            # Generate description
            response = self.model.answer_question(
                enc_image,
                question,
                self.tokenizer,
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Frame analysis failed: {str(e)}")
            return ""

    def detect_text_regions(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect text regions in frame using OpenCV
        
        Args:
            frame: Video frame
        
        Returns:
            List of (x, y, width, height) tuples
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(
                binary,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE,
            )
            
            # Filter contours by size
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio and size
                if 20 < w < 500 and 10 < h < 100:
                    text_regions.append((x, y, w, h))
            
            return text_regions
            
        except Exception as e:
            logger.error(f"Text detection failed: {str(e)}")
            return []

    def detect_diagrams(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect diagram/formula regions in frame
        
        Args:
            frame: Video frame
        
        Returns:
            List of diagram information dictionaries
        """
        try:
            # Simple heuristic: detect large rectangular regions
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE,
            )
            
            diagrams = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter for diagram-like shapes
                if w > 100 and h > 100 and w * h > 10000:
                    diagrams.append({
                        "bbox": (x, y, w, h),
                        "area": w * h,
                        "type": "diagram",
                    })
            
            return diagrams
            
        except Exception as e:
            logger.error(f"Diagram detection failed: {str(e)}")
            return []

    def create_overlay(
        self,
        frame: np.ndarray,
        label: str,
        position: Tuple[int, int],
        font_scale: float = 1.0,
    ) -> np.ndarray:
        """
        Create text overlay on frame
        
        Args:
            frame: Video frame
            label: Text to overlay
            position: (x, y) position
            font_scale: Font size multiplier
        
        Returns:
            Frame with overlay
        """
        try:
            frame_copy = frame.copy()
            
            # Setup text parameters
            font = cv2.FONT_HERSHEY_SIMPLEX
            thickness = 2
            color = (0, 255, 255)  # Yellow
            bg_color = (0, 0, 0)    # Black
            
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(
                label,
                font,
                font_scale,
                thickness,
            )
            
            # Draw background rectangle
            x, y = position
            cv2.rectangle(
                frame_copy,
                (x - 5, y - text_height - 10),
                (x + text_width + 5, y + 5),
                bg_color,
                -1,
            )
            
            # Draw text
            cv2.putText(
                frame_copy,
                label,
                position,
                font,
                font_scale,
                color,
                thickness,
            )
            
            return frame_copy
            
        except Exception as e:
            logger.error(f"Overlay creation failed: {str(e)}")
            return frame

    def process_video_with_overlays(
        self,
        video_path: str,
        translations: Dict[float, str],
        output_path: str,
    ) -> str:
        """
        Process entire video and add translated overlays
        
        Args:
            video_path: Input video path
            translations: Dictionary mapping timestamps to translated labels
            output_path: Output video path
        
        Returns:
            Output video path
        """
        try:
            logger.info(f"Processing video with overlays: {video_path}")
            
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_num = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                timestamp = frame_num / fps
                
                # Check if there's a translation for this timestamp
                if timestamp in translations:
                    label = translations[timestamp]
                    # Add overlay at top center
                    position = (width // 2 - 100, 50)
                    frame = self.create_overlay(frame, label, position)
                
                out.write(frame)
                frame_num += 1
            
            cap.release()
            out.release()
            
            logger.info(f"Overlay processing complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Video overlay processing failed: {str(e)}")
            raise


# Singleton instance
_vision_sync_service: Optional[VisionSyncService] = None


def get_vision_sync_service() -> VisionSyncService:
    """Get or create Vision-Sync service instance"""
    global _vision_sync_service
    if _vision_sync_service is None:
        _vision_sync_service = VisionSyncService()
    return _vision_sync_service
