from datetime import UTC, datetime
from decimal import Decimal

import pytest

from exchange.api.schemas import RateDTO
from exchange.models import Rate
from exchange.services import convert, get_rate_dto


def quote(code: str, official_rate: str, scale: int) -> RateDTO:
    return RateDTO(
        abbreviation=code,
        official_rate=Decimal(official_rate),
        scale=scale,
        rate_date=datetime(2026, 11, 8, tzinfo=UTC),
    )


@pytest.mark.parametrize(
    ("src_rate", "src_scale", "dst_rate", "dst_scale", "amount", "rate", "money"),
    [
        ("3.6535", 100, "1", 1, "100", "0.0365", "3.65"),
        ("1.23455", 1, "1", 1, "1", "1.2346", "1.23"),
        ("1", 1, "1", 1, "1.225", "1.0000", "1.23"),
        ("11.6480", 100000, "1", 1, "100000", "0.0001", "10.00"),
    ],
)
def test_convert(
    src_rate: str,
    src_scale: int,
    dst_rate: str,
    dst_scale: int,
    amount: str,
    rate: str,
    money: str,
) -> None:
    result_money, result_rate = convert(
        Decimal(amount),
        quote("SRC", src_rate, src_scale),
        quote("DST", dst_rate, dst_scale),
    )

    assert result_rate == Decimal(rate)
    assert result_money == Decimal(money)


def test_byn() -> None:
    row = Rate(
        cur_id=1,
        code="000",
        rate_date=datetime(2026, 11, 8),
        abbreviation="BYN",
        scale=100,
        name="Belarusian Ruble",
        official_rate=Decimal("9.9999"),
    )

    rate = get_rate_dto("BYN", {"BYN": row})

    assert rate.official_rate == Decimal("1")
    assert rate.scale == 1


def test_rate() -> None:
    row = Rate(
        cur_id=1,
        code="840",
        rate_date=datetime(2026, 11, 8),
        abbreviation="USD",
        scale=10,
        name="US Dollar",
        official_rate=Decimal("2.5"),
    )

    rate = get_rate_dto("USD", {"USD": row})

    assert rate.official_rate == Decimal("2.5")
    assert rate.scale == 10
