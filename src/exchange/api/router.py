from fastapi import APIRouter

from exchange.api.deals import router as deal_router

router = APIRouter()

router.include_router(deal_router, prefix="/deal", tags=["deal"])
