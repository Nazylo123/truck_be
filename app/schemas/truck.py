"""Pydantic schemas cho resource `Truck`.

Pattern CRUD chuẩn:
  - `TruckBase`   : fields chung
  - `TruckCreate` : payload client gửi lên khi tạo (POST)
  - `TruckUpdate` : payload patch (PATCH) — mọi field optional
  - `TruckRead`   : response trả về client (đã có id + timestamps)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TruckBase(BaseModel):
    """Fields chung của Truck (dùng làm base cho Create/Update/Read)."""

    brand: str = Field(..., min_length=1, max_length=64, examples=["Hino"])
    model: str = Field(..., min_length=1, max_length=128, examples=["XZU720L"])
    year: int = Field(..., ge=1950, le=2100, examples=[2024])
    payload_kg: int = Field(..., ge=0, le=10_000_000, examples=[3500])
    price_vnd: Decimal = Field(..., ge=0, examples=[Decimal("680000000")])
    description: Optional[str] = Field(default=None, examples=["Xe tải nhẹ thành phố, 3.5 tấn"])
    is_active: bool = Field(default=True)


class TruckCreate(TruckBase):
    """Payload cho `POST /trucks` — tạo mới."""


class TruckUpdate(BaseModel):
    """Payload cho `PATCH /trucks/{id}` — mọi field optional để partial update."""

    model_config = ConfigDict(extra="forbid")  # chặn field lạ

    brand: Optional[str] = Field(default=None, min_length=1, max_length=64)
    model: Optional[str] = Field(default=None, min_length=1, max_length=128)
    year: Optional[int] = Field(default=None, ge=1950, le=2100)
    payload_kg: Optional[int] = Field(default=None, ge=0, le=10_000_000)
    price_vnd: Optional[Decimal] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class TruckRead(TruckBase):
    """Response trả về client — có id + timestamps."""

    model_config = ConfigDict(from_attributes=True)  # cho phép dump từ ORM instance

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # `embedding` không trả về qua API mặc định (dài, cũng không cần thiết cho client).
    # Nếu cần, tạo schema `TruckReadWithEmbedding` riêng.