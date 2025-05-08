from abc import ABC
from typing import Any

from langchain.chat_models.base import BaseChatModel


class BaseMasterAgent(ABC):
    def __init__(self, model: BaseChatModel, agents: list[dict[str, Any]]) -> None:
        self.model = model
        self.agents = agents
