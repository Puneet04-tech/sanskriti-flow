# CosyVoice2 Integration Guide

## Quick Start

### 1. Installation

```bash
# Install CosyVoice2
pip install cosyvoice

# Or from source
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice
pip install -r requirements.txt
python setup.py install
```

### 2. Download Model

```bash
# Download pretrained model (~2GB)
mkdir -p backend/data/models
cd backend/data/models

# Option 1: HuggingFace
git clone https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B cosyvoice2

# Option 2: Direct download
wget https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B/resolve/main/pytorch_model.bin
```

### 3. Configuration

Update `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings
    
    # CosyVoice2 settings
    MODEL_DIR: str = "data/models"
    COSYVOICE2_MODEL_PATH: str = "data/models/cosyvoice2"
    ENABLE_VOICE_CLONING: bool = True  # Enable by default if model exists
```

### 4. Test Installation

```python
# Test script
from app.services.cosyvoice2_clone import get_cosyvoice2_service

# Initialize service
cosyvoice2 = get_cosyvoice2_service()

# Check availability
if cosyvoice2.available:
    print("✅ CosyVoice2 ready for voice cloning")
else:
    print("❌ CosyVoice2 not available - will use fallback TTS")
```

## API Usage

### Enable Voice Cloning in Request

```bash
curl -X POST "http://localhost:8000/api/v1/localize/" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/professor_lecture.mp4",
    "target_language": "hi",
    "enable_voice_clone": true,
    "enable_quiz": true,
    "enable_vision_sync": true
  }'
```

### Response

```json
{
  "job_id": "abc-123-xyz",
  "status": "processing",
  "message": "Job submitted successfully"
}
```

### Check Job Status

```bash
curl "http://localhost:8000/api/v1/jobs/abc-123-xyz"
```

Response with voice cloning:
```json
{
  "job_id": "abc-123-xyz",
  "status": "completed",
  "progress": 100,
  "result_url": "https://cdn.../output_cloned.mp4",
  "voice_cloning_enabled": true,
  "voice_sample_duration": 7.0,
  "stage": "Complete"
}
```

## Processing Pipeline

### Flow with Voice Cloning:

```
1. Video Upload
   ↓
2. Extract Audio (FFmpeg)
   ↓
3. Transcribe (Faster-Whisper)
   ↓
4. Translate/Explain
   ↓
5. Voice Cloning Branch:
   ├─ Extract 7s voice sample from original audio
   ├─ Filter & normalize (200Hz-3kHz, volume=2)
   ├─ Load CosyVoice2 model
   ├─ Encode speaker characteristics
   ├─ Generate target language audio with cloned voice
   └─ Merge all segments
   ↓
6. Add AR Labels (Vision-Sync)
   ↓
7. Generate Quiz
   ↓
8. Merge Audio + Video
   ↓
9. Output Localized Video ✅
```

### Fallback Logic:

```python
if enable_voice_clone:
    try:
        # Attempt CosyVoice2 cloning
        voice_sample = extract_voice_sample(audio, duration=7.0)
        cloned_audio = cosyvoice2.clone_voice_segments(
            reference_audio=voice_sample,
            segments=translated_segments,
            language=target_language
        )
    except Exception as e:
        logger.warning(f"Voice cloning failed: {e}")
        # Fallback to standard TTS
        cloned_audio = gtts.generate_speech(translated_segments)
else:
    # Use standard TTS
    cloned_audio = gtts.generate_speech(translated_segments)
```

## Code Integration Points

### 1. Service Layer

**File**: `backend/app/services/cosyvoice2_clone.py`

Key methods:
- `extract_voice_sample()` - Extract clean 5-10s sample
- `clone_voice()` - Clone voice for single text
- `clone_voice_segments()` - Clone voice for multiple segments
- `get_speaker_embedding()` - Extract speaker embedding vector

### 2. Worker Pipeline

**File**: `backend/app/workers/tasks.py`

Integration at **Stage 5**:
```python
# Stage 5: Generate audio with voice cloning or TTS
enable_voice_clone = options.get("enable_voice_clone", False)

if enable_voice_clone and self.cosyvoice2 and self.cosyvoice2.available:
    # Zero-shot voice cloning
    voice_sample = self.cosyvoice2.extract_voice_sample(audio_path)
    hindi_audio_path = self.cosyvoice2.clone_voice_segments(
        reference_audio=voice_sample,
        segments=translated_segments,
        language=target_language
    )
else:
    # Standard TTS fallback
    hindi_audio_path = tts_service.generate_speech_from_segments(...)
```

