import redis
import json

r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
job_id = "5f4b01d6-69c9-4772-9afd-df6a9fa8fec1"
result_key = f"celery-task-meta-{job_id}"
result_json = r.get(result_key)
result = json.loads(result_json)

print(f"\n✅ Job Status: {result['status']}")
print(f"\n📝 Translation Samples (first 3 segments):")
for i, segment in enumerate(result['result']['translated_segments'][:3], 1):
    print(f"\n  [{i}] Original: {segment['original'][:60]}...")
    print(f"      Translated: {segment['translated'][:60]}...")

print(f"\n🎯 Quizzes Generated: {len(result['result']['quizzes'])}")
if result['result']['quizzes']:
    print(f"   First Question: {result['result']['quizzes'][0]['question'][:80]}...")
    
print(f"\n📂 Output Path: {result['result']['output_path']}")
print(f"\n💾 Metadata: {result['result']['metadata']}")
