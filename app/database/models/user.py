# app/database/models/user.py

from enum import Enum as PyEnum
import uuid
from sqlalchemy import String, Text, SMALLINT, Integer, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database.models.base import Base

class Gender(PyEnum):
    man = "man"
    woman = "woman"

class LookingFor(PyEnum):
    man = "man"
    woman = "woman"

class User(Base):
    __tablename__ = "users"

    pk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    max_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)  # BigInteger можно оставить, если БД PostgreSQL
    photo_id: Mapped[str | None] = mapped_column(String, nullable=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    gender: Mapped[Gender | None] = mapped_column(
        SQLEnum(Gender, name="gender_enum"),
        nullable=True,
    )
    looking_for: Mapped[LookingFor | None] = mapped_column(
        SQLEnum(LookingFor, name="looking_for_enum"),
        nullable=True,
    )
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    age: Mapped[int | None] = mapped_column(SMALLINT, nullable=True)
    about: Mapped[str | None] = mapped_column(Text, nullable=True)
    link: Mapped[str | None] = mapped_column(String, nullable=True)
    dislike: Mapped[int | None] = mapped_column(Integer, default=0, nullable=False)
    matches_count: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    payment_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    tariff_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Связь 1:M — один юзер, много заказов. Используем строковую ссылку, чтобы разорвать цикл
    payments: Mapped[list["PaymentOrder"]] = relationship(
        "PaymentOrder",
        back_populates="user",
        lazy="selectin",
    )
