"""API v1 router — gom tất cả endpoint version 1.

Tương đương `RouteGroup` trong NestJS hoặc area mapping trong .NET.
"""

from fastapi import APIRouter

from app.api.v1.trucks import router as trucks_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(trucks_router)

__all__ = ["api_router"]