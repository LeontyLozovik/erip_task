from datetime import UTC, datetime
from decimal import Decimal

from exchange.api.schemas import RateDTO
from exchange.models import Rate


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
