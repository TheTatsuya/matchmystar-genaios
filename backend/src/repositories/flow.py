from typing import List, Optional, Union

from sqlalchemy import delete, select, and_
from src.repositories.base import CRUDBase
from src.models import Agent, AgentWorkflow, User
from src.schemas.api.flow.schemas import AgentFlowCreate, AgentFlowUpdate, FlowAgentId
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.agent import agent_repo
from fastapi import HTTPException


class AgentWorkflowRepository(
    CRUDBase[AgentWorkflow, AgentFlowCreate, AgentFlowUpdate]
):
    def get_invalid_agent_ids_exception(self, agent_ids: list[str]):
        return HTTPException(
            status_code=400,
            detail=f"Cannot create the agent flow as agents '[{','.join(agent_ids)}]' do not exist",
        )

    def get_empty_flow_exception(self):
        return HTTPException(
            status_code=400,
            detail="Cannot create an empty flow",
        )

    async def validate_flow_agent_exists(
        self, db: AsyncSession, flow: Optional[List[FlowAgentId]], user_model: User
    ):
        """
            Validates that all agents in a given flow exist in the database and are owned by
            the current user.

            Args:
                db: The database session.
                flow: A list of Flow objects, each containing an agent_id.  If None or empty,
        validation passes.
                user_model: The User model representing the user making the request.

            Returns:
                True if all agents in the flow exist and are owned by the user; False if the
        flow is empty.

            Raises:
                self.get_invalid_agent_id_exception: If an agent in the flow does not exist or
        is not owned by the user.

            Note:
                Currently, agents must be owned by the user making the request.  Future
            enhancements may allow users to utilize agents from other users, which would require modifying the
            validation logic.
        """
        if flow:
            agent_ids_in = [agent.agent_id for agent in flow]
            # TODO: later on users may be allowed to use agents from other users,
            # then adjust this query by searching agents without the user
            q = await db.execute(select(Agent.id).where(Agent.id.in_(agent_ids_in)))
            agent_ids = q.scalars().all()
            if not agent_ids:
                raise self.get_invalid_agent_ids_exception(agent_ids=agent_ids_in)
            return True  # all agents from flow exist in the db and were created by user
        return False  # empty flow

    async def create_by_user(
        self, db: AsyncSession, *, obj_in: AgentFlowCreate, user_model: User
    ) -> AgentWorkflow:
        """
            Creates a new AgentWorkflow associated with the given user.

            Args:
                db: The database session.
                obj_in: The AgentFlowCreate object containing the workflow details, including
        the flow.
                user_model: The User model representing the user creating the workflow.

            Returns:
                The newly created AgentWorkflow object.

            Raises:
                HTTPException: If the flow is empty.
                HTTPException: If any agent in the flow does not exist or
        is not owned by the user.

            Note:
                Validates that all agents in the flow exist and are owned by the user before
        creating the workflow.
        """
        valid_flow = await self.validate_flow_agent_exists(
            db=db, flow=obj_in.flow, user_model=user_model
        )
        if not valid_flow:
            raise self.get_empty_flow_exception()

        db_obj = self.model(
            name=obj_in.name,
            description=obj_in.description,
            flow=[flow.model_dump(mode="json") for flow in obj_in.flow],
            creator_id=user_model.id,
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_multiple(
        self, db: AsyncSession, flow_ids: list[str], user_id: str
    ):
        result = await db.execute(
            delete(self.model).where(
                and_(self.model.id.in_(flow_ids), self.model.creator_id == user_id)
            )
        )
        await db.commit()
        return result

    async def delete_all_flows_where_deleted_agent_exists(
        self, db: AsyncSession, agent_id: str, user_model: User
    ):
        """
            Deletes all flows that contain the specified agent ID.

            Args:
                db: The database session.
                agent_id: The ID of the agent to search for in flows.

            Returns:
                A list of Flow IDs that were deleted, or None if no flows were found containing
        the agent.

            Note:
                This function identifies and deletes flows containing the provided agent ID.
        """
        q = await db.execute(
            select(self.model).where(self.model.creator_id == str(user_model.id))
        )
        flows = q.scalars().all()

        flow_ids_to_delete: list[Optional[str]] = []
        for flow in flows:
            flow_list = flow.flow
            agent_ids = [agent["agent_id"] for agent in flow_list]
            if agent_id in agent_ids:
                flow_ids_to_delete.append(str(flow.id))

        if flow_ids_to_delete:
            result = await self.delete_multiple(
                db=db, flow_ids=flow_ids_to_delete, user_id=str(user_model.id)
            )
            if result:
                return flow_ids_to_delete

        return None

    async def validate_all_agents_in_flow_are_active(
        self,
        db: AsyncSession,
        obj_in: Union[AgentFlowCreate, AgentFlowUpdate],
        user_model: User,
    ) -> Optional[list[str]]:
        agent_ids = [agent.agent_id for agent in obj_in.flow]
        valid_agents = await agent_repo.get_agents_by_ids(
            db=db, agent_ids=agent_ids, user_model=user_model
        )
        if non_active_agents := list(set(agent_ids) - set(valid_agents)):
            raise HTTPException(
                status_code=400,
                detail=f"One or more agents were not registered previously or are not active: {repr(non_active_agents)}. Make sure agent was registered by you and is active before including it into the agent flow",  # noqa: E501
            )
        return valid_agents

    async def update_flow(
        self,
        db: AsyncSession,
        flow_id: str,
        upd_data: AgentFlowUpdate,
        user_model: User,
    ) -> Optional[AgentWorkflow]:
        valid_agents = await self.validate_all_agents_in_flow_are_active(
            db=db, obj_in=upd_data, user_model=user_model
        )
        if valid_agents:
            return await self.update_by_id(
                db=db, id_=flow_id, obj_in=upd_data, user_model=user_model
            )


agentflow_repo = AgentWorkflowRepository(AgentWorkflow)
