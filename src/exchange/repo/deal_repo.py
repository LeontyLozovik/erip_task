from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from exchange.api.schemas import CreateDealSchema, RateDTO, ResolveDealSchema
from exchange.config.loggers import api_logger
from exchange.models import Deal


async def create_deal(
    data: CreateDealSchema, rate_dto: RateDTO, amount_target: Decimal, session: AsyncSession
) -> Deal:
    new_deal = Deal(
        amount_source=data.amount_source,
        amount_target=amount_target,
        currency_source=data.currency_source,
        currency_target=data.currency_target,
        rate=rate_dto.rate,
        rate_date=rate_dto.rate_date,
    )
    session.add(new_deal)
    try:
        await session.commit()
        await session.refresh(new_deal)
        api_logger.info(
            f"Deal created successfully. id:{new_deal.id} amount_source:{new_deal.amount_source} amount_target:{new_deal.amount_target} currency_source:{new_deal.currency_source} currency_target:{new_deal.currency_target} rate:{new_deal.rate} rate_date:{new_deal.rate_date}"
        )
        return new_deal
    except SQLAlchemyError as e:
        await session.rollback()
        api_logger.error(f"Failed to create deal: {e}")
        raise


async def change_status(data: ResolveDealSchema, session: AsyncSession) -> Deal:
    query = select(Deal).where(Deal.id == data.deal_id).with_for_update()
    deal = await session.scalar(query)
    if not deal:
        api_logger.error(f"Deal with id {data.deal_id} not found")
        raise ValueError(f"Deal with id {data.deal_id} not found")
    deal.status = data.requested_status
    await session.commit()
    await session.refresh(deal)
    api_logger.info(f"Deal status changed successfully. id:{deal.id} status:{deal.status}")
    return deal
