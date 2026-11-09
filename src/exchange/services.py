import json
from datetime import UTC, datetime
from decimal import Decimal

import aiohttp
from pydantic import TypeAdapter

from exchange.api.schemas import NbrbRateSchema, RateDTO
from exchange.config.db_config import AsyncSessionFabric
from exchange.config.loggers import api_logger
from exchange.models import Rate
from exchange.repo.rates_repo import save_rates


async def load_daily_rates() -> None:
    timeout = aiohttp.ClientTimeout(total=30)
    async with (
        aiohttp.ClientSession(timeout=timeout) as client,
        client.get(
            "https://api.nbrb.by/exrates/rates",
            params={"periodicity": 0},
        ) as response,
    ):
        response.raise_for_status()
        text = await response.text()
    api_logger.info("Daily rates loaded")
    payload = json.loads(text, parse_float=Decimal)
    rates = TypeAdapter(list[NbrbRateSchema]).validate_python(payload)
    async with AsyncSessionFabric() as session:
        await save_rates(rates, session)
    api_logger.info("Daily rates saved")


def get_rate_dto(currency: str, rates: dict[str, Rate]) -> RateDTO:
    if currency == "BYN":
        return RateDTO(
            abbreviation="BYN",
            official_rate=Decimal("1"),
            scale=1,
            rate_date=datetime.now(UTC),
        )
    else:
        return RateDTO.model_validate(rates[currency])


def convert(amount_source: Decimal, source: RateDTO, target: RateDTO) -> tuple[Decimal, Decimal]:
    calculated_rate = (source.official_rate / Decimal(source.scale)) / (
        target.official_rate / Decimal(target.scale)
    )
    amount_target = amount_source * calculated_rate
    return (amount_target, calculated_rate)
