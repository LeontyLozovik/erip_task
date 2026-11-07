from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from exchange.api.router import router
from exchange.config.loggers import api_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    api_logger.info("application started")
    yield
    api_logger.info("application stopped")


app = FastAPI(lifespan=lifespan)
app.include_router(router)
