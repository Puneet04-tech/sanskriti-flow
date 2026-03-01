"""
API v1 Router
Main router for API v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import localize, jobs

api_router = APIRouter()

api_router.include_router(localize.router, prefix="/localize", tags=["Localization"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
