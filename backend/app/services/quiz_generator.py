"""
Interactive Quiz Generation Service
Uses Llama 3.1 for contextual MCQ generation
"""

from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.core.config import settings
from app.core.logger import logger
from typing import List, Dict, Optional
import json
import re


class QuizGenerationService:
    """
    Service for generating interactive quizzes from lecture transcripts
    
    Features:
    - Local LLM inference (no API calls)
    - Contextual question generation
    - Multiple difficulty levels
    - Timestamp-based quiz placement
    - Answer explanations
    """

    QUIZ_PROMPT_TEMPLATE = """You are an expert educator creating quiz questions from lecture content.

Lecture Transcript:
{transcript}

Generate {num_questions} multiple-choice questions based on the above transcript. Each question should:
1. Test understanding of key concepts
2. Have 4 options (A, B, C, D)
3. Have exactly one correct answer
4. Include a brief explanation

Format your response as JSON:
[
  {{
    "question": "What is...",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Brief explanation...",
    "difficulty": "easy|medium|hard"
  }}
]

Generate only valid JSON, no additional text."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize quiz generation service
        
        Args:
            model_path: Path to Llama model file
        """
        self.model_path = model_path or settings.LLAMA_MODEL
        
        logger.info(f"Initializing Llama model: {self.model_path}")
        
        try:
            # Initialize LlamaCpp
            self.llm = LlamaCpp(
                model_path=self.model_path,
                n_ctx=4096,  # Context window
                n_threads=8,
                n_gpu_layers=32 if settings.USE_GPU else 0,
                temperature=0.7,
                max_tokens=2048,
                verbose=False,
            )
            
            # Create prompt template
            self.prompt = PromptTemplate(
                template=self.QUIZ_PROMPT_TEMPLATE,
                input_variables=["transcript", "num_questions"],
            )
            
            # Create chain
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
            
            logger.info("Llama model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Llama model: {str(e)}")
            raise

    def generate_quiz(
        self,
        transcript: str,
        num_questions: int = 5,
    ) -> List[Dict]:
        """
        Generate quiz questions from transcript
        
        Args:
            transcript: Lecture transcript text
            num_questions: Number of questions to generate
        
        Returns:
            List of quiz question dictionaries
        """
        try:
            logger.info(f"Generating {num_questions} quiz questions")
            
            # Generate questions
            response = self.chain.run(
                transcript=transcript[:3000],  # Limit context
                num_questions=num_questions,
            )
            
            # Parse JSON response
            questions = self._parse_quiz_response(response)
            
            logger.info(f"Generated {len(questions)} quiz questions")
            
            return questions
            
        except Exception as e:
            logger.error(f"Quiz generation failed: {str(e)}")
            raise

    def generate_quiz_from_segments(
        self,
        segments: List[Dict],
        questions_per_segment: int = 1,
    ) -> List[Dict]:
        """
        Generate quizzes with timestamps from transcript segments
        
        Args:
            segments: List of transcript segments with timestamps
            questions_per_segment: Questions to generate per segment
        
        Returns:
            List of quiz questions with timestamps
        """
        quizzes = []
        
        # Group segments into chunks (e.g., every 5 minutes)
        chunk_duration = 300  # 5 minutes
        chunks = self._chunk_segments(segments, chunk_duration)
        
        for chunk in chunks:
            # Get transcript text for this chunk
            chunk_text = " ".join(seg["text"] for seg in chunk)
            
            # Generate questions
            questions = self.generate_quiz(
                chunk_text,
                num_questions=questions_per_segment,
            )
            
            # Add timestamp (middle of chunk)
            if chunk:
                timestamp = (chunk[0]["start"] + chunk[-1]["end"]) / 2
                for question in questions:
                    question["timestamp"] = timestamp
                    question["segment_start"] = chunk[0]["start"]
                    question["segment_end"] = chunk[-1]["end"]
                
                quizzes.extend(questions)
        
        return quizzes

    def _chunk_segments(
        self,
        segments: List[Dict],
        chunk_duration: float,
    ) -> List[List[Dict]]:
        """
        Split segments into time-based chunks
        
        Args:
            segments: List of segments
            chunk_duration: Duration of each chunk in seconds
        
        Returns:
            List of segment chunks
        """
        chunks = []
        current_chunk = []
        chunk_start = 0
        
        for segment in segments:
            if segment["start"] - chunk_start > chunk_duration:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [segment]
                chunk_start = segment["start"]
            else:
                current_chunk.append(segment)
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    def _parse_quiz_response(self, response: str) -> List[Dict]:
        """
        Parse LLM response into structured quiz format
        
        Args:
            response: Raw LLM output
        
        Returns:
            List of quiz dictionaries
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                questions = json.loads(json_str)
                return questions
            else:
                logger.warning("Could not parse quiz JSON, returning empty list")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse quiz JSON: {str(e)}")
            return []

    def validate_quiz(self, quiz: Dict) -> bool:
        """
        Validate quiz structure
        
        Args:
            quiz: Quiz dictionary
        
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["question", "options", "correct_answer", "explanation"]
        
        if not all(field in quiz for field in required_fields):
            return False
        
        if len(quiz["options"]) != 4:
            return False
        
        if not 0 <= quiz["correct_answer"] < 4:
            return False
        
        return True


# Singleton instance
_quiz_service: Optional[QuizGenerationService] = None


def get_quiz_service() -> QuizGenerationService:
    """Get or create quiz generation service instance"""
    global _quiz_service
    if _quiz_service is None:
        _quiz_service = QuizGenerationService()
    return _quiz_service
