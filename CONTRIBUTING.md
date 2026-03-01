# Contributing to Sanskriti-Flow

Thank you for your interest in contributing to Sanskriti-Flow! This project is part of FOSS Hack 2026 and we welcome contributions from the community.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the FOSS principles

## How to Contribute

### 1. Fork the Repository
```bash
git clone https://github.com/yourusername/sanskriti-flow.git
cd sanskriti-flow
```

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

Follow the coding standards:
- **Python**: PEP 8, type hints, docstrings
- **TypeScript**: ESLint rules, proper typing
- **Commits**: Conventional commits format

### 4. Test Your Changes

**Backend:**
```bash
cd backend
pytest tests/
```

**Frontend:**
```bash
cd frontend
npm test
```

### 5. Submit a Pull Request

- Clear description of changes
- Reference any related issues
- Include screenshots for UI changes
- Ensure all tests pass

## Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Redis
- FFmpeg
- CUDA (optional, for GPU)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Worker Setup
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## Areas for Contribution

### High Priority
- [ ] Implement actual voice cloning (CosyVoice2/Coqui TTS)
- [ ] Implement lip-sync (Wav2Lip/LatentSync)
- [ ] Add model download automation
- [ ] Improve quiz question quality
- [ ] Add more language support

### Medium Priority
- [ ] Job progress tracking UI
- [ ] Video preview player
- [ ] Batch processing support
- [ ] Export formats (SRT subtitles, PDF quiz)
- [ ] Performance benchmarks

### Low Priority
- [ ] Dark mode UI
- [ ] Mobile responsive improvements
- [ ] API documentation
- [ ] Tutorial videos
- [ ] Internationalization (i18n)

## Code Style

### Python
```python
def process_video(video_path: str, language: str) -> Dict[str, Any]:
    """
    Process video with localization.
    
    Args:
        video_path: Path to video file
        language: Target language code
    
    Returns:
        Dictionary with processing results
    """
    # Implementation
    pass
```

### TypeScript
```typescript
interface LocalizationOptions {
  videoUrl: string;
  targetLanguage: string;
  enableQuiz: boolean;
}

const processVideo = async (options: LocalizationOptions): Promise<string> => {
  // Implementation
};
```

## Testing

### Unit Tests (Python)
```python
import pytest
from app.services.translation import TranslationService

def test_translation():
    service = TranslationService()
    result = service.translate("Hello", "hi")
    assert len(result) > 0
```

### Integration Tests
```python
def test_full_pipeline():
    # Test complete video processing
    pass
```

## Documentation

- Update README.md for new features
- Add docstrings to all functions
- Update ARCHITECTURE.md for system changes
- Create examples for new APIs

## License

By contributing, you agree that your contributions will be licensed under GPL-3.0.

## Questions?

- Open an issue on GitHub
- Join our community chat (link TBD)
- Email: contribute@sanskriti-flow.dev (TBD)

## Recognition

All contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in project documentation

Thank you for making education accessible! 🎓
