# Project Structure

```
sanskriti-flow/
│
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API Routes
│   │   │   └── v1/
│   │   │       ├── endpoints/ # Endpoint implementations
│   │   │       │   ├── localize.py
│   │   │       │   └── jobs.py
│   │   │       └── router.py
│   │   │
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py
│   │   │   └── logger.py
│   │   │
│   │   ├── models/            # Data models
│   │   │   └── schemas.py
│   │   │
│   │   ├── services/          # AI/ML Services
│   │   │   ├── transcription.py      # Faster-Whisper
│   │   │   ├── translation.py        # NLLB-200
│   │   │   ├── hinglish_engine.py    # NER-based preservation
│   │   │   ├── quiz_generator.py     # Llama 3.1
│   │   │   ├── vision_sync.py        # Moondream2 VLM
│   │   │   ├── voice_clone.py        # TTS (placeholder)
│   │   │   └── lip_sync.py           # Lip-sync (placeholder)
│   │   │
│   │   ├── utils/             # Utilities
│   │   │   └── video_utils.py        # FFmpeg operations
│   │   │
│   │   └── workers/           # Celery Workers
│   │       ├── celery_app.py
│   │       └── tasks.py              # Processing pipeline
│   │
│   ├── main.py                # FastAPI app entry
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment template
│
├── frontend/                  # Next.js 15 Frontend
│   ├── app/
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── next.config.js
│
├── docs/                      # Documentation
│   ├── SETUP.md              # Setup guide
│   ├── ARCHITECTURE.md       # System architecture
│   ├── API.md                # API documentation
│   └── PROJECT_STRUCTURE.md  # This file
│
├── scripts/                   # Automation scripts
│   ├── setup.sh              # Linux/Mac setup
│   └── setup.bat             # Windows setup
│
├── README.md                 # Main documentation
├── LICENSE                   # GPL-3.0
├── CONTRIBUTING.md           # Contribution guide
├── HACKATHON_SUMMARY.md      # FOSS Hack 2026 submission
└── .gitignore                # Git ignore rules

```

## File Count by Category

### Backend (Python)
- **Core**: 3 files (config, logger, main)
- **API**: 4 files (routes, endpoints)
- **Models**: 1 file (schemas)
- **Services**: 8 files (AI/ML implementations)
- **Workers**: 2 files (Celery tasks)
- **Utils**: 1 file (video processing)
- **Total**: ~19 Python files

### Frontend (TypeScript/React)
- **Pages**: 2 files (layout, home)
- **Config**: 4 files (next, tailwind, ts, postcss)
- **Total**: ~6 TypeScript/config files

### Documentation
- **Guides**: 4 markdown files
- **README**: 2 files (main + frontend)
- **Contributing**: 1 file
- **Total**: 7 documentation files

### Infrastructure
- **Scripts**: 2 files (setup scripts)
- **Config**: 3 files (.env examples, gitignore)
- **Total**: 5 infrastructure files

### Grand Total
**~35 source files** (excluding dependencies, models, and generated files)

## Technology Breakdown

### Languages
- Python: ~2,500 lines
- TypeScript/TSX: ~400 lines
- Markdown: ~2,000 lines
- YAML/JSON: ~200 lines
- Shell: ~100 lines

### Frameworks/Libraries
- **Backend**: FastAPI, Celery, Redis
- **AI/ML**: Transformers, Faster-Whisper, LangChain, spaCy
- **Video**: FFmpeg, OpenCV, Pillow
- **Frontend**: Next.js 15, React 18, Tailwind CSS

### External Models (not included in repo)
- Faster-Whisper (base: ~140MB)
- NLLB-200 (600M: ~2.4GB)
- Llama 3.1 8B (8B: ~4.3GB)
- Moondream2 (~3GB)
- spaCy en_core_web_sm (~13MB)

## Repository Size (without models)
- **Source Code**: ~5 MB
- **Dependencies** (after install):
  - Python packages: ~2 GB
  - Node modules: ~500 MB
- **Models** (separate download): ~10 GB

## Git Statistics
- **Commits**: 6
- **Branches**: 1 (master)
- **Contributors**: 1
- **License**: GPL-3.0

## Development Timeline

1. **Initial Setup** (Commit 1)
   - GPL-3.0 license
   - README and .gitignore
   - Project structure

2. **Backend Infrastructure** (Commit 2)
   - FastAPI setup
   - API endpoints
   - Configuration management

3. **AI/ML Services** (Commit 3)
   - Transcription service
   - Translation service
   - Hinglish engine
   - Quiz generator

4. **Vision & Workers** (Commit 4)
   - Vision-sync service
   - Video utilities
   - Celery pipeline

5. **Frontend** (Commit 5)
   - Next.js app
   - UI components
   - API integration

6. **Documentation & Docker** (Commit 6)
   - Complete documentation
   - Docker setup
   - Setup scripts
