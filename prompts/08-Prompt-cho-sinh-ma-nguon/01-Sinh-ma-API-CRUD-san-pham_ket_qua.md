# API CRUD dịch vụ nha khoa

> Ví dụ hướng tới FastAPI, SQLAlchemy 2.x, Pydantic 2.x, SQLite. Tên module/import database session phụ thuộc cấu trúc dự án; mã dưới đây là các thành phần router/model/schema, không bao gồm xác thực middleware. `price` được lưu dưới dạng số nguyên đồng Việt Nam (VND), tránh số thực tiền tệ.

## 1. SQLAlchemy model

```python
# models/dental_service.py
from sqlalchemy import CheckConstraint, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DentalService(Base):
    __tablename__ = "dental_services"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_dental_service_price_nonnegative"),
        CheckConstraint("duration_minutes > 0", name="ck_dental_service_duration_positive"),
        CheckConstraint(
            "status IN ('active', 'inactive')",
            name="ck_dental_service_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="active")
```

## 2. Pydantic schemas

```python
# schemas/dental_service.py
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class DentalServiceCreate(BaseModel):
    service_code: NonEmpty
    name: NonEmpty
    category: str | None = None
    description: str | None = None
    price: int = Field(ge=0, description="Giá nguyên đồng Việt Nam (VND)")
    duration_minutes: int = Field(gt=0)
    status: Literal["active", "inactive"] = "active"


class DentalServiceUpdate(BaseModel):
    service_code: NonEmpty | None = None
    name: NonEmpty | None = None
    category: str | None = None
    description: str | None = None
    price: int | None = Field(default=None, ge=0)
    duration_minutes: int | None = Field(default=None, gt=0)
    status: Literal["active", "inactive"] | None = None


class DentalServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_code: str
    name: str
    category: str | None
    description: str | None
    price: int
    duration_minutes: int
    status: Literal["active", "inactive"]
```

## 3. FastAPI router

```python
# routers/dental_services.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dental_service import DentalService
from app.schemas.dental_service import (
    DentalServiceCreate,
    DentalServiceRead,
    DentalServiceUpdate,
)

router = APIRouter(prefix="/dental-services", tags=["dental-services"])
DbSession = Annotated[Session, Depends(get_db)]


def _find_or_404(db: Session, service_id: int) -> DentalService:
    service = db.get(DentalService, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy dịch vụ")
    return service


@router.post("", response_model=DentalServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(payload: DentalServiceCreate, db: DbSession) -> DentalService:
    service = DentalService(**payload.model_dump())
    db.add(service)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="service_code đã tồn tại hoặc dữ liệu vi phạm ràng buộc"
        ) from exc
    db.refresh(service)
    return service


@router.get("", response_model=list[DentalServiceRead])
def list_services(
    db: DbSession,
    search: str | None = Query(default=None, min_length=1),
    service_status: str | None = Query(default=None, alias="status", pattern="^(active|inactive)$"),
) -> list[DentalService]:
    stmt = select(DentalService).order_by(DentalService.name)
    if search:
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            DentalService.name.ilike(term) | DentalService.service_code.ilike(term)
        )
    if service_status:
        stmt = stmt.where(DentalService.status == service_status)
    return list(db.scalars(stmt).all())


@router.get("/{service_id}", response_model=DentalServiceRead)
def get_service(service_id: int, db: DbSession) -> DentalService:
    return _find_or_404(db, service_id)


@router.patch("/{service_id}", response_model=DentalServiceRead)
def update_service(
    service_id: int,
    payload: DentalServiceUpdate,
    db: DbSession,
) -> DentalService:
    service = _find_or_404(db, service_id)
    changes = payload.model_dump(exclude_unset=True)
    non_nullable = {
        "service_code", "name", "price", "duration_minutes", "status"
    }
    if any(changes.get(field) is None for field in non_nullable if field in changes):
        raise HTTPException(
            status_code=422,
            detail="Không được gán null cho trường bắt buộc",
        )
    for field, value in changes.items():
        setattr(service, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="service_code đã tồn tại hoặc dữ liệu vi phạm ràng buộc"
        ) from exc
    db.refresh(service)
    return service


@router.patch("/{service_id}/deactivate", response_model=DentalServiceRead)
def deactivate_service(service_id: int, db: DbSession) -> DentalService:
    service = _find_or_404(db, service_id)
    service.status = "inactive"
    db.commit()
    db.refresh(service)
    return service
```

## 4. Include router vào app chính

```python
# app/main.py
from fastapi import FastAPI
from app.routers.dental_services import router as dental_services_router

app = FastAPI()
app.include_router(dental_services_router, prefix="/api")
```

Trong ứng dụng thật cần bổ sung dependency xác thực/phân quyền cho từng endpoint, migration/schema creation theo quy trình dự án và test API. Không đưa hồ sơ bệnh nhân, sức khỏe hay dữ liệu thanh toán vào module danh mục dịch vụ; không xóa vật lý dịch vụ đã được tham chiếu.
