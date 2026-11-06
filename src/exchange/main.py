from fastapi import FastAPI

from exchange.config.loggers import api_logger
from exchange.routers import router

app = FastAPI()
app.include_router(router)
api_logger.info("application started")
