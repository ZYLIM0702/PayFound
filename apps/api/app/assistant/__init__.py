from fastapi import APIRouter

from .realtime import router as realtime_router
from .stream import router as stream_router

router = APIRouter()
router.include_router(stream_router)
router.include_router(realtime_router)

__all__ = ['router']
