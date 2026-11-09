import json
from decimal import Decimal
from typing import Annotated

import aiohttp
from fastapi import APIRouter, Depends, Query
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from exchange.api.schemas import (
    CreateDealSchema,
    NbrbRateSchema,
    ResolveDealSchema,
    ResponseCreateDealSchema,
    ResponsePendingSchema,
    ResponseResolveDealSchema,
    ResponseStatSchema,
    StatSchema,
)
from exchange.config.db_config import get_session
from exchange.repo.deal_repo import change_status, get_pending_deals, get_stat
from exchange.repo.deal_repo import create_deal as save_deal
from exchange.repo.rates_repo import get_needed_rates, save_rates
from exchange.services import convert, get_rate_dto

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.post("/rates")
async def get_rates(session: DbSession) -> dict[str, str]:
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
    payload = json.loads(text, parse_float=Decimal)
    rates = TypeAdapter(list[NbrbRateSchema]).validate_python(payload)
    await save_rates(rates, session)
    return {"message": "Rates saved successfully"}


@router.post("/create", response_model=ResponseCreateDealSchema)
async def create_deal(data: CreateDealSchema, session: DbSession) -> ResponseCreateDealSchema:
    rates = await get_needed_rates(data.currency_source, data.currency_target, session)
    source_rate_dto = get_rate_dto(data.currency_source, rates)
    target_rate_dto = get_rate_dto(data.currency_target, rates)
    amount_target, calculated_rate = convert(data.amount_source, source_rate_dto, target_rate_dto)
    deal = await save_deal(data, calculated_rate, amount_target, session)
    return ResponseCreateDealSchema.model_validate(deal)


@router.post("/{deal_id}/resolve")
async def resolve_deal(data: ResolveDealSchema, session: DbSession) -> ResponseResolveDealSchema:
    deal = await change_status(data, session)
    return ResponseResolveDealSchema.model_validate(deal)


@router.get("/stat")
async def stat(
    data: Annotated[StatSchema, Query()], session: DbSession
) -> list[ResponseStatSchema]:
    statistic = await get_stat(data, session)
    return [ResponseStatSchema.model_validate(row) for row in statistic]


@router.get("/pending")
async def pending_deals(session: DbSession) -> list[ResponsePendingSchema]:
    deals = await get_pending_deals(session)
    return [ResponsePendingSchema.model_validate(deal) for deal in deals]
