import sys
sys.path.insert(0, 'd:/sanskriti-flow/backend')

from app.services.translation import get_translation_service

print("Loading translation service...")
svc = get_translation_service()
print("Service loaded\n")

tests = [
    'Hello, in this short video, I will tell you about the course coverage',
    'The transformer operates at 50 hertz frequency',
    'DC machines are widely used in industry',
    'Transformers have high efficiency of 99 percent',
    'The power transmission system uses AC current',
    'Electrical machines play an important role'
]

print("=" * 70)
print("HINGLISH MODE (Hindi + English technical terms):")
print("=" * 70)
for text in tests:
    result = svc.translate(text, 'hi', preserve_technical=True)
    print(f"\nEN: {text}")
    print(f"HI: {result}")

print("\n" + "=" * 70)
print("\nNote: Technical terms (transformer, DC, AC, etc.) kept in English")
print("Grammar and common words translated to Hindi")
print("=" * 70)
