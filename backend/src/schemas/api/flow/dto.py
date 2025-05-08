from typing import List, Union
from uuid import UUID
from src.schemas.api.flow.schemas import AgentFlowList
from pydantic import BaseModel, field_validator


class AgentFlowDTO(AgentFlowList):
    id: Union[UUID, str]

    @field_validator("id")
    def cast_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


class AgentFlowsList(BaseModel):
    flows: List[AgentFlowDTO]
