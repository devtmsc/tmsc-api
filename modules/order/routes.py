from fastapi import APIRouter
from . import services

router = APIRouter(tags=["order"])
router.include_router(services.router)
