"""TruckService — business logic cho resource `Truck`.

Quy ước:
  - Không nhận/biết về HTTP, FastAPI hay Pydantic Request → chỉ làm việc với
    domain model + DTO (schema). Mapping Pydantic → ORM diễn ra ở router.
  - Raise exception thuộc domain (vd. `TruckNotFoundError`) — router sẽ
    map sang HTTPException.
  - Có thể gọi nhiều repository hoặc service khác.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy.orm import Session

from app.models import Truck
from app.repositories import TruckRepository
from app.schemas import TruckCreate, TruckUpdate


# --- Domain exceptions (router sẽ map sang HTTP) ---
class TruckNotFoundError(LookupError):
    """Raised khi không tìm thấy Truck theo id."""


class TruckConflictError(ValueError):
    """Raised khi dữ liệu vi phạm business rule (vd. trùng brand/model/year)."""


class TruckService:
    """Service chứa business rules cho Truck.

    Tương đương `TruckService` trong .NET hoặc `TrucksService` trong NestJS.
    Một instance phục vụ một request (per-request scope qua Depends).
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = TruckRepository(db)

    # --- Queries ---
    def get(self, truck_id: uuid.UUID) -> Truck:
        truck = self.repo.get(truck_id)
        if truck is None:
            raise TruckNotFoundError(str(truck_id))
        return truck

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        only_active: bool = False,
    ) -> Sequence[Truck]:
        return self.repo.list(
            skip=skip, limit=limit, only_active=only_active
        )

    def count(self, *, only_active: bool = False) -> int:
        return self.repo.count(only_active=only_active)

    def search(self, q: str, *, skip: int = 0, limit: int = 20) -> Sequence[Truck]:
        return self.repo.search_fulltext(q, skip=skip, limit=limit)

    # --- Commands ---
    def create(self, payload: TruckCreate) -> Truck:
        # Business rule: không trùng (brand, model, year)
        if self.repo.exists_by_brand_model(
            payload.brand, payload.model, payload.year
        ):
            raise TruckConflictError(
                f"Đã có xe {payload.brand} {payload.model} {payload.year}"
            )

        truck = Truck(
            brand=payload.brand,
            model=payload.model,
            year=payload.year,
            payload_kg=payload.payload_kg,
            price_vnd=payload.price_vnd,
            description=payload.description,
            is_active=payload.is_active,
        )
        self.repo.add(truck)
        self.db.commit()
        self.db.refresh(truck)
        return truck

    def update(self, truck_id: uuid.UUID, patch: TruckUpdate) -> Truck:
        truck = self.get(truck_id)  # raises TruckNotFoundError nếu thiếu

        data = patch.model_dump(exclude_unset=True)  # chỉ field client gửi
        # Nếu đổi brand/model/year → check trùng
        if {"brand", "model", "year"} & data.keys() and self.repo.exists_by_brand_model(
            data.get("brand", truck.brand),
            data.get("model", truck.model),
            data.get("year", truck.year),
        ):
            raise TruckConflictError("Bản ghi trùng (brand, model, year)")

        for field, value in data.items():
            setattr(truck, field, value)
        self.db.commit()
        self.db.refresh(truck)
        return truck

    def delete(self, truck_id: uuid.UUID) -> None:
        truck = self.get(truck_id)
        self.repo.delete(truck)
        self.db.commit()