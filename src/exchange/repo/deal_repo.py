from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import RowMapping, func, literal, or_, select, union_all
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from exchange.api.schemas import CreateDealSchema, ResolveDealSchema, StatSchema
from exchange.config.loggers import api_logger
from exchange.models import Deal, DealStatus


async def create_deal(
    data: CreateDealSchema, calculated_rate: Decimal, amount_target: Decimal, session: AsyncSession
) -> Deal:
    new_deal = Deal(
        amount_source=data.amount_source,
        amount_target=amount_target,
        currency_source=data.currency_source,
        currency_target=data.currency_target,
        rate=calculated_rate,
    )
    session.add(new_deal)
    try:
        await session.commit()
        await session.refresh(new_deal)
        api_logger.info(
            f"Deal created successfully. id:{new_deal.id} amount_source:{new_deal.amount_source} amount_target:{new_deal.amount_target} currency_source:{new_deal.currency_source} currency_target:{new_deal.currency_target} rate:{new_deal.rate}"
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
    deal.resolved_at = datetime.now(UTC)

    try:
        await session.commit()
        await session.refresh(deal)
        api_logger.info(f"Deal status changed successfully. id:{deal.id} status:{deal.status}")
        return deal
    except SQLAlchemyError as e:
        await session.rollback()
        api_logger.error(f"Failed to update deal status: {e}")
        raise


async def get_stat(data: StatSchema, session: AsyncSession) -> Sequence[RowMapping]:
    filters = [
        Deal.status == DealStatus.COMPLETED,
        Deal.resolved_at >= data.start_date,
        Deal.resolved_at <= data.end_date,
    ]

    if data.currency:
        filters.append(
            or_(
                Deal.currency_source == data.currency,
                Deal.currency_target == data.currency,
            )
        )

    income = select(
        Deal.currency_source.label("currency"),
        Deal.amount_source.label("amount_in"),
        literal(Decimal("0")).label("amount_out"),
        Deal.id.label("deal_id"),
    ).where(*filters)

    outcome = select(
        Deal.currency_target.label("currency"),
        literal(Decimal("0")).label("amount_in"),
        Deal.amount_target.label("amount_out"),
        Deal.id.label("deal_id"),
    ).where(*filters)

    all_deals = union_all(income, outcome).subquery()

    query = (
        select(
            all_deals.c.currency,
            func.sum(all_deals.c.amount_in).label("total_in"),
            func.sum(all_deals.c.amount_out).label("total_out"),
            func.count(func.distinct(all_deals.c.deal_id)).label("deals_count"),
        )
        .group_by(all_deals.c.currency)
        .order_by(all_deals.c.currency)
    )

    result = await session.execute(query)
    return result.mappings().all()


async def get_pending_deals(session: AsyncSession) -> list[Deal]:
    query = select(Deal).where(Deal.status == DealStatus.PENDING)
    result = await session.scalars(query)
    deals = list(result.all())
    return deals
