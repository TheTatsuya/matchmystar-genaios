from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class ReActAgentState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    agents_queue: list[str] = Field([], description="The list of agents IDs to run")
