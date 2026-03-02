"""
Simple Rule-Based Quiz Generator
Generates MCQs from transcripts using pattern matching and NER
No LLM required - works immediately!
"""

from typing import List, Dict, Optional
import re
import random
from app.core.logger import logger

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None


class SimpleQuizGenerator:
    """
    Rule-based quiz generator using patterns and entity extraction
    """
    
    # Question templates for different patterns
    TEMPLATES = {
        "definition": [
            "What is {entity}?",
            "Which of the following best describes {entity}?",
            "What does {entity} refer to?",
        ],
        "purpose": [
            "What is the main purpose of {entity}?",
            "Why is {entity} important?",
            "What problem does {entity} solve?",
        ],
        "comparison": [
            "How does {entity1} differ from {entity2}?",
            "What is the relationship between {entity1} and {entity2}?",
        ],
        "process": [
            "What is the first step in {process}?",
            "How does {process} work?",
        ],
    }
    
    def __init__(self):
        """Initialize the quiz generator"""
        logger.info("Initializing Simple Quiz Generator")
        self.nlp = nlp
    
    def generate_quiz(
        self,
        transcript: str,
        num_questions: int = 3,
        target_language: str = "hi"
    ) -> List[Dict]:
        """
        Generate quiz questions from transcript
        
        Args:
            transcript: Full transcript text
            num_questions: Number of questions to generate
            target_language: Target language code
        
        Returns:
            List of quiz questions with options
        """
        logger.info(f"Generating {num_questions} quiz questions")
        
        try:
            # Extract key concepts
            concepts = self._extract_key_concepts(transcript)
            
            # Generate questions
            questions = []
            
            # Definition questions (from named entities)
            if concepts["entities"]:
                for i, entity in enumerate(concepts["entities"][:num_questions]):
                    q = self._generate_definition_question(entity, transcript)
                    if q:
                        questions.append(q)
                        if len(questions) >= num_questions:
                            break
            
            # Fill remaining with pattern-based questions
            while len(questions) < num_questions and concepts["keywords"]:
                keyword = random.choice(concepts["keywords"])
                q = self._generate_keyword_question(keyword, transcript)
                if q and not any(kw in str(q) for kw in [q2.get("question", "") for q2 in questions]):
                    questions.append(q)
            
            # Fallback: generic questions if not enough
            while len(questions) < num_questions:
                questions.append(self._generate_generic_question(transcript))
            
            logger.info(f"Generated {len(questions)} quiz questions")
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Quiz generation failed: {str(e)}")
            # Return at least one question
            return [self._generate_generic_question(transcript)]
    
    def _extract_key_concepts(self, text: str) -> Dict[str, List]:
        """Extract key concepts from text"""
        concepts = {
            "entities": [],
            "keywords": [],
            "numbers": []
        }
        
        # Use spaCy if available
        if self.nlp:
            try:
                doc = self.nlp(text[:5000])  # Limit for performance
                
                # Extract named entities (technical terms, organizations, etc.)
                for ent in doc.ents:
                    if ent.label_ in ["ORG", "PRODUCT", "TECH", "GPE", "EVENT"]:
                        if len(ent.text) > 3 and ent.text not in concepts["entities"]:
                            concepts["entities"].append(ent.text)
                
                # Extract noun phrases as keywords
                for chunk in doc.noun_chunks:
                    if len(chunk.text.split()) >= 2 and chunk.text not in concepts["keywords"]:
                        concepts["keywords"].append(chunk.text)
                        if len(concepts["keywords"]) >= 20:
                            break
            except:
                pass
        
        # Fallback: extract capitalized words as entities
        if not concepts["entities"]:
            pattern = r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)+\b'
            entities = re.findall(pattern, text)
            concepts["entities"] = list(set(entities))[:10]
        
        # Extract numbers with context
        number_pattern = r'(\d+(?:\.\d+)?)\s*(\w+)'
        numbers = re.findall(number_pattern, text)
        concepts["numbers"] = numbers[:5]
        
        return concepts
    
    def _generate_definition_question(self, entity: str, context: str) -> Optional[Dict]:
        """Generate a definition question about an entity"""
        # Find sentence containing the entity
        sentences = context.split('.')
        relevant_sentence = None
        for sent in sentences:
            if entity.lower() in sent.lower():
                relevant_sentence = sent.strip()
                break
        
        if not relevant_sentence:
            return None
        
        # Generate question
        question_text = random.choice(self.TEMPLATES["definition"]).format(entity=entity)
        
        # Generate plausible wrong answers
        wrong_answers = [
            f"A type of software framework",
            f"A programming language feature",
            f"A mathematical concept",
            f"A hardware component"
        ]
        
        # Correct answer (simplified from sentence)
        correct_answer = relevant_sentence[:100] + "..." if len(relevant_sentence) > 100 else relevant_sentence
        
        # Shuffle options
        options = [correct_answer] + random.sample(wrong_answers, 3)
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        return {
            "question": question_text,
            "options": options,
            "correct_answer": correct_index,
            "explanation": f"{entity} is described in the lecture as: {relevant_sentence[:150]}...",
            "difficulty": "medium",
            "type": "definition"
        }
    
    def _generate_keyword_question(self, keyword: str, context: str) -> Optional[Dict]:
        """Generate a question about a keyword concept"""
        question_text = f"What is the significance of '{keyword}' in the lecture?"
        
        # Find context
        sentences = context.split('.')
        relevant = None
        for sent in sentences:
            if keyword.lower() in sent.lower():
                relevant = sent.strip()
                break
        
        if not relevant:
            return None
        
        options = [
            relevant[:80] + "...",
            "It is not mentioned in the lecture",
            "It is a minor detail",
            "It is explained in a different context"
        ]
        random.shuffle(options)
        
        return {
            "question": question_text,
            "options": options,
            "correct_answer": 0,
            "explanation": f"The lecture discusses: {relevant[:150]}...",
            "difficulty": "easy",
            "type": "comprehension"
        }
    
    def _generate_generic_question(self, context: str) -> Dict:
        """Generate a generic question as fallback"""
        # Extract first meaningful sentence
        sentences = [s.strip() for s in context.split('.') if len(s.strip()) > 20]
        first_sentence = sentences[0] if sentences else "The lecture content"
        
        return {
            "question": "What is the main topic of this lecture?",
            "options": [
                first_sentence[:80] + "...",
                "General computer science concepts",
                "Basic programming principles",
                "Advanced mathematics"
            ],
            "correct_answer": 0,
            "explanation": "The lecture begins with: " + first_sentence[:150] + "...",
            "difficulty": "easy",
            "type": "general"
        }


def get_simple_quiz_generator():
    """Factory function to get quiz generator instance"""
    return SimpleQuizGenerator()
