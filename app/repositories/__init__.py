"""Repository pattern — data access layer.

Tách biệt query SQLAlchemy ra khỏi service / router, giống
`IRepository<T>` trong .NET hoặc Repository<T> trong NestJS/TypeORM.
"""

from app.repositories.base import BaseRepository
from app.repositories.truck_repository import TruckRepository

__all__ = ["BaseRepository", "TruckRepository"]