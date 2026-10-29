"""Truck router — thin controller, chỉ HTTP I/O.

Mọi logic nghiệp vụ đã nằm ở `TruckService`. Router chỉ:
  1. Parse query/path/body bằng Pydantic (FastAPI tự làm).
  2. Gọi service.
  3. Map domain exception → HTTPException.
  4. Trả response schema.

Tương đương `TrucksController` trong .NET hoặc `TrucksController` trong NestJS.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import TruckCreate, TruckRead, TruckUpdate
from app.services.truck_service import (
    TruckConflictError,
    TruckNotFoundError,
    TruckService,
)

router = APIRouter(prefix="/trucks", tags=["trucks"])


# --- DI factories ---
def get_truck_service(db: Annotated[Session, Depends(get_db)]) -> TruckService:
    """Tạo TruckService mới mỗi request, dùng chung Session trong request đó."""
    return TruckService(db)


# --- Endpoints ---
@router.get(
    "",
    response_model=list[TruckRead],
    summary="List trucks (phân trang + lọc)",
)
def list_trucks(
    service: Annotated[TruckService, Depends(get_truck_service)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    only_active: bool = Query(False),
) -> list[TruckRead]:
    trucks = service.list(skip=skip, limit=limit, only_active=only_active)
    return [TruckRead.model_validate(t) for t in trucks]


@router.get(
    "/search",
    response_model=list[TruckRead],
    summary="Full-text search (sẽ thay bằng vector search sau)",
)
def search_trucks(
    service: Annotated[TruckService, Depends(get_truck_service)],
    q: str = Query(..., min_length=1, max_length=128),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[TruckRead]:
    trucks = service.search(q, skip=skip, limit=limit)
    return [TruckRead.model_validate(t) for t in trucks]


@router.post(
    "",
    response_model=TruckRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo truck mới",
)
def create_truck(
    payload: TruckCreate,
    service: Annotated[TruckService, Depends(get_truck_service)],
) -> TruckRead:
    try:
        truck = service.create(payload)
    except TruckConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        ) from e
    return TruckRead.model_validate(truck)


@router.get(
    "/{truck_id}",
    response_model=TruckRead,
    summary="Lấy chi tiết 1 truck",
)
def get_truck(
    truck_id: uuid.UUID,
    service: Annotated[TruckService, Depends(get_truck_service)],
) -> TruckRead:
    try:
        truck = service.get(truck_id)
    except TruckNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found"
        ) from e
    return TruckRead.model_validate(truck)


@router.patch(
    "/{truck_id}",
    response_model=TruckRead,
    summary="Cập nhật 1 phần (partial update)",
)
def update_truck(
    truck_id: uuid.UUID,
    patch: TruckUpdate,
    service: Annotated[TruckService, Depends(get_truck_service)],
) -> TruckRead:
    try:
        truck = service.update(truck_id, patch)
    except TruckNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found"
        ) from e
    except TruckConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        ) from e
    return TruckRead.model_validate(truck)


@router.delete(
    "/{truck_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Xoá truck (hard delete)",
)
def delete_truck(
    truck_id: uuid.UUID,
    service: Annotated[TruckService, Depends(get_truck_service)],
) -> Response:
    try:
        service.delete(truck_id)
    except TruckNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found"
        ) from e
    return Response(status_code=status.HTTP_204_NO_CONTENT)