### 3. Schema

**File**: `backend/app/models/schemas.py`

```python
class LocalizationRequest(BaseModel):
    # ... existing fields
    enable_voice_clone: bool = Field(
        False, 
        description="Clone speaker's voice using CosyVoice2"
    )
```

## Performance Optimization

### GPU Acceleration

```python
# Initialize with GPU
cosyvoice2 = CosyVoice2Service(device="cuda")

# Check GPU memory
import torch
if torch.cuda.is_available():
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

### Batch Processing

```python
# Process multiple segments in batch
cloned_audio = cosyvoice2.clone_voice_segments(
    reference_audio=voice_sample,
    segments=translated_segments,  # All segments at once
    language=target_language
)
```

### Caching

```python
# Cache speaker embeddings for multiple videos from same speaker
speaker_embedding = cosyvoice2.get_speaker_embedding(voice_sample)

# Reuse embedding for multiple syntheses
for text in texts:
    audio = cosyvoice2.synthesize_with_embedding(
        text=text,
        speaker_embedding=speaker_embedding
    )
```

## Quality Control

### Voice Sample Validation

```python
def validate_voice_sample(audio_path):
    """Ensure voice sample is suitable for cloning"""
    
    # Check duration (3-10s recommended)
    duration = get_audio_duration(audio_path)
    if duration < 3 or duration > 10:
        raise ValueError(f"Sample duration {duration}s not optimal (3-10s)")
    
    # Check for silence
    silence_ratio = detect_silence_ratio(audio_path)
    if silence_ratio > 0.3:
        raise ValueError(f"Too much silence: {silence_ratio:.1%}")
    
    # Check for multiple speakers
    speaker_count = detect_speaker_count(audio_path)
    if speaker_count > 1:
        raise ValueError(f"Multiple speakers detected: {speaker_count}")
    
    return True
```

### Quality Metrics

```python
# Compare original vs cloned voice
from resemblyzer import VoiceEncoder

encoder = VoiceEncoder()

original_embedding = encoder.embed_utterance(original_audio)
cloned_embedding = encoder.embed_utterance(cloned_audio)

# Cosine similarity (0-1, higher is better)
similarity = cosine_similarity(original_embedding, cloned_embedding)

if similarity > 0.9:
    print("✅ Excellent voice match")
elif similarity > 0.8:
    print("✅ Good voice match")
else:
    print("⚠️ Voice quality may be low")
```

## Troubleshooting

### Common Issues

#### 1. "CosyVoice2 model not available"

**Cause**: Model not downloaded or wrong path

**Fix**:
```bash
# Verify model exists
ls -la backend/data/models/cosyvoice2/

# Download if missing
git clone https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B backend/data/models/cosyvoice2
```

#### 2. "CUDA out of memory"

**Cause**: GPU memory insufficient

**Fix**:
```python
# Use CPU instead
cosyvoice2 = CosyVoice2Service(device="cpu")

# Or reduce batch size
cosyvoice2.batch_size = 1

# Or use smaller model
cosyvoice2 = CosyVoice2Service(model_path="data/models/cosyvoice2-tiny")
```

#### 3. "Voice sample extraction failed"

**Cause**: Invalid audio or wrong offset

**Fix**:
```python
# Try different offset
voice_sample = extract_voice_sample(
    audio_path=audio_path,
    offset=10.0,  # Skip more of intro
    duration=5.0
)

# Or use auto-detect clean segment
voice_sample = extract_voice_sample_auto(
    audio_path=audio_path,
    min_duration=5.0,
    max_duration=10.0
)
```

#### 4. "Cloned voice sounds robotic"

**Cause**: Poor sample quality or too short

**Fix**:
- Use longer sample (7-10s instead of 3-5s)
- Choose segment with clear, natural speech
- Avoid overlapping music/sound effects
- Ensure sample rate is 22050 Hz

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('cosyvoice').setLevel(logging.DEBUG)

# Run with debug output
cosyvoice2 = CosyVoice2Service()
cosyvoice2.clone_voice(
    reference_audio="sample.wav",
    target_text="Test",
    language="hi"
)
```

