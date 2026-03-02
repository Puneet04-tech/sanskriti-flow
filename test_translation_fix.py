"""Test script to verify span-based translation fixes"""

import sys
sys.path.append('d:/sanskriti-flow/backend')

from app.services.hinglish_engine import NeuralHinglishEngine
from app.services.translation import TranslationService

# Initialize services
hinglish = NeuralHinglishEngine()
translator = TranslationService()

# Test cases
test_texts = [
    "Quantum computing is a fundamentally new way of computing",
    "The technology is still one step ahead",
    "Applications range from drug discovery to risk analysis",
    "India is a global leader in IT sector"
]

print("="*60)
print("TESTING SPAN-BASED TRANSLATION FIXES")
print("="*60)

for i, text in enumerate(test_texts, 1):
    print(f"\n{i}. Input: {text}")
    
    # Identify technical terms
    terms = hinglish.identify_technical_terms(text)
    print(f"   Terms: {[term for term, _, _ in terms]}")
    
    # Translate with span-based approach
    result = translator.translate_span_based(text, "hi")
    print(f"   Output: {result}")
    
    # Check for issues
    issues = []
    if text.split()[0] * 2 in result:
        issues.append("DUPLICATE WORD")
    if "  " in result:
        issues.append("DOUBLE SPACE")
    
    if issues:
        print(f"   ⚠️  Issues: {', '.join(issues)}")
    else:
        print(f"   ✓ OK")

print("\n" + "="*60)
