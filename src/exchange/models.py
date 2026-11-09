from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DealStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Base(DeclarativeBase):
    pass


class Rate(Base):
    __tablename__ = "rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cur_id: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(3), nullable=False)
    rate_date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(3), nullable=False)
    scale: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    official_rate: Mapped[Decimal] = mapped_column(Numeric[Decimal](18, 4), nullable=False)

    __table_args__ = (
        UniqueConstraint("abbreviation", "rate_date", name="uq_abbreviation_rate_date"),
    )


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount_source: Mapped[Decimal] = mapped_column(Numeric[Decimal], nullable=False)
    amount_target: Mapped[Decimal] = mapped_column(Numeric[Decimal], nullable=False)
    currency_source: Mapped[str] = mapped_column(String(3), nullable=False)
    currency_target: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric[Decimal], nullable=False)
    status: Mapped[DealStatus] = mapped_column(
        Enum(DealStatus, native_enum=False), nullable=False, default=DealStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    __table_args__ = (
        CheckConstraint(amount_target > 0, name="check_amount_target"),
        CheckConstraint(rate > 0, name="ck_rate"),
        CheckConstraint(
            "resolved_at IS NULL OR resolved_at >= created_at",
            name="chk_resolved_at_created_at",
        ),
    )
