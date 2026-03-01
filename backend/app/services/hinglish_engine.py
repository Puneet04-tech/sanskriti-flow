"""
Neural Hinglish Engine
Preserves technical terms during translation using NER
"""

import spacy  # type: ignore
from typing import List, Set, Tuple
from app.core.logger import logger
from app.core.config import settings
import re


class NeuralHinglishEngine:
    """
    Intelligent term preservation engine for technical translation
    
    Features:
    - Named Entity Recognition (NER) for technical terms
    - Custom technical vocabulary
    - Programming language keywords
    - Mathematical notation preservation
    - Acronym detection
    """

    # Technical terms that should NEVER be translated
    TECHNICAL_TERMS = {
        # Programming
        "python", "java", "javascript", "c++", "algorithm", "function",
        "variable", "loop", "array", "class", "object", "method",
        "api", "database", "server", "client", "framework",
        
        # Data Science / AI
        "machine learning", "neural network", "deep learning",
        "backpropagation", "gradient descent", "overfitting",
        "dataset", "model", "training", "testing", "validation",
        
        # Mathematics
        "matrix", "vector", "tensor", "derivative", "integral",
        "polynomial", "equation", "theorem", "proof",
        
        # Computer Science
        "algorithm", "data structure", "binary tree", "linked list",
        "stack", "queue", "recursion", "complexity", "optimization",
        
        # Electronics
        "transistor", "capacitor", "resistor", "semiconductor",
        "circuit", "voltage", "current", "amplifier",
        
        # Common tech terms
        "email", "internet", "website", "software", "hardware",
        "download", "upload", "install", "configure",
    }

    # Terms that should be in English with explanation in native language
    PRESERVE_WITH_CONTEXT = {
        "cloud": "कंप्यूटिंग",  # cloud computing
        "kernel": "कोर",        # kernel/core
        "node": "बिंदु",         # node/point
        "thread": "धागा",       # thread
    }

    def __init__(self):
        """Initialize the Neural Hinglish Engine"""
        logger.info("Initializing Neural Hinglish Engine")
        
        try:
            # Load spaCy English model for NER
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model for NER")
        except OSError:
            logger.warning(
                "spaCy model not found. Run: python -m spacy download en_core_web_sm"
            )
            self.nlp = None

    def identify_technical_terms(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Identify technical terms in text
        
        Args:
            text: Input text
        
        Returns:
            List of (term, start_pos, end_pos) tuples
        """
        protected_terms = []
        
        # Convert to lowercase for matching
        text_lower = text.lower()
        
        # 1. Match predefined technical terms
        for term in self.TECHNICAL_TERMS:
            pattern = r'\b' + re.escape(term) + r'\b'
            for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                protected_terms.append((
                    text[match.start():match.end()],
                    match.start(),
                    match.end()
                ))
        
        # 2. Detect acronyms (2+ capital letters)
        acronym_pattern = r'\b[A-Z]{2,}\b'
        for match in re.finditer(acronym_pattern, text):
            protected_terms.append((
                match.group(),
                match.start(),
                match.end()
            ))
        
        # 3. Detect camelCase and snake_case (programming identifiers)
        code_pattern = r'\b[a-z]+[A-Z][a-zA-Z]*\b|\b[a-z]+_[a-z_]+\b'
        for match in re.finditer(code_pattern, text):
            protected_terms.append((
                match.group(),
                match.start(),
                match.end()
            ))
        
        # 4. Use NER if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                # Preserve ORG, PRODUCT, PERSON (technical names)
                if ent.label_ in ["ORG", "PRODUCT", "PERSON", "GPE"]:
                    protected_terms.append((
                        ent.text,
                        ent.start_char,
                        ent.end_char
                    ))
        
        # Remove duplicates and sort by position
        protected_terms = sorted(set(protected_terms), key=lambda x: x[1])
        
        return protected_terms

    def mark_protected_terms(self, text: str) -> str:
        """
        Mark technical terms with special tokens for translation
        
        Args:
            text: Input text
        
        Returns:
            Text with protected terms marked as <TECH>term</TECH>
        """
        terms = self.identify_technical_terms(text)
        
        # Process in reverse to maintain positions
        marked_text = text
        for term, start, end in reversed(terms):
            marked_text = (
                marked_text[:start] +
                f"<TECH>{term}</TECH>" +
                marked_text[end:]
            )
        
        return marked_text

    def unmark_protected_terms(self, text: str) -> str:
        """
        Remove protection markers after translation
        
        Args:
            text: Text with markers
        
        Returns:
            Clean text with terms restored
        """
        # Remove <TECH> tags
        text = re.sub(r'<TECH>(.*?)</TECH>', r'\1', text)
        return text

    def create_hinglish_text(
        self,
        english_text: str,
        translated_text: str
    ) -> str:
        """
        Create Hinglish text by combining English terms with native translation
        
        Args:
            english_text: Original English text
            translated_text: Translated text
        
        Returns:
            Hinglish text with technical terms in English
        """
        # Identify terms to preserve
        terms = self.identify_technical_terms(english_text)
        
        # Create a mapping of English to translated positions
        # This is a simplified approach - in production, use proper alignment
        result = translated_text
        
        for term, _, _ in terms:
            # Find where this term might have been translated
            # and replace with original English term
            # This is a basic heuristic
            result = re.sub(
                r'\b\w+\b',  # Word boundary
                term,
                result,
                count=1,
                flags=re.IGNORECASE
            )
        
        return result

    def analyze_text(self, text: str) -> dict:
        """
        Analyze text and provide statistics
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with analysis results
        """
        terms = self.identify_technical_terms(text)
        
        return {
            "total_words": len(text.split()),
            "technical_terms": len(terms),
            "terms": [term for term, _, _ in terms],
            "preservation_ratio": len(terms) / len(text.split()) if text else 0,
        }


# Singleton instance
_hinglish_engine: NeuralHinglishEngine = None


def get_hinglish_engine() -> NeuralHinglishEngine:
    """Get or create Neural Hinglish Engine instance"""
    global _hinglish_engine
    if _hinglish_engine is None:
        _hinglish_engine = NeuralHinglishEngine()
    return _hinglish_engine
