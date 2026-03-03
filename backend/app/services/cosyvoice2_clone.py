"""
CosyVoice2 - Zero-Shot Voice Cloning Service

Features:
- Zero-shot voice cloning from 3-10 second audio samples
- Cross-lingual voice cloning (clone English voice, speak Hindi)
- High-fidelity voice replication
- Natural prosody and emotion preservation
- Real-time synthesis capability

CosyVoice2 Paper: https://arxiv.org/abs/2409.xxxxx
Repository: https://github.com/FunAudioLLM/CosyVoice
"""

from app.core.logger import logger
from app.core.config import settings
from typing import Optional, List, Dict, Tuple
import torch
import torchaudio
import numpy as np
import os
import tempfile
import subprocess
from pathlib import Path


class CosyVoice2Service:
    """
    Zero-Shot Voice Cloning using CosyVoice2
    
    Pipeline:
    1. Extract 5-10 second voice sample from original video
    2. Encode speaker characteristics into embedding
    3. Generate target language speech with cloned voice
    4. Maintain prosody, pitch, and emotion
    
    Requirements:
    - PyTorch with CUDA (GPU recommended)
    - CosyVoice2 model weights (~2GB)
    - librosa, soundfile for audio processing
    """

    def __init__(self, model_path: Optional[str] = None, device: str = "auto"):
        """
        Initialize CosyVoice2 service
        
        Args:
            model_path: Path to CosyVoice2 model weights
            device: 'cuda', 'cpu', or 'auto' (auto-detect)
        """
        logger.info("Initializing CosyVoice2 Zero-Shot Voice Cloning Service")
        
        # Auto-detect device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Using device: {self.device}")
        
        # Model paths
        self.model_path = model_path or os.path.join(settings.MODEL_DIR, "cosyvoice2")
        self.available = False
        
        # Try to load model
        try:
            self._load_model()
        except Exception as e:
            logger.warning(f"CosyVoice2 model not available: {e}")
            logger.info("Voice cloning will use fallback TTS")
    
    def _load_model(self):
        """Load CosyVoice2 model weights"""
        try:
            # Check if model exists
            if not os.path.exists(self.model_path):
                logger.info(f"CosyVoice2 model not found at {self.model_path}")
                logger.info("To use voice cloning, download model:")
                logger.info("git clone https://github.com/FunAudioLLM/CosyVoice.git")
                return
            
            # Import CosyVoice2 (only if model exists)
            try:
                from cosyvoice.cli.cosyvoice import CosyVoice2
                from cosyvoice.utils.file_utils import load_wav
                
                # Load model
                self.model = CosyVoice2(self.model_path)
                self.load_wav = load_wav
                self.available = True
                
                logger.info("✅ CosyVoice2 model loaded successfully")
                logger.info(f"Model supports: Zero-shot cross-lingual voice cloning")
                
            except ImportError as e:
                logger.warning(f"CosyVoice2 library not installed: {e}")
                logger.info("Install: pip install cosyvoice")
                
        except Exception as e:
            logger.error(f"Failed to load CosyVoice2 model: {e}")
    
    def extract_voice_sample(
        self, 
        audio_path: str, 
        duration: float = 5.0,
        offset: float = 5.0
    ) -> str:
        """
        Extract a clean voice sample from audio for cloning
        
        Args:
            audio_path: Path to source audio file
            duration: Duration of sample in seconds (3-10 recommended)
            offset: Start time offset in seconds (skip intro)
        
        Returns:
            Path to extracted voice sample
        """
        try:
            logger.info(f"Extracting {duration}s voice sample from {audio_path}")
            
            # Create temp file for sample
            sample_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
            
            # Use ffmpeg to extract clean audio segment
            # Apply noise reduction and normalization
            cmd = [
                'ffmpeg', '-i', audio_path,
                '-ss', str(offset),  # Start offset
                '-t', str(duration),  # Duration
                '-af', 'highpass=f=200,lowpass=f=3000,volume=2',  # Clean voice frequency range
                '-ar', '22050',  # Resample to 22kHz (CosyVoice2 native rate)
                '-ac', '1',  # Mono
                '-y', sample_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                timeout=30,
                check=True
            )
            
            # Validate sample
            if os.path.exists(sample_path) and os.path.getsize(sample_path) > 1000:
                logger.info(f"✅ Voice sample extracted: {os.path.getsize(sample_path)} bytes")
                return sample_path
            else:
                raise ValueError("Extracted sample is too small or invalid")
                
        except Exception as e:
            logger.error(f"Voice sample extraction failed: {e}")
            raise
    
    def clone_voice(
        self,
        reference_audio: str,
        target_text: str,
        language: str = "hi",
        output_path: str = None
    ) -> str:
        """
        Clone voice from reference and generate speech in target language
        
        Args:
            reference_audio: Path to 3-10s voice sample
            target_text: Text to synthesize in cloned voice
            language: Target language code
            output_path: Output audio file path
        
        Returns:
            Path to generated audio with cloned voice
        """
        if not self.available:
            raise RuntimeError("CosyVoice2 model not available")
        
        try:
            logger.info(f"Cloning voice from {reference_audio}")
            logger.info(f"Generating: '{target_text[:50]}...' in {language}")
            
            # Load reference audio
            reference_wav = self.load_wav(reference_audio, target_sr=22050)
            
            # Generate speech with cloned voice (zero-shot)
            # CosyVoice2 supports cross-lingual cloning
            # Can clone English voice and speak Hindi
            output = self.model.inference_zero_shot(
                text=target_text,
                prompt_speech=reference_wav,
                language=language,
                stream=False
            )
            
            # Save output
            if output_path is None:
                output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
            
            # Convert tensor to audio file
            torchaudio.save(
                output_path,
                output['wav'].cpu(),
                sample_rate=22050
            )
            
            logger.info(f"✅ Voice cloned successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            raise
    
    def clone_voice_segments(
        self,
        reference_audio: str,
        segments: List[Dict],
        language: str = "hi",
        output_path: str = None
    ) -> str:
        """
        Generate audio for multiple segments with cloned voice
        
        Args:
            reference_audio: Path to voice sample
            segments: List of text segments with timing
            language: Target language
            output_path: Output audio path
        
        Returns:
            Path to combined audio file
        """
        if not self.available:
            raise RuntimeError("CosyVoice2 model not available")
        
        try:
            logger.info(f"Generating {len(segments)} segments with cloned voice")
            
            # Load reference audio once
            reference_wav = self.load_wav(reference_audio, target_sr=22050)
            
            # Generate each segment
            segment_files = []
            for i, segment in enumerate(segments):
                text = segment.get('translated', segment.get('text', ''))
                if not text.strip():
                    continue
                
                logger.info(f"Segment {i+1}/{len(segments)}: {text[:40]}...")
                
                # Generate audio for this segment
                output = self.model.inference_zero_shot(
                    text=text,
                    prompt_speech=reference_wav,
                    language=language,
                    stream=False
                )
                
                # Save segment audio
                segment_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
                torchaudio.save(
                    segment_file,
                    output['wav'].cpu(),
                    sample_rate=22050
                )
                segment_files.append(segment_file)
            
            # Combine all segments
            if output_path is None:
                output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
            
            self._concatenate_audio_segments(segment_files, output_path)
            
            # Cleanup temp files
            for f in segment_files:
                try:
                    os.remove(f)
                except:
                    pass
            
            logger.info(f"✅ All segments generated with cloned voice: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Segment voice cloning failed: {e}")
            raise
    
    def _concatenate_audio_segments(self, segment_files: List[str], output_path: str):
        """Concatenate multiple audio files with silence between them"""
        try:
            # Create concat file for ffmpeg
            concat_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
            for f in segment_files:
                concat_file.write(f"file '{f}'\n")
            concat_file.close()
            
            # Use ffmpeg to concatenate
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', concat_file.name,
                '-c', 'copy',
                '-y', output_path
            ]
            
            subprocess.run(cmd, capture_output=True, timeout=60, check=True)
            
            # Cleanup
            os.remove(concat_file.name)
            
        except Exception as e:
            logger.error(f"Audio concatenation failed: {e}")
            raise
    
    def get_speaker_embedding(self, audio_path: str) -> np.ndarray:
        """
        Extract speaker embedding from audio sample
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Speaker embedding vector (numpy array)
        """
        if not self.available:
            raise RuntimeError("CosyVoice2 model not available")
        
        try:
            # Load audio
            wav = self.load_wav(audio_path, target_sr=22050)
            
            # Extract speaker embedding
            embedding = self.model.extract_speaker_embedding(wav)
            
            return embedding.cpu().numpy()
            
        except Exception as e:
            logger.error(f"Speaker embedding extraction failed: {e}")
            raise
    
    def supports_language(self, language: str) -> bool:
        """Check if language is supported for voice cloning"""
        # CosyVoice2 supports major languages including:
        supported = ['en', 'hi', 'zh', 'ja', 'ko', 'es', 'fr', 'de']
        return language in supported
    
    def estimate_synthesis_time(self, text_length: int) -> float:
        """
        Estimate synthesis time in seconds
        
        Args:
            text_length: Number of characters
        
        Returns:
            Estimated time in seconds
        """
        # Rough estimate: ~0.1s per character on GPU, ~0.5s on CPU
        per_char_time = 0.1 if self.device == "cuda" else 0.5
        return text_length * per_char_time


def get_cosyvoice2_service() -> CosyVoice2Service:
    """Factory function to get CosyVoice2 service instance"""
    return CosyVoice2Service()
