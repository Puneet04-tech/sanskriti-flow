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

    def translate_span_based(
        self,
        text: str,
        target_lang: str,
    ) -> str:
        """
        Translate using span-based approach: preserve technical terms by NOT translating them
        
        Args:
            text: Input text
            target_lang: Target language code
        
        Returns:
            Hinglish text with technical terms preserved
        """
        try:
            # Get technical terms and their positions
            terms = self.hinglish_engine.identify_technical_terms(text)
            
            if not terms:
                # No technical terms, translate normally
                return self._translate_text(text, target_lang)
            
            # Split text into spans: [(start, end, is_technical, text)]
            spans = []
            last_end = 0
            
            for term, start, end in terms:
                # Add non-technical text before this term
                if start > last_end:
                    spans.append((last_end, start, False, text[last_end:start]))
                
                # Add technical term (keep as-is)
                spans.append((start, end, True, text[start:end]))
                last_end = end
            
            # Add remaining text
            if last_end < len(text):
                spans.append((last_end, len(text), False, text[last_end:]))
            
            # Translate only non-technical spans
            translated_parts = []
            for start, end, is_technical, span_text in spans:
                if is_technical:
                    # Keep technical terms as-is
                    translated_parts.append(span_text)
                elif len(span_text.strip()) == 0:
                    # Keep whitespace/punctuation as-is
                    translated_parts.append(span_text)
                else:
                    # Translate non-technical text
                    # Detect leading/trailing whitespace
                    leading_space = span_text[:len(span_text) - len(span_text.lstrip())]
                    trailing_space = span_text[len(span_text.rstrip()):]
                    clean_text = span_text.strip()
                    
                    if clean_text:
                        translated = self._translate_text(clean_text, target_lang)
                        # Reassemble with original spacing
                        translated_parts.append(leading_space + translated + trailing_space)
                    else:
                        translated_parts.append(span_text)
            
            result = ''.join(translated_parts)
            
            # Apply Hindi simplification
            result = self.hinglish_engine.simplify_hindi(result)
            
            logger.info(f"Span-based translation: {text[:50]}... -> {result[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Span-based translation failed: {str(e)}, falling back to normal")
            return self._translate_text(text, target_lang)
    
    def _translate_text(
        self,
        text: str,
        target_lang: str,
    ) -> str:
        """
        Internal method to translate text without term preservation
        
        Args:
            text: Input text
            target_lang: Target language code
        
        Returns:
            Translated text
        """
        if len(text.strip()) == 0:
            return text
        
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
            generated_tokens = self.model.generate(
                **inputs,
                max_length=512,
                num_beams=4,
                early_stopping=True,
            )
        else:
            src_code = self.LANGUAGE_CODES.get("en", "eng_Latn")
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
        
        return translation
    
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
            if preserve_technical:
                # Use span-based translation to preserve technical terms
                return self.translate_span_based(text, target_lang)
            else:
                # Normal translation without preservation
                return self._translate_text(text, target_lang)
            
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