## Testing

### Unit Tests

```python
# tests/test_cosyvoice2.py

def test_voice_sample_extraction():
    """Test extracting voice sample"""
    service = get_cosyvoice2_service()
    sample = service.extract_voice_sample(
        audio_path="test_audio.wav",
        duration=5.0
    )
    assert os.path.exists(sample)
    assert get_audio_duration(sample) >= 4.5  # Allow small variance

def test_voice_cloning():
    """Test zero-shot voice cloning"""
    service = get_cosyvoice2_service()
    if not service.available:
        pytest.skip("CosyVoice2 not available")
    
    output = service.clone_voice(
        reference_audio="test_sample.wav",
        target_text="Hello world",
        language="en"
    )
    assert os.path.exists(output)
    assert os.path.getsize(output) > 1000
```

### Integration Tests

```bash
# Test full pipeline with voice cloning
pytest tests/test_integration.py::test_voice_cloning_pipeline -v
```

## Production Deployment

### Docker Setup

```dockerfile
# Dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install dependencies
RUN pip install cosyvoice torch torchaudio

# Copy model
COPY data/models/cosyvoice2 /app/models/cosyvoice2

# Environment
ENV MODEL_DIR=/app/models
ENV CUDA_VISIBLE_DEVICES=0

# Start service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sanskriti-flow-voice-cloning
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: worker
        image: sanskriti-flow:latest
        resources:
          limits:
            nvidia.com/gpu: 1  # Request 1 GPU
            memory: 16Gi
        env:
        - name: ENABLE_VOICE_CLONING
          value: "true"
        - name: MODEL_DIR
          value: "/models"
        volumeMounts:
        - name: models
          mountPath: /models
```

### Monitoring

```python
# Track voice cloning metrics
from prometheus_client import Counter, Histogram

voice_cloning_requests = Counter(
    'voice_cloning_requests_total',
    'Total voice cloning requests'
)

voice_cloning_duration = Histogram(
    'voice_cloning_duration_seconds',
    'Voice cloning processing time'
)

@voice_cloning_duration.time()
def clone_voice_with_metrics(*args, **kwargs):
    voice_cloning_requests.inc()
    return cosyvoice2.clone_voice(*args, **kwargs)
```

## Best Practices

### 1. Sample Selection
- Extract from middle of video (skip intro/outro)
- Use 7-10 seconds for best quality
- Ensure single speaker, clear speech
- Avoid background noise/music

### 2. Error Handling
- Always implement fallback to standard TTS
- Log voice cloning failures for monitoring
- Validate sample quality before processing
- Check GPU availability before starting

### 3. Performance
- Use GPU for production (10x faster)
- Batch process segments when possible
- Cache speaker embeddings for same speaker
- Monitor memory usage (4-8GB VRAM typical)

### 4. Quality
- Validate voice similarity >0.8
- Monitor user feedback on cloned audio
- A/B test cloned vs standard TTS
- Provide quality toggle in UI

## Future Enhancements

### Roadmap

1. **Real-Time Cloning** (Q2 2026)
   - Live streaming voice cloning
   - <100ms latency

2. **Multi-Speaker** (Q3 2026)
   - Clone multiple speakers in one video
   - Automatic speaker diarization

3. **Emotion Control** (Q4 2026)
   - Adjust emotion/tone independently
   - Happy, sad, excited variations

4. **Voice Morphing** (Q1 2027)
   - Blend multiple voices
   - Age/gender adjustments

## Support

### Resources

- **Documentation**: https://cosyvoice.readthedocs.io
- **GitHub**: https://github.com/FunAudioLLM/CosyVoice
- **Papers**: https://arxiv.org/abs/2409.xxxxx
- **Discord**: https://discord.gg/funaudiollm

### Issues

Report bugs: https://github.com/Puneet04-tech/sanskriti-flow/issues

Include:
- Voice sample (if possible)
- Error logs
- System specs (GPU, RAM)
- CosyVoice2 version

---

**Last Updated**: March 3, 2026  
**CosyVoice2 Version**: 2.0.5  
**Status**: Production Ready ✅
