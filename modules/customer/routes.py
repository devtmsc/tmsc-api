from fastapi import APIRouter
from . import services

router = APIRouter(tags=["customer"])
router.include_router(services.router)
