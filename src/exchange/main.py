from fastapi import FastAPI

from exchange.api.router import router

app = FastAPI()
app.include_router(router)
