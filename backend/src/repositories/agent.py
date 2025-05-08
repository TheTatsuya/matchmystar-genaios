from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import and_, select
from src.auth.jwt import TokenLifespanType, create_access_token, validate_token
from src.schemas.api.agent.dto import (
    ActiveAgentsDTO,
    AgentDTOWithJWT,
    MLAgentJWTDTO,
    MLAgentSchema,
)
from src.repositories.base import CRUDBase
from src.models import Agent, User
from src.schemas.api.agent.schemas import AgentCreate, AgentRegister, AgentUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class AgentRepository(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    async def get_one_by_user(
        self, db: AsyncSession, id_: UUID, user_model: User
    ) -> Optional[Agent]:
        """
        Method to get an agent by user.
        In case when two agents have the same id, name, description
        the agent with the most recent last_invoked_at will be returned.
        """
        q = await db.execute(
            select(self.model)
            .where(
                and_(
                    self.model.id == str(id_),
                    self.model.creator_id == str(user_model.id),
                )
            )
            .order_by(self.model.last_invoked_at.desc())
        )
        return q.scalars().first()

    async def create_by_user(
        self, db: AsyncSession, *, obj_in: AgentRegister, user_model: User
    ) -> AgentDTOWithJWT:
        """
        Creates a new Agent associated with the given user.

        Args:
            db: The database session.
            obj_in: The AgentRegister object containing the agent's details.
            user_id: The ID of the user creating the agent.

        Returns:
            The newly created Agent object.

        Raises:
            Any database-related exceptions will be propagated.
        """

        # This lookup for existing agent is needed due to the way jwt is created.
        # Since jwt is tied to the `Agent.id`, it needs to be added via `db_obj.jwt = jwt`
        # which is treated as table **update** by sqlalchemy

        existing_agent = await self.get_by_user(
            db=db, id_=obj_in.id, user_model=user_model
        )
        if existing_agent:
            raise HTTPException(
                status_code=400, detail=f"Agent with {obj_in.id} already exists"
            )

        db_obj = Agent(
            id=obj_in.id,
            name=obj_in.name,
            description=obj_in.description,
            input_parameters=obj_in.input_parameters,
            creator_id=str(user_model.id),
            is_active=False,
        )
        jwt = create_access_token(
            subject=str(db_obj.id),
            lifespan_type=TokenLifespanType.cli,
            user_id=str(db_obj.creator_id),
        )
        db_obj.jwt = jwt
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return AgentDTOWithJWT(**db_obj.__dict__)

    async def get_all_online_agents(
        self, db: AsyncSession, user_model: User, offset: int = 0, limit: int = 100
    ) -> list[Agent]:
        """
        Get all agents that were registered in the backend.

        Args:
            db: The database session.

        Returns:
            A list of Agent objects that are online.
        """
        agents = await self.get_multiple_by_user(
            db, user_model=user_model, offset=offset, limit=limit
        )
        agent_schemas = [
            MLAgentSchema(
                agent_id=str(agent.id),
                agent_name=agent.name,
                agent_description=agent.description,
                agent_input_schema=agent.input_parameters,
            ).model_dump(mode="json")
            for agent in agents
            if agent.is_active
        ]
        return ActiveAgentsDTO(
            count_active_connections=len(agent_schemas),
            active_connections=agent_schemas,
        )

    async def get_all_online_agents_by_user(
        self, db: AsyncSession, user_model: User, offset: int = 0, limit: int = 100
    ):
        agents = await self.get_multiple_by_user(
            db, user_model=user_model, offset=offset, limit=limit
        )
        agent_schemas = [
            MLAgentSchema(
                agent_id=str(agent.id),
                agent_name=agent.name,
                agent_description=agent.description,
                agent_input_schema=agent.input_parameters,
            ).model_dump(mode="json")
            for agent in agents
            if agent.is_active
        ]
        return ActiveAgentsDTO(
            count_active_connections=len(agent_schemas),
            active_connections=agent_schemas,
        )

    async def get_agent(
        self, db: AsyncSession, id_: str, user_model: User
    ) -> Optional[MLAgentJWTDTO]:
        agent = await self.get_by_user(db=db, id_=id_, user_model=user_model)
        if not agent:
            raise HTTPException(status_code=400, detail=f"Agent {id_} was not found.")
        return MLAgentJWTDTO(
            agent_id=str(agent.id),
            agent_name=agent.name,
            agent_description=agent.description,
            agent_input_schema=agent.input_parameters,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            is_active=agent.is_active,
            agent_jwt=agent.jwt,
        )

    async def list_all_agents(
        self, db: AsyncSession, user_model: User, limit: int, offset: int
    ) -> list[Optional[MLAgentJWTDTO]]:
        result = await self.get_multiple_by_user(
            db=db, user_model=user_model, offset=offset, limit=limit
        )
        return [
            MLAgentJWTDTO(
                agent_id=str(agent.id),
                agent_name=agent.name,
                agent_description=agent.description,
                agent_input_schema=agent.input_parameters,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                is_active=agent.is_active,
                agent_jwt=agent.jwt,
            )
            for agent in result
        ]

    async def get_agents_by_ids(
        self, db: AsyncSession, agent_ids: list[str], user_model: User
    ) -> list[Optional[str]]:
        """
        Get all agent_ids queried by the provided collection of agent_ids.

        Args:
            db: The database session.
            agents_from_flow: list of [{"agent_id": uuid}, {"agent_id": uuid}, ...]

        Returns:
            A list of Agent objects that are online and match provided agent_id.
        """
        # `is` comparison vs booleans is not supported in SQLAlchemy
        q = await db.execute(
            select(self.model).where(
                and_(
                    self.model.id.in_(agent_ids),
                    self.model.creator_id == user_model.id,
                    self.model.is_active == True,  # noqa: E712
                )
            )
        )
        agents = q.scalars().all()
        return [str(agent.id) for agent in agents]

    async def set_all_agents_inactive(self, db: AsyncSession) -> None:
        """
        Set is_active=False for all agents in the database on startup of the backend

        Args:
            db: The database session.

        Returns: None
        """
        q = await db.execute(select(self.model))
        agents = q.scalars().all()
        if not agents:
            return

        for agent in agents:
            agent.is_active = False

        await db.commit()
        return

    async def set_agent_as_inactive(
        self, db: AsyncSession, id_: str, user_id: str
    ) -> Agent:
        user_q = await db.execute(select(User).where(User.id == user_id))
        user = user_q.scalars().first()
        if not user:
            return

        agent = await self.get_by_user(db=db, id_=id_, user_model=user)
        if agent:
            agent.is_active = False

        await db.commit()
        await db.refresh(agent)
        return agent

    async def validate_agent_by_jwt(
        self, db: AsyncSession, agent_jwt: str
    ) -> Optional[Agent]:
        agent_jwt_payload = validate_token(
            token=agent_jwt, lifespan_type=TokenLifespanType.cli
        )
        if not agent_jwt_payload:
            return  # TODO: raise jwt invalid
        q = await db.execute(
            select(self.model).where(
                and_(
                    self.model.id == agent_jwt_payload.sub,
                    self.model.creator_id == agent_jwt_payload.user_id,
                )
            )
        )
        return q.scalars().first()  # one jwt per one agent per user


agent_repo = AgentRepository(Agent)
