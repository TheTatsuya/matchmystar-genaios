from typing import Optional
from fastapi import APIRouter, HTTPException

from src.auth.dependencies import (
    CurrentUserDependency,
    CurrentUserByAgentOrUserTokenDependency,
)
from src.db.session import AsyncDBSession
from src.repositories.agent import agent_repo
from src.repositories.flow import agentflow_repo
from src.schemas.api.agent.schemas import AgentRegister, AgentUpdate
from src.schemas.api.agent.dto import (
    ActiveAgentsWithQueryParams,
    AgentDTOWithJWT,
    MLAgentJWTDTO,
)
from uuid import UUID
from fastapi.responses import Response
from sqlalchemy.exc import IntegrityError
import traceback
import logging

logger = logging.getLogger(__name__)
agent_router = APIRouter(tags=["agents"], prefix="/agents")


@agent_router.get(
    path="/active",
    summary="Get list of active agent connections",
)
async def get_active_connections(
    db: AsyncDBSession,
    user_model: CurrentUserByAgentOrUserTokenDependency,
    offset: int = 0,
    limit: int = 100,
) -> ActiveAgentsWithQueryParams:
    agents = await agent_repo.get_all_online_agents_by_user(
        db=db, user_model=user_model, offset=offset, limit=limit
    )
    return ActiveAgentsWithQueryParams(**agents.__dict__, limit=limit, offset=offset)


@agent_router.get("/", response_model=list[MLAgentJWTDTO])
async def list_all_agents(
    db: AsyncDBSession,
    user: CurrentUserByAgentOrUserTokenDependency,
    offset: Optional[int] = 0,
    limit: int = 100,
):
    # TODO: pagination
    return await agent_repo.list_all_agents(
        db=db, user_model=user, offset=offset, limit=limit
    )


@agent_router.get("/{agent_id}", response_model=MLAgentJWTDTO)
async def get_data(
    db: AsyncDBSession, user: CurrentUserByAgentOrUserTokenDependency, agent_id: UUID
):
    return await agent_repo.get_agent(db=db, id_=str(agent_id), user_model=user)


@agent_router.post("/register", response_model=AgentDTOWithJWT)
async def register_agent(
    db: AsyncDBSession, user: CurrentUserDependency, agent_in: AgentRegister
):
    try:
        agent_with_token = await agent_repo.create_by_user(
            db=db, obj_in=agent_in, user_model=user
        )
        return agent_with_token
    except IntegrityError:
        logger.debug(traceback.format_exc())
        raise HTTPException(
            status_code=400, detail=f"Agent with {agent_in.id} already exists"
        )

    # if 400 is raised in agent_repo, catch and reraise here so it is not catched by 500 err response
    except HTTPException as e:
        raise e

    except Exception:
        logger.error(f"Unexpected error occured: {traceback.format_exc(limit=600)}")
        raise HTTPException(
            status_code=500, detail="Unexpected error occured, try again later."
        )


@agent_router.patch("/{agent_id}")
async def update_agent(
    db: AsyncDBSession,
    user: CurrentUserDependency,
    agent_id: UUID,
    agent_upd_data: AgentUpdate,
):
    agent = await agent_repo.update_by_id(
        db=db, id_=str(agent_id), obj_in=agent_upd_data, user_model=user
    )

    return agent


@agent_router.delete("/{agent_id}")
async def delete_agent(
    db: AsyncDBSession,
    user: CurrentUserDependency,
    agent_id: UUID,
):
    await agentflow_repo.delete_all_flows_where_deleted_agent_exists(
        db=db, agent_id=str(agent_id), user_model=user
    )
    is_ok = await agent_repo.delete(db=db, id_=str(agent_id))
    if not is_ok:
        raise HTTPException(status_code=400, detail=f"Agent {agent_id} was not found")

    return Response(status_code=204)
