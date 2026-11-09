import asyncio
from decimal import Decimal

import pytest
from fastapi import HTTPException

from exchange.api.deals import create_deal, pending_deals, resolve_deal, stat
from exchange.api.schemas import CreateDealSchema, ResolveDealSchema, StatSchema
from exchange.models import Deal, DealStatus, Rate


async def save_deal(
    data: CreateDealSchema,
    calculated_rate: Decimal,
    amount_target: Decimal,
    session: object,
) -> Deal:
    return Deal(
        id=1,
        amount_source=data.amount_source,
        amount_target=amount_target,
        currency_source=data.currency_source,
        currency_target=data.currency_target,
        rate=calculated_rate,
    )


def test_create(monkeypatch: pytest.MonkeyPatch, usd: Rate, eur: Rate) -> None:
    async def rates(currency_source: str, currency_target: str, session: object) -> dict[str, Rate]:
        return {"USD": usd, "EUR": eur}

    monkeypatch.setattr("exchange.api.deals.get_needed_rates", rates)
    monkeypatch.setattr("exchange.api.deals.save_deal", save_deal)

    result = asyncio.run(
        create_deal(
            CreateDealSchema(
                amount_source=Decimal("10"),
                currency_source="USD",
                currency_target="EUR",
            ),
            None,
        )
    )

    assert result.rate == Decimal("0.5000")
    assert result.amount_target == Decimal("5.00")


def test_create_byn(monkeypatch: pytest.MonkeyPatch, usd: Rate) -> None:
    async def rates(currency_source: str, currency_target: str, session: object) -> dict[str, Rate]:
        return {"USD": usd}

    monkeypatch.setattr("exchange.api.deals.get_needed_rates", rates)
    monkeypatch.setattr("exchange.api.deals.save_deal", save_deal)

    result = asyncio.run(
        create_deal(
            CreateDealSchema(
                amount_source=Decimal("10"),
                currency_source="BYN",
                currency_target="USD",
            ),
            None,
        )
    )

    assert result.rate == Decimal("0.5000")
    assert result.amount_target == Decimal("5.00")


def test_no_rate(monkeypatch: pytest.MonkeyPatch) -> None:
    async def rates(currency_source: str, currency_target: str, session: object) -> dict[str, Rate]:
        raise HTTPException(status_code=404, detail="No rate")

    monkeypatch.setattr("exchange.api.deals.get_needed_rates", rates)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            create_deal(
                CreateDealSchema(
                    amount_source=Decimal("10"),
                    currency_source="USD",
                    currency_target="EUR",
                ),
                None,
            )
        )

    assert error.value.status_code == 404


def test_resolve(monkeypatch: pytest.MonkeyPatch) -> None:
    async def change_status(data: ResolveDealSchema, session: object) -> Deal:
        return Deal(
            id=data.deal_id,
            amount_source=Decimal("10"),
            amount_target=Decimal("5.00"),
            currency_source="USD",
            currency_target="EUR",
            rate=Decimal("0.5000"),
            status=DealStatus.COMPLETED,
        )

    monkeypatch.setattr("exchange.api.deals.change_status", change_status)

    result = asyncio.run(
        resolve_deal(ResolveDealSchema(deal_id=7, requested_status="accept"), None)
    )

    assert result.id == 7
    assert result.status == DealStatus.COMPLETED


def test_stat(monkeypatch: pytest.MonkeyPatch) -> None:
    async def get_stat(data: StatSchema, session: object) -> list[dict[str, object]]:
        return [
            {
                "currency": "USD",
                "total_in": Decimal("1.00E+6"),
                "total_out": Decimal("0"),
                "deals_count": 1,
            }
        ]

    monkeypatch.setattr("exchange.api.deals.get_stat", get_stat)

    rows = asyncio.run(stat(StatSchema(start_date="01.11.2026", end_date="09.11.2026"), None))
    data = rows[0].model_dump(mode="json")

    assert data["total_in"] == "1000000.00"
    assert data["total_out"] == "0.00"


def test_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    async def get_pending(session: object) -> list[Deal]:
        return [
            Deal(
                id=1,
                amount_source=Decimal("10"),
                amount_target=Decimal("5.00"),
                currency_source="USD",
                currency_target="EUR",
                rate=Decimal("0.5000"),
            )
        ]

    monkeypatch.setattr("exchange.api.deals.get_pending_deals", get_pending)

    rows = asyncio.run(pending_deals(None))

    assert rows[0].id == 1
    assert rows[0].currency_source == "USD"
