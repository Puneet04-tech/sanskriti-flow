"""
Translation Service
Uses NLLB-200 (Meta) for multilingual translation
"""

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from app.core.config import settings
from app.core.logger import logger
from app.services.hinglish_engine import get_hinglish_engine
from typing import List, Dict, Optional
import torch


class TranslationService:
    """
    Service for translating text using NLLB-200
    
    Features:
    - 200+ language support
    - Local processing (no API calls)
    - GPU acceleration
    - Technical term preservation (Neural Hinglish)
    - Batch processing support
    """

    # NLLB language codes mapping
    LANGUAGE_CODES = {
        "hi": "hin_Deva",  # Hindi
        "ta": "tam_Taml",  # Tamil
        "te": "tel_Telu",  # Telugu
        "bn": "ben_Beng",  # Bengali
        "mr": "mar_Deva",  # Marathi
        "gu": "guj_Gujr",  # Gujarati
        "kn": "kan_Knda",  # Kannada
        "ml": "mal_Mlym",  # Malayalam
        "pa": "pan_Guru",  # Punjabi
        "or": "ory_Orya",  # Odia
        "en": "eng_Latn",  # English
    }

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize translation service
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name or settings.NLLB_MODEL
        self.device = "cuda" if settings.USE_GPU and torch.cuda.is_available() else "cpu"
        
        # Check if using Helsinki-NLP opus model (simpler, lighter)
        self.is_opus_model = "Helsinki-NLP" in self.model_name or "opus-mt" in self.model_name
        
        logger.info(f"Initializing translation model: {self.model_name} on {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            
            if settings.USE_GPU:
                self.model.half()  # Use FP16 for faster inference
            
            logger.info("Translation model loaded successfully")
            
            # Initialize Hinglish Engine
            self.hinglish_engine = get_hinglish_engine()
            
        except Exception as e:
            logger.error(f"Failed to load translation model: {str(e)}")
            raise

    def translate(
        self,
        text: str,
        target_lang: str,
        source_lang: str = "en",
        preserve_technical: bool = True,
    ) -> str:
        """
        Translate text to target language
        
        Args:
            text: Input text
            target_lang: Target language code (hi, ta, etc.)
            source_lang: Source language code (default: en)
            preserve_technical: Whether to preserve technical terms
        
        Returns:
            Translated text
        """
        try:
            # Mark technical terms if preservation is enabled
            if preserve_technical:
                text = self.hinglish_engine.mark_protected_terms(text)
            
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            ).to(self.device)
            
            # Generate translation
            if self.is_opus_model:
                # Simpler generation for opus models (no language codes needed)
                generated_tokens = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True,
                )
            else:
                # NLLB-style generation with language codes
                src_code = self.LANGUAGE_CODES.get(source_lang, "eng_Latn")
                tgt_code = self.LANGUAGE_CODES.get(target_lang)
                
                if not tgt_code:
                    raise ValueError(f"Unsupported target language: {target_lang}")
                
                self.tokenizer.src_lang = src_code
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_code],
                    max_length=512,
                    num_beams=5,
                    length_penalty=1.0,
                )
            
            # Decode
            translation = self.tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True
            )[0]
            
            # Unmark technical terms
            if preserve_technical:
                translation = self.hinglish_engine.unmark_protected_terms(translation)
            
            logger.info(f"Translated: {text[:50]}... -> {translation[:50]}...")
            
            return translation
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise

    def translate_batch(
        self,
        texts: List[str],
        target_lang: str,
        source_lang: str = "en",
        preserve_technical: bool = True,
    ) -> List[str]:
        """
        Translate multiple texts in batch
        
        Args:
            texts: List of input texts
            target_lang: Target language code
            source_lang: Source language code
            preserve_technical: Whether to preserve technical terms
        
        Returns:
            List of translated texts
        """
        return [
            self.translate(text, target_lang, source_lang, preserve_technical)
            for text in texts
        ]

    def translate_segments(
        self,
        segments: List[Dict],
        target_lang: str,
        preserve_technical: bool = True,
    ) -> List[Dict]:
        """
        Translate transcript segments
        
        Args:
            segments: List of segment dictionaries with 'text' field
            target_lang: Target language code
            preserve_technical: Whether to preserve technical terms
        
        Returns:
            List of segments with translated text
        """
        translated_segments = []
        
        for segment in segments:
            translated_segment = segment.copy()
            translated_segment["text"] = self.translate(
                segment["text"],
                target_lang,
                preserve_technical=preserve_technical,
            )
            translated_segment["original_text"] = segment["text"]
            translated_segments.append(translated_segment)
        
        return translated_segments

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        return list(self.LANGUAGE_CODES.keys())


# Singleton instance
_translation_service: Optional[TranslationService] = None


def get_translation_service() -> TranslationService:
    """Get or create translation service instance"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
