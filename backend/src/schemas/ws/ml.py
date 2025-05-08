from typing import List, Union, Optional

from pydantic import BaseModel
from src.schemas.api.flow.schemas import FlowSchema
from src.schemas.ws.dto.response import MLAgentSchema
from src.schemas.ws.frontend import LLMPropertiesDTO
from src.schemas.api.files.dto import FileDTO


class OutgoingMLRequestSchema(BaseModel):
    message: str
    agents: List[Union[MLAgentSchema, FlowSchema]]
    configs: LLMPropertiesDTO
    files: Optional[List[FileDTO]] = []


class IncomingMLResponseSchema(BaseModel):
    session_id: str
    request_id: str
    agents_plan: List
