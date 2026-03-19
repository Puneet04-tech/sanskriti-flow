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
        Translate with word-level English preservation for natural Hinglish
        
        Strategy:
        1. Identify words to keep in English (technical + common)
        2. Build spans: English words + spaces to translate
        3. Translate only non-English spans
        4. Merge spans back together
        
        Args:
            text: English text to translate
            target_lang: Target language code (e.g., 'hi')
        
        Returns:
            Hinglish text with English words preserved
        """
        import re
        
        try:
            # Step 1: Identify all words to keep in English
            words_to_keep = set()
            
            # Get technical terms from engine
            terms = self.hinglish_engine.identify_technical_terms(text)
            for term, _, _ in terms:
                # Add each word in the technical term
                for word in term.split():
                    if len(word) > 1:
                        words_to_keep.add(word.lower())
            
            # Also check against TECHNICAL_TERMS list
            text_lower = text.lower()
            for tech_term in self.hinglish_engine.TECHNICAL_TERMS:
                if tech_term in text_lower:
                    for word in tech_term.split():
                        if len(word) > 1:
                            words_to_keep.add(word.lower())
            
            # Step 2: Build word-level spans
            words = re.findall(r'\b\w+\b|[^\w\s]', text)  # Extract words and punctuation
            spans = []  # List of (text, keep_english)
            current_hindi_span = []
            
            for word in words:
                word_clean = re.sub(r'[^a-zA-Z0-9]', '', word).lower()
                
                # Check if this word should stay in English
                if word_clean in words_to_keep or len(word_clean) == 0:
                    # First, flush any accumulated Hindi span
                    if current_hindi_span:
                        hindi_text = ' '.join(current_hindi_span)
                        spans.append((hindi_text, False))  # Needs translation
                        current_hindi_span = []
                    
                    # Add English word
                    spans.append((word, True))  # Keep as-is
                else:
                    # Accumulate for Hindi translation
                    current_hindi_span.append(word)
            
            # Flush remaining Hindi span
            if current_hindi_span:
                hindi_text = ' '.join(current_hindi_span)
                spans.append((hindi_text, False))
            
            # Step 3: Translate non-English spans
            result_parts = []
            for text_part, keep_english in spans:
                if keep_english:
                    result_parts.append(text_part)
                else:
                    # Translate this span to Hindi
                    if text_part.strip():
                        translated = self._translate_text(text_part, target_lang)
                        translated = self.hinglish_engine.simplify_hindi(translated)
                        result_parts.append(translated)
            
            # Step 4: Merge with proper spacing
            result = ' '.join(result_parts)
            result = re.sub(r'\s+([.,!?;:])', r'\1', result)  # Fix punctuation spacing
            result = re.sub(r'\s+', ' ', result).strip()
            
            logger.info(f"Hinglish translation: {text[:40]}... -> {result[:40]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"Hinglish translation failed: {str(e)}, falling back to normal")
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

        def _get_target_bos_id(tgt_code: str) -> int:
            """Resolve target language BOS token id across tokenizer variants."""
            if hasattr(self.tokenizer, "lang_code_to_id"):
                lang_map = getattr(self.tokenizer, "lang_code_to_id") or {}
                if tgt_code in lang_map:
                    return int(lang_map[tgt_code])

            token_id = self.tokenizer.convert_tokens_to_ids(tgt_code)
            if token_id is None:
                raise ValueError(f"Could not resolve token id for target language code: {tgt_code}")

            try:
                token_id = int(token_id)
            except Exception:
                raise ValueError(f"Invalid token id for target language code {tgt_code}: {token_id}")

            if token_id < 0:
                raise ValueError(f"Tokenizer returned invalid token id for {tgt_code}: {token_id}")

            return token_id
        
        # Generate translation
        if self.is_opus_model:
            generated_tokens = self.model.generate(
                **inputs,
                max_length=512,
                num_beams=5,  # Increased for better quality
                early_stopping=True,
                length_penalty=1.0,
                repetition_penalty=1.2,  # Avoid repetitions
                no_repeat_ngram_size=3,  # Better quality
            )
        else:
            src_code = self.LANGUAGE_CODES.get("en", "eng_Latn")
            tgt_code = self.LANGUAGE_CODES.get(target_lang)
            
            if not tgt_code:
                raise ValueError(f"Unsupported target language: {target_lang}")
            
            if hasattr(self.tokenizer, "src_lang"):
                self.tokenizer.src_lang = src_code

            target_bos_id = _get_target_bos_id(tgt_code)
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=target_bos_id,
                max_length=512,
                num_beams=5,  # Maximum quality beam search
                length_penalty=1.0,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                early_stopping=True,
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
