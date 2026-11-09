from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from exchange.api.schemas import (
    CreateDealSchema,
    NbrbRateSchema,
    ResponseCreateDealSchema,
    ResponseStatSchema,
    StatSchema,
)


def test_currency() -> None:
    deal = CreateDealSchema(
        amount_source=Decimal("100"),
        currency_source="usd",
        currency_target="eur",
    )

    assert deal.currency_source == "USD"
    assert deal.currency_target == "EUR"


@pytest.mark.parametrize(
    ("amount", "source", "target"),
    [
        ("100", "USD", "USD"),
        ("100", "ZZZ", "EUR"),
        ("0", "USD", "EUR"),
    ],
)
def test_bad_deal(amount: str, source: str, target: str) -> None:
    with pytest.raises(ValidationError):
        CreateDealSchema(
            amount_source=Decimal(amount),
            currency_source=source,
            currency_target=target,
        )


def test_stat_date() -> None:
    period = StatSchema(start_date="01.01.2026", end_date="01.01.2026", currency="usd")

    assert period.start_date == datetime(2026, 1, 1, tzinfo=ZoneInfo("Europe/Minsk"))
    assert period.currency == "USD"


@pytest.mark.parametrize(
    ("start", "end"),
    [
        ("02.01.2026", "01.01.2026"),
        ("2026-01-01", "02.01.2026"),
    ],
)
def test_bad_date(start: str, end: str) -> None:
    with pytest.raises(ValidationError):
        StatSchema(start_date=start, end_date=end)


def test_nbrb() -> None:
    rate = NbrbRateSchema.model_validate(
        {
            "Cur_ID": 431,
            "Cur_Code": "840",
            "Date": "2026-11-08T00:00:00",
            "Cur_Abbreviation": "USD",
            "Cur_Scale": 1,
            "Cur_Name": "US Dollar",
            "Cur_OfficialRate": "2.9915",
        }
    )

    assert rate.abbreviation == "USD"
    assert rate.official_rate == Decimal("2.9915")
    assert rate.scale == 1


def test_money() -> None:
    row = ResponseStatSchema(
        currency="USD",
        total_in=Decimal("1.00E+6"),
        total_out=Decimal("0"),
        deals_count=1,
    )
    data = row.model_dump(mode="json")

    assert data["total_in"] == "1000000.00"
    assert data["total_out"] == "0.00"

    deal = ResponseCreateDealSchema(
        id=1,
        amount_target=Decimal("1.00E+6"),
        rate=Decimal("8.18804E+1"),
    )
    body = deal.model_dump(mode="json")
    assert body["amount_target"] == "1000000.00"
    assert body["rate"] == "81.8804"
