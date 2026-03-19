import json

with open('data/output/5f4b01d6-69c9-4772-9afd-df6a9fa8fec1.json') as f:
    data = json.load(f)

print(f"✅ JSON Sidecar Quizzes: {len(data.get('quizzes', []))}")
print(f"\n📋 Quiz Questions:")
for i, q in enumerate(data.get('quizzes', []), 1):
    print(f"  {i}. {q['question'][:70]}...")
