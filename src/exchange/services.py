import json
from datetime import UTC, datetime
from decimal import Decimal

import aiohttp
from pydantic import TypeAdapter, ValidationError

from exchange.api.schemas import NbrbRateSchema, RateDTO
from exchange.config.db_config import AsyncSessionFabric
from exchange.config.loggers import api_logger
from exchange.models import Rate
from exchange.repo.rates_repo import save_rates


async def load_daily_rates() -> None:
    try:
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
    except (aiohttp.ClientError, TimeoutError) as e:
        api_logger.error(f"Failed to fetch NBRB rates: {e}")
        raise

    try:
        payload = json.loads(text, parse_float=Decimal)
        rates = TypeAdapter(list[NbrbRateSchema]).validate_python(payload)
    except (json.JSONDecodeError, ValidationError) as e:
        api_logger.error(f"Invalid NBRB rates payload: {e}")
        raise

    if not rates:
        api_logger.warning("NBRB returned no rates")
        return

    api_logger.info("Successfuly fetch NBRB rates")
    async with AsyncSessionFabric() as session:
        await save_rates(rates, session)


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
