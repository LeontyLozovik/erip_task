from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    Enum,
    Integer,
    Numeric,
    String,
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

    # __table_args__ = (
    #     UniqueConstraint("rate_date", "abbreviation", name="uq_rates_date_abbreviation"),
    #     CheckConstraint("nbrb_id > 0", name="ck_rates_nbrb_id_positive"),
    #     CheckConstraint("scale > 0", name="ck_rates_scale_positive"),
    #     CheckConstraint("official_rate > 0", name="ck_rates_official_rate_positive"),
    #     CheckConstraint("code ~ '^[0-9]{3}$'", name="ck_rates_code_digits"),
    #     CheckConstraint("abbreviation ~ '^[A-Z]{3}$'", name="ck_rates_abbreviation_alpha"),
    #     CheckConstraint("char_length(name) > 0", name="ck_rates_name_present"),
    # )


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount_source: Mapped[float] = mapped_column(Numeric[Decimal], nullable=False)
    amount_target: Mapped[float] = mapped_column(Numeric[Decimal], nullable=False)
    currency_source: Mapped[str] = mapped_column(String(3), nullable=False)
    currency_target: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric[Decimal], nullable=False)
    rate_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[DealStatus] = mapped_column(
        Enum(DealStatus, native_enum=False), nullable=False, default=DealStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    # __table_args__ = (
    #     CheckConstraint(amount_target > 0, name="check_amount_target"),
    #     CheckConstraint(rate > 0, name="ck_rate"),
    #     CheckConstraint(currency_source != currency_target, name="chk_currency_source_target"),
    #     CheckConstraint(status in DealStatus, name="chk_status"),
    #     CheckConstraint(created_at <= resolved_at, name="chk_created_at_resolved_at"),
    #     CheckConstraint(created_at <= rate_date, name="chk_created_at_rate_date"),
    #     CheckConstraint(resolved_at <= rate_date, name="chk_resolved_at_rate_date"),
    #     CheckConstraint(resolved_at <= created_at, name="chk_resolved_at_created_at"),
    #     CheckConstraint(resolved_at <= rate_date, name="chk_resolved_at_rate_date"),
    # )
