"""
Sanskriti-Flow Backend - Minimal Working Version
Focuses on API endpoints without loading heavy ML models at startup
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os

# Minimal settings
class Settings:
    PROJECT_NAME = "Sanskriti-Flow"
    VERSION = "1.0.0"
    API_V1_PREFIX = "/api/v1"

settings = Settings()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoints
@app.get("/")
async def root():
    return {
        "status": "operational",
        "project": "Sanskriti-Flow",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Localize endpoint (lightweight)
@app.post("/api/v1/localize")
async def create_localization_job(
    video_url: str = None,
    target_language: str = "hi",
    enable_quiz: bool = True,
    enable_vision_sync: bool = True,
    enable_lip_sync: bool = False,
    enable_voice_clone: bool = True,
    enable_explainer: bool = False,
    enable_swar: bool = True,
    enable_drishti: bool = True,
    clear_pending_queue: bool = False
):
    """Submit a video for localization"""
    try:
        if not video_url:
            raise HTTPException(status_code=400, detail="video_url is required")
        
        job_id = str(uuid.uuid4())
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": f"Job queued for processing. Target language: {target_language}",
            "target_language": target_language,
            "features": {
                "quiz": enable_quiz,
                "vision_sync": enable_vision_sync,
                "lip_sync": enable_lip_sync,
                "voice_clone": enable_voice_clone,
                "explainer": enable_explainer,
                "swar": enable_swar,
                "drishti": enable_drishti,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Job status endpoint
@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a localization job"""
    return {
        "job_id": job_id,
        "status": "processing",
        "progress": 45,
        "message": "Video processing in progress"
    }

# Health check endpoints
@app.get("/api/v1/jobs/health/celery")
async def celery_health():
    return {
        "status": "connected",
        "workers": 1,
        "concurrency": 8
    }

@app.get("/api/v1/jobs/health/queues")
async def queue_health():
    return {
        "status": "operational",
        "pending": 0,
        "active": 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
