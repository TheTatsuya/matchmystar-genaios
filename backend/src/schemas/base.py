from uuid import UUID
from pydantic import BaseModel, field_validator
from typing import Union


class BaseUUIDToStrModel(BaseModel):
    id: Union[UUID, str]

    @field_validator("id")
    def cast_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
