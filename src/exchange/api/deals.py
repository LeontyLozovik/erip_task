import json
from decimal import Decimal
from typing import Annotated

import aiohttp
from fastapi import APIRouter, Depends
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from exchange.api.schemas import (
    CreateDealSchema,
    NbrbRateSchema,
    ResolveDealSchema,
    ResponseCreateDealSchema,
    ResponseResolveDealSchema,
)
from exchange.config.db_config import get_session
from exchange.repo.deal_repo import change_status
from exchange.repo.deal_repo import create_deal as save_deal
from exchange.repo.rates_repo import get_rate_data, save_rates
from exchange.services import calculate_amount_target

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


@router.post("/create")
async def create_deal(data: CreateDealSchema, session: DbSession) -> ResponseCreateDealSchema:
    rate_data = await get_rate_data(data.currency_source, session)
    amount_target = calculate_amount_target(data.amount_source, rate_data.rate)
    deal = await save_deal(data, rate_data, amount_target, session)
    return ResponseCreateDealSchema.model_validate(deal)


@router.post("/{deal_id}/resolve")
async def resolve_deal(data: ResolveDealSchema, session: DbSession) -> ResponseResolveDealSchema:
    deal = await change_status(data, session)
    return ResponseResolveDealSchema.model_validate(deal)


@router.get("/stat/")
async def get_stat() -> None:
    pass


@router.get("/pending")
async def get_pending_deals() -> None:
    pass
