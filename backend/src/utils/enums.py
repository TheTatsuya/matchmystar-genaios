from enum import Enum


class AgentPlanType(Enum):
    agent = "agent"
    flow = "flow"


class FileValidationOutputChoice(Enum):
    file_id = "file_id"
    dto = "dto"
