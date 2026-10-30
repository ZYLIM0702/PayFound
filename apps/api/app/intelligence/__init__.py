"""Mount with app.include_router(router, prefix='/api') before metadata.create_all."""
from fastapi import APIRouter

from .agents import router as agent_router
from ..assistant import router as assistant_router
from .channel3 import router as online_router
from .models import AgentRun, ConsentGrant, MerchantReport
from .reports import router as report_router
from .status import router as status_router

router = APIRouter()
router.include_router(agent_router)
router.include_router(assistant_router)
router.include_router(online_router)
router.include_router(report_router)
router.include_router(status_router)

__all__ = ['router', 'AgentRun', 'ConsentGrant', 'MerchantReport']
