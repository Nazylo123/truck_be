"""Healthcheck endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Liveness: app có phản hồi không."""
    return {"status": "ok"}


@router.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict:
    """Readiness: kết nối DB còn ok không (chạm pgvector/pg_trgm)."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "reachable"}