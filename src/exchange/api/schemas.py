from datetime import datetime
from decimal import Decimal
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

    rate: Decimal
    rate_date: datetime


class NbrbRateSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cur_id: Annotated[int, Field(alias="Cur_ID")]
    code: Annotated[str, Field(alias="Cur_Code")]
    rate_date: Annotated[datetime, Field(alias="Date")]
    abbreviation: Annotated[str, Field(alias="Cur_Abbreviation")]
    scale: Annotated[int, Field(alias="Cur_Scale", gt=0)]
    name: Annotated[str, Field(alias="Cur_Name", max_length=128)]
    official_rate: Annotated[Decimal, Field(alias="Cur_OfficialRate", gt=0)]


class ResolveDealSchema(BaseModel):
    deal_id: int
    requested_status: DealStatus


class ResponseResolveDealSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: DealStatus


class StatSchema(BaseModel):
    date_start: datetime
    date_end: datetime
    total_deals: int
    total_amount_source: float
    total_amount_target: float
    total_rate: float
