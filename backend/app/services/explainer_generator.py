"""
Explainer Video Generator - Creates simplified Hinglish explanations
Converts complex educational content into easy-to-understand explanations
"""

import re
from typing import List, Dict, Optional
from app.core.logger import logger


class ExplainerGenerator:
    """
    Generates simplified Hinglish explanations of video content
    No heavy words, simple language for better understanding
    """
    
    def __init__(self):
        # Simple word replacements - complex to simple
        self.simplifications = {
            # Technical terms → Simple Hinglish
            "quantum computing": "quantum computer - ek naye tarah ka computer",
            "algorithm": "tarika ya method",
            "implementation": "banane ka tarika",
            "architecture": "design ya structure",
            "infrastructure": "basic setup",
            "configuration": "settings",
            "parameters": "values ya settings",
            "optimization": "behtar banane ka process",
            "efficiency": "kitna fast kaam karta hai",
            "scalability": "bade level par use kar sakte hain",
            "synchronization": "sath mein chalana",
            "asynchronous": "alag alag time par",
            "dependency": "jo cheez chahiye",
            "repository": "code store karne ki jagah",
            "framework": "ready-made structure",
            "middleware": "beech ki layer",
            "protocol": "rules ya niyam",
            "interface": "connection point",
            "authentication": "login check karna",
            "authorization": "permission check karna",
            "deployment": "live karna",
            "migration": "data shift karna",
            "integration": "jodna ya connect karna",
            "validation": "check karna",
            "verification": "confirm karna",
            "initialization": "shuru karna",
            "instantiation": "object banana",
            "encapsulation": "data ko safe rakhna",
            "polymorphism": "alag alag forms",
            "inheritance": "parent se properties lena",
            "exception": "error ya galti",
            "iteration": "ek ek karke chalana",
            "recursion": "apne aap ko call karna",
            "parallel": "sath sath",
            "sequential": "ek ke baad ek",
            "concurrent": "same time par",
            "database": "data store",
            "query": "data dhundna",
            "index": "quick search ke liye list",
            "cache": "temporary fast storage",
            "buffer": "temporary holding area",
            "thread": "chhoti processing unit",
            "process": "program ka running instance",
            "latency": "delay ya waiting time",
            "throughput": "kitna data process hota hai",
            "bandwidth": "data transfer speed",
            "capacity": "kitna hold kar sakta hai",
            "threshold": "limit",
            "compile": "code ko machine language mein convert karna",
            "runtime": "jab program chal raha ho",
            "compile time": "jab code compile ho raha ho",
            "syntax": "language ke rules",
            "semantics": "meaning",
            "variable": "container jisme value store hoti hai",
            "constant": "jo value change nahi hoti",
            "function": "code ka chhota piece jo koi kaam karta hai",
            "method": "class ke andar ka function",
            "class": "blueprint ya template",
            "object": "class ka instance",
            "array": "list of items",
            "list": "items ki list",
            "dictionary": "key-value pairs",
            "string": "text data",
            "integer": "pura number",
            "float": "decimal number",
            "boolean": "true ya false",
        }
        
        # Complex phrases to simple explanations
        self.phrase_explanations = {
            "machine learning": "Computer ko sikha ke kaam karwana",
            "artificial intelligence": "Computer ko smart banana",
            "deep learning": "Complex patterns seekhna",
            "neural network": "Brain ki tarah kaam karne wala system",
            "data structure": "Data ko organize karne ka tarika",
            "time complexity": "Code ko chalane mein kitna time lagta hai",
            "space complexity": "Kitna memory use hoti hai",
            "big o notation": "Code ki speed measure karne ka tarika",
            "rest api": "Internet par data lene dene ka tarika",
            "http request": "Server se kuch mangna",
            "http response": "Server ka jawab",
            "frontend": "Jo user dekhta hai - screen par",
            "backend": "Server side - jo background mein hota hai",
            "full stack": "Frontend aur backend dono",
            "database schema": "Database ki structure",
            "foreign key": "Dusre table se connection",
            "primary key": "Unique ID",
            "cloud computing": "Internet par server use karna",
            "virtual machine": "Computer ke andar virtual computer",
            "container": "Application ko bundle karke chalana",
            "microservices": "Application ko chhote parts mein divide karna",
            "load balancing": "Kaam ko equally distribute karna",
            "version control": "Code changes ko track karna",
            "git commit": "Changes save karna",
            "pull request": "Changes review ke liye bhejna",
            "code review": "Code check karna",
            "unit testing": "Chhote parts test karna",
            "integration testing": "Sab parts sath mein test karna",
            "continuous integration": "Code automatically test hota rahta hai",
            "continuous deployment": "Automatic live ho jata hai",
        }
        
        logger.info("Explainer Generator initialized with simplified vocabulary")
    
    def generate_explanation(
        self,
        segments: List[Dict],
        target_language: str = "hi"
    ) -> List[Dict]:
        """
        Generate simplified Hinglish explanation from video segments
        
        Args:
            segments: Video transcript segments
            target_language: Target language (default: Hindi)
        
        Returns:
            List of explanation segments with simplified text
        """
        explained_segments = []
        
        for segment in segments:
            original_text = segment.get("text", "")
            
            # Generate simple explanation
            explanation = self._simplify_text(original_text)
            
            # Create explanation segment
            explained_segment = {
                "start": segment.get("start", 0),
                "end": segment.get("end", 0),
                "original": original_text,
                "explanation": explanation,
                "language": "hinglish",
                "simplified": True
            }
            
            explained_segments.append(explained_segment)
        
        logger.info(f"Generated {len(explained_segments)} explanation segments")
        return explained_segments
    
    def _simplify_text(self, text: str) -> str:
        """
        Simplify complex text into easy Hinglish
        
        Steps:
        1. Replace complex technical terms
        2. Break long sentences
        3. Add simple explanations
        4. Use everyday analogies
        """
        simplified = text.lower()
        
        # Replace complex terms with simple explanations
        for complex_term, simple_term in self.simplifications.items():
            if complex_term in simplified:
                simplified = simplified.replace(complex_term, simple_term)
        
        # Replace complex phrases
        for phrase, explanation in self.phrase_explanations.items():
            if phrase in simplified:
                simplified = simplified.replace(phrase, explanation)
        
        # Add conversational markers
        simplified = self._add_conversational_style(simplified)
        
        # Remove overly technical jargon
        simplified = self._remove_jargon(simplified)
        
        return simplified
    
    def _add_conversational_style(self, text: str) -> str:
        """Add friendly conversational style"""
        
        # Add intro phrases randomly
        intro_phrases = [
            "Dekho, ",
            "Samjho aise, ",
            "Matlab ye hai ki, ",
            "Simple shabdon mein, ",
            "Ek minute, ",
        ]
        
        # Add connecting words
        connectors = {
            "therefore": "toh iska matlab",
            "however": "lekin",
            "moreover": "aur ek baat",
            "furthermore": "aage",
            "thus": "toh",
            "hence": "isliye",
            "additionally": "aur",
            "consequently": "result mein",
            "meanwhile": "same time par",
            "whereas": "jabki",
            "although": "chahe",
            "unless": "jab tak nahi",
            "whether": "kya",
            "because": "kyunki",
            "since": "kyunki",
            "if": "agar",
            "when": "jab",
            "while": "jab tak",
            "after": "ke baad",
            "before": "se pehle",
        }
        
        for english, hinglish in connectors.items():
            text = text.replace(f" {english} ", f" {hinglish} ")
        
        return text
    
    def _remove_jargon(self, text: str) -> str:
        """Remove or explain remaining technical jargon"""
        
        # Words to avoid - replace with simpler alternatives
        jargon_replacements = {
            "utilize": "use karna",
            "facilitate": "aasan banana",
            "implement": "lagana",
            "execute": "chalana",
            "terminate": "band karna",
            "initialize": "shuru karna",
            "instantiate": "banana",
            "allocate": "dena",
            "deallocate": "wapas lena",
            "invoke": "call karna",
            "trigger": "start karna",
            "subscribe": "follow karna",
            "publish": "bhejna",
            "parse": "samajhna",
            "serialize": "convert karna",
            "deserialize": "wapas convert karna",
            "encrypt": "secure karna",
            "decrypt": "unlock karna",
            "compress": "chhota karna",
            "decompress": "expand karna",
        }
        
        for jargon, simple in jargon_replacements.items():
            text = re.sub(rf'\b{jargon}\b', simple, text, flags=re.IGNORECASE)
        
        return text
    
    def create_explanation_script(
        self,
        segments: List[Dict],
        video_title: str = "Video"
    ) -> str:
        """
        Create a complete explanation script for the video
        
        Returns:
            Full script as a string
        """
        script_parts = []
        
        # Intro
        intro = f"""
Namaste dosto! Aaj hum samjhenge "{video_title}" ke baare mein.
Main aapko bilkul simple language mein samjhaunga, bina kisi heavy words ke.
Chalo shuru karte hain!
"""
        script_parts.append(intro.strip())
        
        # Main content
        for i, segment in enumerate(segments):
            explanation = segment.get("explanation", "")
            if explanation:
                # Add section markers
                if i % 3 == 0:  # Every 3 segments, add a transition
                    script_parts.append("\nAchchha, ab aage dekhte hain...")
                
                script_parts.append(explanation)
        
        # Outro
        outro = """
Toh dosto, yahi tha aaj ka topic.
Agar samajh mein aaya toh bahut badhiya!
Agar koi doubt hai, toh comments mein zaroor puchho.
Thank you, aur milte hain next video mein!
"""
        script_parts.append(outro.strip())
        
        full_script = "\n\n".join(script_parts)
        
        logger.info(f"Created explanation script: {len(full_script)} characters")
        return full_script
    
    def generate_talking_points(self, text: str) -> List[str]:
        """
        Break down explanation into key talking points
        
        Useful for creating slide-style explanations
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        talking_points = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Skip very short fragments
                # Make it a bullet point
                talking_points.append(f"• {sentence}")
        
        return talking_points
    
    def estimate_explanation_duration(self, text: str) -> float:
        """
        Estimate how long the explanation will take
        
        Assumes speaking rate of ~150 words per minute for Hinglish
        """
        word_count = len(text.split())
        words_per_minute = 150
        duration_minutes = word_count / words_per_minute
        duration_seconds = duration_minutes * 60
        
        return duration_seconds
