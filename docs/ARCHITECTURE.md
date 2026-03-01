# System Architecture

## Overview

Sanskriti-Flow is built using a microservices architecture with three main components:

1. **Backend (FastAPI)**: REST API for job management
2. **Worker (Celery)**: Asynchronous processing pipeline
3. **Frontend (Next.js)**: User interface and dashboard

## High-Level Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Next.js       │
│   Frontend      │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐      ┌─────────────┐
│   FastAPI       │◄────►│   Redis     │
│   Backend       │      │   (Queue)   │
└────────┬────────┘      └─────────────┘
         │
         │ Celery Tasks
         ▼
┌─────────────────────────────────────┐
│         Celery Worker               │
│  ┌───────────────────────────────┐ │
│  │  1. Audio Extraction          │ │
│  │  2. Transcription (Whisper)   │ │
│  │  3. Translation (NLLB-200)    │ │
│  │  4. Quiz Generation (Llama)   │ │
│  │  5. Vision-Sync (VLM)         │ │
│  │  6. Voice Cloning             │ │
│  │  7. Lip-Sync                  │ │
│  │  8. Final Assembly            │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Processing Pipeline

### Stage 1: Audio Extraction
- **Tool**: FFmpeg
- **Input**: Video file
- **Output**: WAV audio (16kHz, mono)
- **Duration**: ~5 seconds per minute of video

### Stage 2: Transcription
- **Tool**: Faster-Whisper
- **Input**: Audio file
- **Output**: Transcript with timestamps
- **Features**: 
  - Language detection
  - Voice Activity Detection (VAD)
  - Segment-level timestamps
- **Duration**: ~10-20 seconds per minute of audio (GPU)

### Stage 3: Translation
- **Tool**: NLLB-200 + Neural Hinglish Engine
- **Input**: Transcript segments
- **Output**: Translated segments
- **Features**:
  - Technical term preservation
  - Multi-language support (200+)
  - Context-aware translation
- **Duration**: ~5 seconds per minute of transcript

### Stage 4: Quiz Generation
- **Tool**: Llama 3.1 (LangChain)
- **Input**: Transcript chunks
- **Output**: MCQ questions with timestamps
- **Features**:
  - Context-based question generation
  - Multiple difficulty levels
  - Answer explanations
- **Duration**: ~10 seconds per question

### Stage 5: Vision-Sync Overlays
- **Tool**: Moondream2 VLM + OpenCV
- **Input**: Video frames + translations
- **Output**: Video with translated overlays
- **Features**:
  - Text detection
  - Diagram analysis
  - Overlay positioning
- **Duration**: ~30 seconds per minute of video

### Stage 6: Voice Cloning (Planned)
- **Tool**: CosyVoice2
- **Input**: Reference audio + translated text
- **Output**: Cloned voice audio
- **Features**:
  - Zero-shot cloning
  - Emotion preservation
  - Multilingual TTS

### Stage 7: Lip-Sync (Planned)
- **Tool**: LatentSync
- **Input**: Video + new audio
- **Output**: Lip-synced video
- **Features**:
  - Diffusion-based rendering
  - Face tracking
  - Quality preservation

### Stage 8: Final Assembly
- **Tool**: FFmpeg
- **Input**: All processed components
- **Output**: Final localized video
- **Features**:
  - Audio/video merging
  - Overlay compositing
  - Format conversion

## Data Flow

```
Video URL
    ↓
[Download] → video.mp4
    ↓
[Extract Audio] → audio.wav
    ↓
[Transcribe] → segments.json
    ↓
[Translate] → translated_segments.json
    ↓
[Generate Quizzes] → quizzes.json
    ↓
[Vision Analysis] → frame_labels.json
    ↓
[Apply Overlays] → video_with_overlays.mp4
    ↓
[Voice Clone] → cloned_audio.wav
    ↓
[Lip-Sync] → final_synced.mp4
    ↓
Output Video
```

## Tech Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Task Queue**: Celery 5.3+
- **Data Store**: Redis 5.0+
- **Video Processing**: FFmpeg

### AI/ML Models
- **Transcription**: Faster-Whisper (OpenAI Whisper)
- **Translation**: NLLB-200 (Meta)
- **NER**: spaCy English (en_core_web_sm)
- **VLM**: Moondream2 (vikhyatk)
- **LLM**: Llama 3.1 8B Instruct
- **Vision**: YOLOv11, OpenCV

### Frontend
- **Framework**: Next.js 15
- **Styling**: Tailwind CSS 3.4+
- **Language**: TypeScript 5+
- **HTTP Client**: Axios

## Scalability

### Horizontal Scaling
- Multiple Celery workers can be spawned
- Redis handles task distribution
- Stateless API design allows multiple backend instances

### Vertical Scaling
- GPU acceleration for AI models
- Multi-threading for video processing
- Batch processing for translations

### Performance Optimizations
- Frame sampling for vision analysis (every 5th frame)
- Caching of model outputs
- Lazy loading of AI models
- Streaming responses for long videos

## Security

- Input validation on all endpoints
- File size limits (500MB default)
- Rate limiting (planned)
- CORS configuration
- No credential storage in logs

## Monitoring

- Celery Flower (web-based monitoring)
- FastAPI built-in /docs endpoint
- Health check endpoints
- Structured logging

## Future Enhancements

1. **Real-time streaming**: Sub-10s latency for live webinars
2. **Multi-speaker diarization**: Unique voices for each speaker
3. **Mobile app**: Android/iOS native apps
4. **Cloud deployment**: AWS/GCP integration
5. **Collaborative features**: Shared notes, discussions
