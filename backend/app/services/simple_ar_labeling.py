"""
Simple AR Labeling Service
Uses OpenCV for text/object detection and adds translated labels
No heavy ML models required - works immediately!
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from app.core.logger import logger
import re


class SimpleARLabelingService:
    """
    Simple AR labeling using OpenCV for detection
    """
    
    def __init__(self):
        """Initialize AR labeling service"""
        logger.info("Initializing Simple AR Labeling Service")
        self.detected_labels = []
    
    def process_video(
        self,
        video_path: str,
        output_path: str,
        translations: Dict[str, str],
        sample_rate: int = 30
    ) -> str:
        """
        Add AR labels to video
        
        Args:
            video_path: Input video file
            output_path: Output video with labels
            translations: Dict of English -> Target language labels
            sample_rate: Process every Nth frame for performance
        
        Returns:
            Path to output video
        """
        logger.info(f"Processing video for AR labels: {video_path}")
        
        try:
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception("Cannot open video file")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            detected_regions = {}  # Cache detected regions
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every Nth frame for detection
                if frame_count % sample_rate == 0:
                    detected_regions = self._detect_label_regions(frame)
                
                # Add labels to frame
                labeled_frame = self._add_labels_to_frame(
                    frame,
                    detected_regions,
                    translations
                )
                
                out.write(labeled_frame)
                frame_count += 1
                
                if frame_count % 100 == 0:
                    logger.info(f"Processed {frame_count}/{total_frames} frames")
            
            cap.release()
            out.release()
            
            logger.info(f"AR labeling complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"AR labeling failed: {str(e)}")
            raise
    
    def _detect_label_regions(self, frame: np.ndarray) -> Dict[str, List]:
        """
        Detect regions where labels should be placed
        
        Args:
            frame: Video frame
        
        Returns:
            Dict of detected regions with positions
        """
        regions = {
            "text_boxes": [],
            "high_contrast_areas": [],
            "diagram_boxes": []
        }
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect text regions using edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours (potential text/diagram boxes)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter by size (avoid noise)
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                # Text boxes: rectangular, moderate size
                if 1000 < area < 50000 and 0.2 < w/h < 5:
                    regions["text_boxes"].append({
                        "position": (x, y, w, h),
                        "area": area,
                        "type": "text"
                    })
                
                # Diagram boxes: larger, more square
                elif 50000 < area < 200000 and 0.5 < w/h < 2:
                    regions["diagram_boxes"].append({
                        "position": (x, y, w, h),
                        "area": area,
                        "type": "diagram"
                    })
            
            # Detect high-contrast areas (likely text/important content)
            _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            white_pixels = cv2.countNonZero(thresh)
            
            if white_pixels > gray.size * 0.1:  # More than 10% white
                regions["high_contrast_areas"].append({
                    "coverage": white_pixels / gray.size,
                    "type": "text_heavy"
                })
            
        except Exception as e:
            logger.warning(f"Detection failed: {str(e)}")
        
        return regions
    
    def _add_labels_to_frame(
        self,
        frame: np.ndarray,
        regions: Dict[str, List],
        translations: Dict[str, str]
    ) -> np.ndarray:
        """
        Add translated labels to frame
        
        Args:
            frame: Original frame
            regions: Detected regions
            translations: Translation dictionary
        
        Returns:
            Frame with labels added
        """
        labeled_frame = frame.copy()
        
        try:
            # Add labels to text boxes
            for i, text_box in enumerate(regions.get("text_boxes", [])[:5]):  # Limit to 5
                x, y, w, h = text_box["position"]
                
                # Pick a translation based on position (simplified)
                if translations:
                    label_key = list(translations.keys())[i % len(translations)]
                    label_text = translations[label_key]
                    
                    # Draw semi-transparent background
                    overlay = labeled_frame.copy()
                    cv2.rectangle(overlay, (x, y-30), (x+w, y), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.6, labeled_frame, 0.4, 0, labeled_frame)
                    
                    # Draw label text
                    cv2.putText(
                        labeled_frame,
                        label_text[:30],  # Limit length
                        (x+5, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 255),  # Yellow text
                        1,
                        cv2.LINE_AA
                    )
                    
                    # Draw box around region
                    cv2.rectangle(labeled_frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
            
            # Add labels to diagram boxes
            for i, diagram_box in enumerate(regions.get("diagram_boxes", [])[:3]):  # Limit to 3
                x, y, w, h = diagram_box["position"]
                
                # Add "Diagram" label
                label_text = "चित्र" if "diagram" in str(diagram_box) else "Diagram"
                
                # Draw annotation
                cv2.rectangle(labeled_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(
                    labeled_frame,
                    label_text,
                    (x+5, y+20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2,
                    cv2.LINE_AA
                )
            
            # Add watermark showing AR is active
            cv2.putText(
                labeled_frame,
                "AR Labels Active",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )
            
        except Exception as e:
            logger.warning(f"Label drawing failed: {str(e)}")
            return frame
        
        return labeled_frame
    
    def generate_label_data(
        self,
        segments: List[Dict],
        hinglish_engine
    ) -> Dict[str, str]:
        """
        Generate label translations from segments
        
        Args:
            segments: Translated segments
            hinglish_engine: Hinglish engine for term extraction
        
        Returns:
            Dictionary of English -> Hinglish labels
        """
        labels = {}
        
        try:
            for segment in segments:
                # Extract technical terms from original English
                original = segment.get("original", "")
                
                if hinglish_engine and original:
                    terms = hinglish_engine.identify_technical_terms(original)
                    
                    for term, _, _ in terms[:10]:  # Limit to 10 terms per segment
                        if term not in labels and len(term) > 3:
                            # Use the term itself (it's already technical English)
                            labels[term] = term
            
            logger.info(f"Generated {len(labels)} AR labels")
            
        except Exception as e:
            logger.error(f"Label generation failed: {str(e)}")
        
        return labels


def get_simple_ar_service():
    """Factory function to get AR service instance"""
    return SimpleARLabelingService()
