"""Base Repository generic cho mọi ORM model.

Làm mỏng nhất có thể — chỉ CRUD thuần, không business logic.
Subclass thêm method đặc thù (vd. `TruckRepository.search_by_embedding`).
"""

from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic CRUD repository.

    Tương đương `IRepository<TEntity>` trong .NET hoặc `Repository<T>` trong NestJS.
    """

    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    # --- Read ---
    def get(self, id: uuid.UUID) -> ModelT | None:
        return self.db.get(self.model, id)

    def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        only_active: bool = False,
    ) -> list[ModelT]:
        q = self.db.query(self.model)
        if only_active and hasattr(self.model, "is_active"):
            q = q.filter(self.model.is_active.is_(True))  # type: ignore[attr-defined]
        return q.offset(skip).limit(limit).all()

    def count(self, *, only_active: bool = False) -> int:
        q = self.db.query(self.model)
        if only_active and hasattr(self.model, "is_active"):
            q = q.filter(self.model.is_active.is_(True))  # type: ignore[attr-defined]
        return q.count()

    # --- Write ---
    def add(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.flush()  # flush để có PK, nhưng chưa commit
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.flush()