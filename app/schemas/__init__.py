"""Pydantic schemas (request/response DTOs)."""

from app.schemas.truck import (
    TruckBase,
    TruckCreate,
    TruckRead,
    TruckUpdate,
)

__all__ = ["TruckBase", "TruckCreate", "TruckRead", "TruckUpdate"]