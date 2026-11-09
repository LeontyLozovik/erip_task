from datetime import date, datetime, time
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Self

import pycountry
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from exchange.models import DealStatus


class CreateDealSchema(BaseModel):
    amount_source: Annotated[
        Decimal, Field(gt=0, description="Amount of source currency", example=100)
    ]
    currency_source: Annotated[
        str,
        StringConstraints(min_length=3, max_length=3),
        Field(description="ISO 4217 currency code", example="USD"),
    ]
    currency_target: Annotated[
        str,
        StringConstraints(min_length=3, max_length=3),
        Field(description="ISO 4217 currency code", example="BYN"),
    ]

    @field_validator("currency_source", "currency_target")
    @classmethod
    def validate_iso_currency(cls, currency: str) -> str:
        currency_upper = currency.upper()
        if not pycountry.currencies.get(alpha_3=currency_upper):
            raise ValueError(f"Currency '{currency_upper}' not found in ISO 4217 or is invalid")
        return currency_upper

    @model_validator(mode="after")
    def check_different_currencies(self) -> Self:
        if self.currency_source == self.currency_target:
            raise ValueError("Source and target currencies cannot be the same")
        return self


class ResponseCreateDealSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount_target: Decimal
    rate: Decimal


class RateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    official_rate: Decimal
    scale: int
    currency: str = Field(validation_alias="abbreviation")
    rate_date: datetime


class NbrbRateSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cur_id: Annotated[int, Field(alias="Cur_ID", gt=0)]
    code: Annotated[str, Field(alias="Cur_Code", pattern=r"^[0-9]{3}$")]
    rate_date: Annotated[datetime, Field(alias="Date")]
    abbreviation: Annotated[str, Field(alias="Cur_Abbreviation", pattern=r"^[A-Z]{3}$")]
    scale: Annotated[int, Field(alias="Cur_Scale", gt=0)]
    name: Annotated[str, Field(alias="Cur_Name", min_length=1, max_length=128)]
    official_rate: Annotated[
        Decimal, Field(alias="Cur_OfficialRate", gt=0, max_digits=18, decimal_places=4)
    ]


class DealResolution(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"


class ResolveDealSchema(BaseModel):
    deal_id: Annotated[int, Field(gt=0, description="Deal id", example=1)]
    requested_status: Annotated[
        DealResolution,
        Field(
            description="Accept or reject deal",
            example="accept",
        ),
    ]


class ResponseResolveDealSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: DealStatus


class StatSchema(BaseModel):
    start_date: Annotated[
        datetime, Field(description="Start date", examples=["2026-01-01T00:00:00Z"])
    ]
    end_date: Annotated[datetime, Field(description="End date", examples=["2026-01-01T00:00:00Z"])]
    currency: Annotated[
        str | None,
        StringConstraints(min_length=3, max_length=3),
        Field(description="ISO 4217 currency code", example="USD"),
    ] = None

    @field_validator("currency")
    @classmethod
    def validate_iso_currency(cls, currency: str | None) -> str | None:
        if currency is None:
            return currency
        currency_upper = currency.upper()
        if not pycountry.currencies.get(alpha_3=currency_upper):
            raise ValueError(f"Currency '{currency_upper}' not found in ISO 4217 or is invalid")
        return currency_upper

    @field_validator("end_date", mode="before")
    @classmethod
    def set_end_of_day(cls, value: object) -> object:
        if isinstance(value, str):
            raw = value.strip()
            if "T" not in raw and " " not in raw and ":" not in raw:
                day = date.fromisoformat(raw)
                return datetime.combine(day, time.max)
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime.combine(value, time.max)
        return value

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date should be greater or equal then start_date")
        return self


class ResponseStatSchema(BaseModel):
    currency: str
    total_in: Decimal
    total_out: Decimal
    deals_count: int


class ResponsePendingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount_source: Decimal
    amount_target: Decimal
    currency_source: str
    currency_target: str
    rate: Decimal
