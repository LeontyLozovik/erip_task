from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import insert

from exchange.api.schemas import NbrbRateSchema
from exchange.config.loggers import api_logger
from exchange.models import Rate


async def save_rates(rates: list[NbrbRateSchema], session: AsyncSession) -> None:
    rows = [rate.model_dump() for rate in rates]
    query = insert(Rate).values(rows)
    try:
        await session.execute(query)
        await session.commit()
        api_logger.info(f"Saved {len(rates)} rates")
        return
    except SQLAlchemyError as e:
        await session.rollback()
        api_logger.error(f"Failed to save rates: {e}")
        raise


async def get_needed_rates(
    currency_source: str, currency_target: str, session: AsyncSession
) -> dict[str, Rate]:
    needed = [cur_abbr for cur_abbr in (currency_source, currency_target) if cur_abbr != "BYN"]
    result_rates: dict[str, Rate] = {}
    if needed:
        for rate_abbr in needed:
            query = (
                select(Rate)
                .where(Rate.abbreviation == rate_abbr)
                .order_by(Rate.rate_date.desc())
                .limit(1)
            )
            try:
                result = await session.execute(query)
                rate_row = result.scalar_one_or_none()
            except SQLAlchemyError as e:
                api_logger.error(f"Failed to get rate for {rate_abbr}: {e}")
                raise
            if rate_row is None:
                raise ValueError(f"No rate for {rate_abbr}")
            result_rates[rate_abbr] = rate_row
    return result_rates
