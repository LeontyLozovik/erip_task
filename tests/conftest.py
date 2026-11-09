from datetime import datetime
from decimal import Decimal

import pytest

from exchange.models import Rate

RATE_DATE = datetime(2026, 11, 8)


@pytest.fixture
def usd() -> Rate:
    return Rate(
        cur_id=1,
        code="840",
        rate_date=RATE_DATE,
        abbreviation="USD",
        scale=1,
        name="US Dollar",
        official_rate=Decimal("2"),
    )


@pytest.fixture
def eur() -> Rate:
    return Rate(
        cur_id=2,
        code="978",
        rate_date=RATE_DATE,
        abbreviation="EUR",
        scale=1,
        name="Euro",
        official_rate=Decimal("4"),
    )
