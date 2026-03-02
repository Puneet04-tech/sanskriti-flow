"""
Test Quiz Generation
"""
import sys
sys.path.insert(0, "d:\\sanskriti-flow\\backend")

from app.services.simple_quiz_generator import get_simple_quiz_generator

# Sample transcript from a technical video
sample_transcript = """
Hello, in this short video, I will tell you about the course coverage. 
The transformer operates at 50 hertz frequency. DC machines are widely used in industry.
Transformers have high efficiency of 99 percent. The power transmission system uses AC current.
Electrical machines play an important role in power systems. A transformer is an electrical device 
that transfers electrical energy between circuits through electromagnetic induction. 
The efficiency of modern transformers typically exceeds 95 percent.
"""

print("Testing Quiz Generation...")
print("="*60)

try:
    generator = get_simple_quiz_generator()
    print("Quiz generator initialized successfully!")
    print()
    
    quizzes = generator.generate_quiz(sample_transcript, num_questions=3, target_language="hi")
    
    print(f"Generated {len(quizzes)} quiz questions:")
    print()
    
    for i, quiz in enumerate(quizzes, 1):
        print(f"Question {i}: {quiz.get('question', 'N/A')}")
        print(f"Options:")
        for j, opt in enumerate(quiz.get('options', [])):
            marker = "✓" if j == quiz.get('correct_answer', -1) else " "
            print(f"  {marker} {chr(65+j)}. {opt}")
        print(f"Correct Answer: {chr(65 + quiz.get('correct_answer', 0))}")
        print(f"Explanation: {quiz.get('explanation', 'N/A')}")
        print(f"Difficulty: {quiz.get('difficulty', 'N/A')}")
        print()
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
