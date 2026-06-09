from fastapi import APIRouter
from . import services

router = APIRouter(tags=["auth"])
router.include_router(services.router)
