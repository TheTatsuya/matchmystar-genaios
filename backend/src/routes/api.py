from fastapi import APIRouter
from src.routes.user.routes import user_router
from src.routes.agents.routes import agent_router
from src.routes.flows.routes import flow_router
from src.routes.logs.routes import log_router
from src.routes.utils.routes import utils_router


api_router = APIRouter(prefix="/api")
api_router.include_router(user_router)
api_router.include_router(agent_router)
api_router.include_router(flow_router)
api_router.include_router(log_router)
api_router.include_router(utils_router)
