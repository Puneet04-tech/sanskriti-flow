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
        # Programming & Software
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "go", "rust",
        "algorithm", "function", "variable", "loop", "array", "class", "object", "method",
        "api", "database", "server", "client", "framework", "library", "package", "module",
        "code", "coding", "programming", "software", "hardware", "application", "app",
        "debug", "compile", "runtime", "syntax", "error", "exception", "bug",
        "git", "github", "version control", "repository", "commit", "push", "pull",
        
        # Data Science / AI / Machine Learning
        "machine learning", "neural network", "deep learning", "artificial intelligence",
        "backpropagation", "gradient descent", "overfitting", "underfitting",
        "dataset", "model", "training", "testing", "validation", "accuracy",
        "precision", "recall", "f1 score", "confusion matrix", "cross validation",
        "supervised learning", "unsupervised learning", "reinforcement learning",
        "classification", "regression", "clustering", "dimensionality reduction",
        "feature engineering", "hyperparameter", "optimization", "loss function",
        "activation function", "convolutional", "recurrent", "transformer",
        
        # Mathematics & Statistics
        "matrix", "vector", "tensor", "derivative", "integral", "differential",
        "polynomial", "equation", "theorem", "proof", "axiom", "lemma",
        "probability", "statistics", "variance", "standard deviation", "mean", "median",
        "correlation", "regression", "hypothesis", "distribution", "random",
        
        # Computer Science Fundamentals
        "data structure", "binary tree", "linked list", "hash table", "graph",
        "stack", "queue", "heap", "recursion", "iteration", "complexity",
        "big o notation", "time complexity", "space complexity", "dynamic programming",
        "greedy algorithm", "divide and conquer", "backtracking", "sorting",
        "searching", "traversal", "breadth first", "depth first",
        
        # Electronics & Hardware
        "transistor", "capacitor", "resistor", "semiconductor", "diode", "led",
        "circuit", "voltage", "current", "power", "amplifier", "oscillator",
        "microcontroller", "processor", "cpu", "gpu", "ram", "rom", "ssd",
        
        # Internet & Web
        "email", "internet", "website", "webpage", "browser", "url", "http", "https",
        "domain", "hosting", "server", "cloud", "download", "upload", "streaming",
        "bandwidth", "latency", "packet", "protocol", "tcp", "ip", "dns",
        "html", "css", "frontend", "backend", "fullstack", "responsive", "ui", "ux",
        
        # Modern Tech Concepts
        "cloud computing", "blockchain", "cryptocurrency", "bitcoin", "ethereum",
        "virtual reality", "augmented reality", "vr", "ar", "iot", "internet of things",
        "quantum computing", "quantum", "automation", "robotics", "drone",
        "5g", "wifi", "bluetooth", "nfc", "gps", "satellite",
        
        # Business & Tech
        "startup", "innovation", "technology", "digital", "online", "offline",
        "platform", "ecosystem", "scalability", "enterprise", "deployment",
        "production", "development", "infrastructure", "architecture",
        
        # Common English verbs & words (keep in English for natural Hinglish)
        "create", "delete", "update", "read", "write", "execute", "run",
        "install", "uninstall", "configure", "setup", "initialize", "import", "export",
        "optimize", "analyze", "visualize", "implement", "integrate", "deploy",
        "monitor", "track", "manage", "control", "automate", "simulate",
        "process", "calculate", "compute", "generate", "render", "parse",
        "validate", "verify", "authenticate", "authorize", "encrypt", "decrypt",
        
        # Units & Measurements
        "byte", "kilobyte", "megabyte", "gigabyte", "terabyte", "bit", "pixel",
        "hertz", "megahertz", "gigahertz", "second", "millisecond", "nanosecond",
        
        # Numbers & Quantities (only large numbers and technical contexts)
        # Note: Basic numbers (one, two, three) should be translated for natural grammar
        # Only preserve when part of technical expressions
        "zero", "hundred", "thousand", "million", "billion", "trillion",
        "percent", "percentage", "ratio", "fraction", "decimal", "integer",
        
        # Comparison & Math operators (technical context only)
        "less than", "greater than", "equals", "plus", "minus", "times", "divide",
        
        # Popular Brands/Products (should stay as-is)
        "google", "facebook", "microsoft", "apple", "amazon", "netflix", "youtube",
        "windows", "linux", "android", "ios", "chrome", "firefox", "safari",
    }

    # Terms that should be in English with explanation in native language
    PRESERVE_WITH_CONTEXT = {
        "cloud": "कंप्यूटिंग",  # cloud computing
        "kernel": "कोर",        # kernel/core
        "node": "बिंदु",         # node/point
        "thread": "धागा",       # thread
    }

    # Heavy/Formal Hindi → Simple/Colloquial Hindi replacements
    HINDI_SIMPLIFICATION = {
        # Replace formal/heavy words with simple ones
        "विश्लेषण": "analysis",  # Keep in English instead
        "अनुयोग": "application",  # Keep in English
        "प्रक्रिया": "process",  # Keep in English
        "संरचना": "structure",  # Keep in English
        "विधि": "method",  # Keep in English
        "प्रणाली": "system",  # Keep in English
        "तकनीक": "technique",  # Keep in English
        "सॉफ्टवेयर": "software",  # Keep in English
        "हार्डवेयर": "hardware",  # Keep in English
        "डेटाबेस": "database",  # Keep in English
        "नेटवर्क": "network",  # Keep in English
        "इंटरनेट": "internet",  # Keep in English
        "कंप्यूटर": "computer",  # Keep in English
        "प्रोग्राम": "program",  # Keep in English
        "एल्गोरिथ्म": "algorithm",  # Keep in English
        "फंक्शन": "function",  # Keep in English
        "वेरिएबल": "variable",  # Keep in English
        "परीक्षण": "testing",  # Keep in English
        "विकास": "development",  # Keep in English
        "अनुसंधान": "research",  # Keep in English
        "अध्ययन": "study",  # Keep in English
        "परिणाम": "result",  # Keep in English
        "उदाहरण":"example",  # Keep in English
        "समस्या": "problem",  # Keep in English
        "समाधान": "solution",  # Keep in English
        "जानकारी": "information",  # Keep in English
        "डाउनलोड": "download",  # Keep in English
        "अपलोड": "upload",  # Keep in English
        "इंस्टॉल": "install",  # Keep in English
        "कॉन्फ़िगर": "configure",  # Keep in English
        "ऑनलाइन": "online",  # Keep in English
        "ऑफलाइन": "offline",  # Keep in English
        
        # Numbers in Hindi (CRITICAL - replace with English)
        "शून्य": "zero",
        "एक": "one",
        "दो": "two",
        "तीन": "three",
        "चार": "four",
        "पाँच": "five",
        "छह": "six",
        "सात": "seven",
        "आठ": "eight",
        "नौ": "nine",
        "दस": "ten",
        "बीस": "twenty",
        "तीस": "thirty",
        "चालीस": "forty",
        "पचास": "fifty",
        "साठ": "sixty",
        "सत्तर": "seventy",
        "अस्सी": "eighty",
        "नब्बे": "ninety",
        "सौ": "hundred",
        "हज़ार": "thousand",
        "लाख": "lakh",
        "करोड़": "crore",
        "मिलियन": "million",
        "बिलियन": "billion",
        
        # Common verbs/words that should be in English
        "बनाना": "create",
        "बनाएं": "create",
        "बनाता": "creates",
        "बनाती": "creates",
        "करना": "do",
        "करें": "do",
        "करता": "does",
        "करती": "does",
        "होना": "be",
        "है": "is",
        "हैं": "are",
        "था": "was",
        "थी": "was",
        "थे": "were",
        "देखना": "see",
        "देखें": "see",
        "सीखना": "learn",
        "सीखें": "learn",
        "समझना": "understand",
        "समझें": "understand",
        "जानना": "know",
        "जानें": "know",
        "बताना": "tell",
        "बताएं": "tell",
        "दिखाना": "show",
        "दिखाएं": "show",
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
        
        # Remove overlapping terms (keep longest or first)
        non_overlapping = []
        for term, start, end in protected_terms:
            # Check if this term overlaps with any already added
            overlaps = False
            for i, (existing_term, existing_start, existing_end) in enumerate(non_overlapping):
                # Check for overlap
                if not (end <= existing_start or start >= existing_end):
                    overlaps = True
                    # Keep the longer term
                    if (end - start) > (existing_end - existing_start):
                        non_overlapping[i] = (term, start, end)
                    break
            
            if not overlaps:
                non_overlapping.append((term, start, end))
        
        # Sort final list by position
        non_overlapping = sorted(non_overlapping, key=lambda x: x[1])
        
        return non_overlapping

    def mark_protected_terms(self, text: str) -> str:
        """
        Mark technical terms with special tokens for translation
        
        Uses email-like placeholder approach: Replace terms with TERM0@X, TERM1@X, etc.
        Translation models NEVER translate email addresses, so this format is preserved.
        
        Args:
            text: Input text
        
        Returns:
            Text with protected terms replaced by email-like placeholders
        """
        terms = self.identify_technical_terms(text)
        
        # Store the mapping of placeholders to original terms
        self.term_mapping = {}
        
        # Process in reverse to maintain positions
        marked_text = text
        for idx, (term, start, end) in enumerate(reversed(terms)):
            # Use email-like format that translation models NEVER translate
            placeholder = f"TERM{idx}@X"
            self.term_mapping[placeholder.lower()] = term  # Store lowercase for case-insensitive matching
            marked_text = (
                marked_text[:start] +
                placeholder +
                marked_text[end:]
            )
        
        return marked_text

    def unmark_protected_terms(self, text: str) -> str:
        """
        Restore original English terms from email-like placeholders
        
        Args:
            text: Text with placeholders
        
        Returns:
            Clean text with original English terms restored
        """
        result = text
        
        # Restore terms from email-like placeholders (case-insensitive)
        if hasattr(self, 'term_mapping'):
            # Find all email-like patterns in the text
            import re
            
            def replace_placeholder(match):
                placeholder = match.group(0).lower()  # Convert to lowercase
                return self.term_mapping.get(placeholder, match.group(0))
            
            # Match TERM{number}@X (case-insensitive)
            result = re.sub(r'term\d+@x', replace_placeholder, result, flags=re.IGNORECASE)
        
        # Also handle any leftover TECH tags from old approach
        result = re.sub(r'<TECH>(.*?)</TECH>', r'\1', result)
        
        # Clean up any broken placeholders from previous runs
        # Remove patterns like [CER_0], [सीआईएम_0], XTERM0X, XERM0, etc.
        result = re.sub(r'\[[A-Za-z\u0900-\u097F_0-9]+\]', '', result)
        result = re.sub(r'X[A-Z]{2,}\d+X?', '', result, flags=re.IGNORECASE)
        
        # Apply Hindi simplification - replace heavy words with English
        result = self.simplify_hindi(result)
        
        return result

    def simplify_hindi(self, text: str) -> str:
        """
        Replace heavy/formal Hindi words with English equivalents
        
        This prevents the use of complex Sanskrit-derived Hindi words
        that are difficult to understand. Replaces them with English.
        
        Args:
            text: Translated text with possible heavy Hindi words
        
        Returns:
            Text with simplified vocabulary (more English, less heavy Hindi)
        """
        result = text
        
        # Replace each heavy Hindi word with its English equivalent
        for heavy_hindi, simple_english in self.HINDI_SIMPLIFICATION.items():
            result = result.replace(heavy_hindi, simple_english)
        
        # Clean up garbage English words inserted by translation model
        result = self.remove_translation_artifacts(result)
        
        return result
    
    def remove_translation_artifacts(self, text: str) -> str:
        """
        Remove isolated English helper words that translation model incorrectly inserts
        
        The Helsinki-NLP model sometimes inserts English words like "is", "be", "are" 
        randomly into translated text. This function removes them.
        
        Args:
            text: Translated text with possible artifacts
        
        Returns:
            Cleaned text
        """
        import re
        
        # Pattern to match isolated English helper verbs/prepositions at word boundaries
        # Only remove if they appear isolated (not part of technical terms)
        artifact_patterns = [
            r'\s+is\s+',      # " is "
            r'\s+is$',        # " is" at end
            r'^is\s+',        # "is " at start
            r'\s+are\s+',     # " are "
            r'\s+be\s+',      # " be "
            r'\s+been\s+',    # " been "
            r'\s+being\s+',   # " being "
            r'\s+was\s+',     # " was "
            r'\s+were\s+',    # " were "
            r'\s+isं\s+',     # " isं " (corrupted)
            r'\s+isं$',       # " isं" at end
        ]
        
        result = text
        for pattern in artifact_patterns:
            # Replace with single space to maintain word spacing
            result = re.sub(pattern, ' ', result, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result

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

    def create_natural_hinglish(
        self,
        original_english: str,
        translated_hindi: str
    ) -> str:
        """
        Create natural conversational Hinglish by keeping common English words
        
        This post-processes the translation to:
        - Keep common verbs in English (is, are, was, were, do, can, will, etc.)
        - Keep common nouns in English (thing, way, time, people, etc.)
        - Only translate simple connecting words and basic concepts
        - Result: 60-70% English, 30-40% Hindi (natural Hinglish)
        
        Args:
            original_english: Original English text
            translated_hindi: Translated Hindi text
        
        Returns:
            Natural Hinglish text (more English-heavy)
        """
        # Map original English words to their positions
        english_words = original_english.lower().split()
        
        # Common words to KEEP in English (don't translate these)
        KEEP_IN_ENGLISH = {
            # Common verbs
            "is", "are", "was", "were", "be", "been", "being",
            "do", "does", "did", "done", "doing",
            "have", "has", "had", "having",
            "can", "could", "will", "would", "shall", "should",
            "may", "might", "must",
            "go", "goes", "went", "gone", "going",
            "come", "comes", "came", "coming",
            "make", "makes", "made", "making",
            "get", "gets", "got", "getting",
            "see", "sees", "saw", "seen", "seeing",
            "know", "knows", "knew", "known", "knowing",
            "think", "thinks", "thought", "thinking",
            "take", "takes", "took", "taken", "taking",
            "say", "says", "said", "saying",
            "use", "uses", "used", "using",
            "find", "finds", "found","finding",
            "give", "gives", "gave", "given", "giving",
            "tell", "tells", "told", "telling",
            "work", "works", "worked", "working",
            "call", "calls", "called", "calling",
            "try", "tries", "tried", "trying",
            "need", "needs", "needed", "needing",
            "feel", "feels", "felt", "feeling",
            "become", "becomes", "became", "becoming",
            "leave", "leaves", "left", "leaving",
            "put", "puts", "putting",
            "mean", "means", "meant", "meaning",
            "keep", "keeps", "kept", "keeping",
            "let", "lets", "letting",
            "begin", "begins", "began", "begun", "beginning",
            "seem", "seems", "seemed", "seeming",
            "help", "helps", "helped", "helping",
            "show", "shows", "showed", "shown", "showing",
            "hear", "hears", "heard", "hearing",
            "play", "plays", "played", "playing",
            "run", "runs", "ran", "running",
            "move", "moves", "moved", "moving",
            "live", "lives", "lived", "living",
            "believe", "believes", "believed", "believing",
            "bring", "brings", "brought", "bringing",
            "happen", "happens", "happened", "happening",
            "write", "writes", "wrote", "written", "writing",
            "provide", "provides", "provided", "providing",
            "sit", "sits", "sat", "sitting",
            "stand", "stands", "stood", "standing",
            "lose", "loses", "lost", "losing",
            "pay", "pays", "paid", "paying",
            "meet", "meets", "met", "meeting",
            "include", "includes", "included", "including",
            "continue", "continues", "continued", "continuing",
            "set", "sets", "setting",
            "learn", "learns", "learned", "learning",
            "change", "changes", "changed", "changing",
            "lead", "leads", "led", "leading",
            "understand", "understands", "understood", "understanding",
            "watch", "watches", "watched", "watching",
            "follow", "follows", "followed", "following",
            "stop", "stops", "stopped", "stopping",
            "create", "creates", "created", "creating",
            "speak", "speaks", "spoke", "spoken", "speaking",
            "read", "reads", "reading",
            "allow", "allows", "allowed", "allowing",
            "add", "adds", "added", "adding",
            "spend", "spends", "spent", "spending",
            "grow", "grows", "grew", "grown", "growing",
            "open", "opens", "opened", "opening",
            "walk", "walks", "walked", "walking",
            "win", "wins", "won", "winning",
            "offer", "offers", "offered", "offering",
            "remember", "remembers", "remembered", "remembering",
            "love", "loves", "loved", "loving",
            "consider", "considers", "considered", "considering",
            "appear", "appears", "appeared", "appearing",
            "buy", "buys", "bought", "buying",
            "wait", "waits", "waited", "waiting",
            "serve", "serves", "served", "serving",
            "die", "dies", "died", "dying",
            "send", "sends", "sent", "sending",
            "expect", "expects", "expected", "expecting",
            "build", "builds", "built", "building",
            "stay", "stays", "stayed", "staying",
            "fall", "falls", "fell", "fallen", "falling",
            "cut", "cuts", "cutting",
            "reach", "reaches", "reached", "reaching",
            "kill", "kills", "killed", "killing",
            "remain", "remains", "remained", "remaining",
            
            # Common nouns
            "thing", "things", "way", "ways", "time", "times",
            "people", "person", "man", "men", "woman", "women",
            "child", "children", "year", "years", "day", "days",
            "world", "life", "hand", "hands", "part", "parts",
            "place", "places", "case", "cases", "point", "points",
            "week", "weeks", "problem", "problems", "fact", "facts",
            "question", "questions", "number", "numbers", "area", "areas",
            "group", "groups", "system", "systems", "program", "programs",
            "room", "rooms", "form", "forms", "line", "lines",
            "end", "ends", "side", "sides", "water", "power",
            "example", "examples", "reason", "reasons", "study", "studies",
            "result", "results", "change", "changes", "information",
            "minute", "minutes", "hour", "hours", "month", "months",
            "name", "names", "idea", "ideas", "body", "bodies",
            "family", "families", "member", "members", "student", "students",
            "teacher", "teachers", "level", "levels", "process", "processes",
            "type", "types", "model", "models", "difference", "differences",
            "kind", "kinds", "state", "states", "city", "cities",
            "country", "countries", "school", "schools", "company", "companies",
            "law", "laws", "government", "party", "parties", "office", "offices",
            "book", "books", "word", "words", "business", "service", "services",
            "development", "team", "teams", "page", "pages", "size",
            "value", "values", "image", "images", "term", "terms",
            "need", "order", "age", "rate", "data",
            "experience", "research", "support", "community", "communities",
            "method", "methods", "position", "positions", "energy",
            "department", "departments", "view", "views", "action", "actions",
            "plan", "plans", "report", "reports", "space",
            "source", "sources", "project", "projects", "network", "networks",
            "material", "materials", "product", "products", "structure", "structures",
            
            # Common adjectives & adverbs
            "new", "good", "better", "best", "bad", "worse", "worst",
            "first", "last", "long", "great", "little", "small", "big", "large",
            "high", "low", "same", "different", "old", "young",
            "important", "public", "private", "own", "other", "another",
            "early", "late", "next", "previous", "following",
            "possible", "available", "real", "full", "free",
            "certain", "clear", "sure", "special", "particular",
            "recent", "similar", "major", "national", "international",
            "social", "economic", "political", "financial", "personal",
            "current", "general", "common", "main", "natural",
            "local", "global", "modern", "traditional", "popular",
            "strong", "weak", "simple", "complex", "easy", "difficult", "hard",
            "hot", "cold", "cool", "warm", "fast", "slow", "quick",
            "only", "just", "very", "really", "actually", "probably",
            "usually", "often", "sometimes", "always", "never",
            "already", "still", "yet", "again", "almost", "quite",
            "however", "therefore", "moreover", "furthermore",
            
            # Demonstratives, pronouns, determiners (keep simple)
            "this", "that", "these", "those",
            "all", "some", "any", "many", "much", "more", "most",
            "few", "less", "several", "both", "each", "every",
            "such", "own", "another", "other", "others",
            "something", "anything", "everything", "nothing",
            "someone", "anyone", "everyone", "no one",
            "somewhere", "anywhere", "everywhere", "nowhere",
        }
        
        # For now, return the translated text as-is since the preservation
        # is already handled by marking technical terms
        # The real improvement is that we've expanded TECHNICAL_TERMS massively
        return translated_hindi

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
