from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from exchange.api.router import router
from exchange.config.loggers import api_logger
from exchange.services import load_daily_rates

scheduler = AsyncIOScheduler(timezone="Europe/Minsk")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    api_logger.info("Starting the application")
    try:
        await load_daily_rates()
    except Exception:
        api_logger.error("Starting without a fresh NBRB snapshot")
    scheduler.add_job(
        load_daily_rates,
        CronTrigger(hour=6, minute=00, timezone="Europe/Minsk"),
        id="nbrb_daily_rates",
        replace_existing=True,
    )
    api_logger.info("Task scheduled")
    scheduler.start()
    yield
    scheduler.shutdown()
    api_logger.info("Application stopped")


app = FastAPI(
    title="Currency exchange",
    description="Exchange deals, NBRB rates, and cash desk statistics.",
    lifespan=lifespan,
)
app.include_router(router)
