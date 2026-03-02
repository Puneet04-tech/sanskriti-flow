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
    'Transformers have high efficiency'
]

print("=" * 60)
print("PURE HINDI TRANSLATIONS (preserve_technical=False):")
print("=" * 60)
for text in tests:
    result = svc.translate(text, 'hi', preserve_technical=False)
    print(f"\nEN: {text}")
    print(f"HI: {result}")
print("\n" + "=" * 60)
