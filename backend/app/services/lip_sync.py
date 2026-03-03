"""
Neural Lip-Sync Service using LatentSync (Diffusion-Based)

LatentSync: High-quality lip-sync using latent diffusion models
Paper: https://arxiv.org/abs/2312.xxxxx
Features:
- Diffusion-based facial re-rendering
- Audio-driven mouth movement generation
- Preserves face identity and expression
- High-resolution output (up to 1080p)
- Multi-speaker support

Alternative: Wav2Lip (faster but lower quality)
"""

from app.core.logger import logger
from app.core.config import settings
from typing import Optional, List, Tuple
import torch
import cv2
import numpy as np
import os
import tempfile
import subprocess
from pathlib import Path


class LatentSyncService:
    """
    Neural lip-sync using LatentSync diffusion model
    
    Pipeline:
    1. Detect faces in video frames
    2. Extract face regions and audio features
    3. Generate lip movements using diffusion model
    4. Blend synced faces back into original video
    5. Preserve identity and expression fidelity
    
    Requirements:
    - PyTorch with CUDA (GPU strongly recommended)
    - LatentSync model weights (~5GB)
    - Face detection model (RetinaFace/MTCNN)
    - Audio processing (librosa)
    """

    def __init__(self, model_path: Optional[str] = None, device: str = "auto"):
        """
        Initialize LatentSync service
        
        Args:
            model_path: Path to LatentSync model weights
            device: 'cuda', 'cpu', or 'auto'
        """
        logger.info("Initializing LatentSync Neural Lip-Sync Service")
        
        # Auto-detect device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Using device: {self.device}")
        
        # Model paths
        self.model_path = model_path or os.path.join(settings.MODEL_DIR, "latentsync")
        self.available = False
        
        # Face detection model
        self.face_detector = None
        
        # Try to load models
        try:
            self._load_models()
        except Exception as e:
            logger.warning(f"LatentSync models not available: {e}")
            logger.info("Lip-sync will use fallback method (audio merge only)")
    
    def _load_models(self):
        """Load LatentSync and face detection models"""
        try:
            # Check if models exist
            if not os.path.exists(self.model_path):
                logger.info(f"LatentSync model not found at {self.model_path}")
                logger.info("To enable lip-sync, download model:")
                logger.info("git clone https://huggingface.co/LatentSync/model latentsync")
                return
            
            # Import LatentSync (only if model exists)
            try:
                # Try to import from installed package
                from latentsync import LatentSyncModel
                from latentsync.face_detector import RetinaFaceDetector
                
                # Load LatentSync diffusion model
                self.model = LatentSyncModel.from_pretrained(
                    self.model_path,
                    device=self.device
                )
                
                # Load face detector
                self.face_detector = RetinaFaceDetector(device=self.device)
                
                self.available = True
                logger.info("✅ LatentSync model loaded successfully")
                logger.info("Neural lip-sync ready for diffusion-based rendering")
                
            except ImportError as e:
                logger.warning(f"LatentSync library not installed: {e}")
                logger.info("Install: pip install latentsync")
                
                # Fallback: Try to use Wav2Lip as alternative
                try:
                    from Wav2Lip import Wav2LipModel
                    logger.info("Using Wav2Lip as fallback (faster but lower quality)")
                    self.model = Wav2LipModel(device=self.device)
                    self.available = True
                except ImportError:
                    logger.warning("Neither LatentSync nor Wav2Lip available")
                
        except Exception as e:
            logger.error(f"Failed to load lip-sync models: {e}")
    
    def detect_faces(self, video_path: str) -> List[dict]:
        """
        Detect faces in video frames
        
        Args:
            video_path: Path to video file
        
        Returns:
            List of face detections per frame: [
                {
                    "frame_idx": 0,
                    "bbox": [x1, y1, x2, y2],
                    "landmarks": [[x, y], ...],
                    "confidence": 0.99
                }
            ]
        """
        if not self.face_detector:
            logger.warning("Face detector not available")
            return []
        
        try:
            logger.info(f"Detecting faces in {video_path}")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            detections = []
            frame_idx = 0
            
            # Process every 5th frame for efficiency
            sample_rate = 5
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_rate == 0:
                    # Detect faces in this frame
                    faces = self.face_detector.detect(frame)
                    
                    for face in faces:
                        detections.append({
                            "frame_idx": frame_idx,
                            "bbox": face["bbox"],
                            "landmarks": face["landmarks"],
                            "confidence": face["confidence"]
                        })
                
                frame_idx += 1
            
            cap.release()
            
            logger.info(f"Detected {len(detections)} face instances in {total_frames} frames")
            return detections
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []
    
    def extract_audio_features(self, audio_path: str) -> np.ndarray:
        """
        Extract audio features for lip-sync
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Audio feature array (spectrograms, mel features, etc.)
        """
        try:
            import librosa
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Extract mel-spectrogram (used by most lip-sync models)
            mel_spec = librosa.feature.melspectrogram(
                y=audio,
                sr=sr,
                n_mels=80,
                fmax=8000
            )
            
            # Convert to log scale
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            return mel_spec_db.T  # (time, features)
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return np.array([])
    
    def sync_video(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        face_bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> str:
        """
        Apply neural lip-sync to video with new audio
        
        Args:
            video_path: Input video path
            audio_path: New audio track path (dubbed/translated)
            output_path: Output video path
            face_bbox: Optional face bounding box (x1, y1, x2, y2)
        
        Returns:
            Path to lip-synced video
        """
        if not self.available:
            logger.warning("LatentSync not available. Using audio merge fallback.")
            return self._fallback_audio_merge(video_path, audio_path, output_path)
        
        try:
            logger.info(f"Applying LatentSync neural lip-sync to {video_path}")
            
            # Step 1: Detect faces (if bbox not provided)
            if face_bbox is None:
                detections = self.detect_faces(video_path)
                if not detections:
                    logger.warning("No faces detected. Using audio merge fallback.")
                    return self._fallback_audio_merge(video_path, audio_path, output_path)
                
                # Use first detected face
                face_bbox = detections[0]["bbox"]
            
            # Step 2: Extract audio features
            audio_features = self.extract_audio_features(audio_path)
            
            # Step 3: Process video with LatentSync
            output_path = self._process_with_latentsync(
                video_path=video_path,
                audio_features=audio_features,
                face_bbox=face_bbox,
                output_path=output_path
            )
            
            # Step 4: Merge synced video with new audio
            output_path = self._merge_audio(output_path, audio_path, output_path)
            
            logger.info(f"✅ Lip-sync completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Lip-sync failed: {e}. Using fallback.")
            return self._fallback_audio_merge(video_path, audio_path, output_path)
    
    def _process_with_latentsync(
        self,
        video_path: str,
        audio_features: np.ndarray,
        face_bbox: Tuple[int, int, int, int],
        output_path: str
    ) -> str:
        """
        Core LatentSync processing: diffusion-based lip re-rendering
        
        Args:
            video_path: Input video
            audio_features: Extracted audio features (mel-spectrograms)
            face_bbox: Face bounding box
            output_path: Output path
        
        Returns:
            Path to synced video
        """
        try:
            logger.info("Running LatentSync diffusion model...")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_idx = 0
            x1, y1, x2, y2 = face_bbox
            
            # Process each frame
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Get audio features for this frame
                audio_window = self._get_audio_window(audio_features, frame_idx, fps)
                
                # Extract face region
                face_region = frame[y1:y2, x1:x2]
                
                # Generate synced lip movements using diffusion model
                synced_face = self.model.generate(
                    face_region=face_region,
                    audio_features=audio_window,
                    num_inference_steps=3,  # Reduced from 5 to 3 for 40% faster processing
                    guidance_scale=7.5
                )
                
                # Blend synced face back into frame
                frame[y1:y2, x1:x2] = synced_face
                
                # Write frame
                out.write(frame)
                
                frame_idx += 1
                
                # Progress logging
                if frame_idx % 30 == 0:
                    progress = (frame_idx / total_frames) * 100
                    logger.info(f"Lip-sync progress: {progress:.1f}%")
            
            # Cleanup
            cap.release()
            out.release()
            
            logger.info(f"LatentSync processing complete: {frame_idx} frames")
            return output_path
            
        except Exception as e:
            logger.error(f"LatentSync processing failed: {e}")
            raise
    
    def _get_audio_window(
        self,
        audio_features: np.ndarray,
        frame_idx: int,
        fps: float,
        window_size: int = 5
    ) -> np.ndarray:
        """
        Get audio feature window for current frame
        
        Args:
            audio_features: Full audio features
            frame_idx: Current frame index
            fps: Video FPS
            window_size: Number of frames in window
        
        Returns:
            Audio feature window
        """
        # Calculate corresponding audio frame
        audio_frame = int((frame_idx / fps) * 50)  # Assuming 50 fps for audio features
        
        # Get window
        start = max(0, audio_frame - window_size // 2)
        end = min(len(audio_features), audio_frame + window_size // 2)
        
        window = audio_features[start:end]
        
        # Pad if necessary
        if len(window) < window_size:
            padding = window_size - len(window)
            window = np.pad(window, ((0, padding), (0, 0)), mode='edge')
        
        return window
    
    def _fallback_audio_merge(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> str:
        """
        Fallback: Just merge new audio without lip-sync
        
        Args:
            video_path: Input video
            audio_path: New audio
            output_path: Output path
        
        Returns:
            Path to output video
        """
        try:
            logger.info("Using fallback: merging audio without lip-sync")
            
            # Use ffmpeg to replace audio track
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',  # Copy video stream
                '-map', '0:v:0',  # Video from first input
                '-map', '1:a:0',  # Audio from second input
                '-shortest',  # Match shortest stream
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300,
                check=True
            )
            
            logger.info(f"Audio merged successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Audio merge failed: {e}")
            raise
    
    def _merge_audio(self, video_path: str, audio_path: str, output_path: str) -> str:
        """Merge audio with video using ffmpeg"""
        return self._fallback_audio_merge(video_path, audio_path, output_path)
    
    def estimate_processing_time(self, video_duration: float) -> float:
        """
        Estimate lip-sync processing time
        
        Args:
            video_duration: Video duration in seconds
        
        Returns:
            Estimated time in seconds
        """
        if not self.available:
            return 10  # Just audio merge
        
        # LatentSync is slow: ~10 seconds per second of video on GPU
        # ~60 seconds per second on CPU
        if self.device == "cuda":
            return video_duration * 10
        else:
            return video_duration * 60
    
    def supports_language(self, language: str) -> bool:
        """Check if language is supported (all languages supported)"""
        return True  # Lip-sync is language-agnostic


# Singleton instances
_latentsync_service: Optional[LatentSyncService] = None


def get_lip_sync_service() -> LatentSyncService:
    """Get or create LatentSync service instance"""
    global _latentsync_service
    if _latentsync_service is None:
        _latentsync_service = LatentSyncService()
    return _latentsync_service
