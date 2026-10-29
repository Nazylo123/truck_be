"""TruckRepository — các query đặc thù cho Truck.

Kế thừa `BaseRepository[Truck]`, thêm method phục vụ nghiệp vụ showroom.
"""

from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Truck
from app.repositories.base import BaseRepository


class TruckRepository(BaseRepository[Truck]):
    """Truck-specific data access.

    Tương đương `ITruckRepository` + `TruckRepository` trong .NET.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.model = Truck  # gán cho generic

    def find_by_brand_model(
        self,
        brand: str | None = None,
        model: str | None = None,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Truck]:
        """Tìm theo brand/model (case-insensitive partial match)."""
        stmt = select(Truck)
        if brand:
            stmt = stmt.where(Truck.brand.ilike(f"%{brand}%"))
        if model:
            stmt = stmt.where(Truck.model.ilike(f"%{model}%"))
        stmt = stmt.order_by(Truck.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def exists_by_brand_model(
        self, brand: str, model: str, year: int
    ) -> bool:
        """Check trùng (brand, model, year) — dùng cho validation trước insert."""
        stmt = select(Truck.id).where(
            Truck.brand == brand,
            Truck.model == model,
            Truck.year == year,
        )
        return self.db.execute(stmt).first() is not None

    def search_fulltext(
        self,
        q: str,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Truck]:
        """Full-text đơn giản: match trên brand/model/description.

        Sau này thay bằng vector search (pgvector) khi có embedding.
        """
        pattern = f"%{q}%"
        stmt = (
            select(Truck)
            .where(
                or_(
                    Truck.brand.ilike(pattern),
                    Truck.model.ilike(pattern),
                    Truck.description.ilike(pattern),
                )
            )
            .order_by(Truck.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())