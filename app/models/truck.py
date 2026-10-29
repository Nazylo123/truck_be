"""Truck (xe tải) model — bảng chính của showroom."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Truck(Base):
    """Một mẫu xe tải trong showroom."""

    __tablename__ = "trucks"

    # --- PK ---
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    # --- Thông tin cơ bản ---
    brand: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    year: Mapped[int] = mapped_column(nullable=False)

    payload_kg: Mapped[int] = mapped_column(
        Numeric(10, 0), nullable=False, comment="Tải trọng (kg)"
    )
    price_vnd: Mapped[Decimal] = mapped_column(
        Numeric(16, 0), nullable=False, comment="Giá bán (VND)"
    )

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # --- Flags ---
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    # --- Embedding cho RAG search ---
    # 384 = chiều phổ biến cho all-MiniLM-L6-v2; đổi nếu dùng model khác.
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(384), nullable=True
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Truck {self.brand} {self.model} ({self.year})>"