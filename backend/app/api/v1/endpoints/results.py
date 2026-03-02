"""
Results API Endpoints
Handles serving processed video files
"""

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.logger import logger
import os

router = APIRouter()


@router.get("/{filename}")
async def get_result_file(filename: str = Path(..., description="Result filename")):
    """
    Download a processed video file
    
    Returns the localized video file when processing is complete.
    """
    try:
        file_path = os.path.join(settings.OUTPUT_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Result file not found")
        
        logger.info(f"Serving result file: {filename}")
        
        return FileResponse(
            path=file_path,
            media_type="video/mp4",
            filename=filename,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving result file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
