from typing import Optional, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from src.auth.encrypt import encrypt_secret
from src.schemas.base import BaseUUIDToStrModel
from src.utils.constants import DEFAULT_SYSTEM_PROMPT


class ModelProviderBase(BaseModel):
    api_key: str


class ModelConfigBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    model: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = Field(default=0.7)

    credentials: Optional[dict] = {}


class ModelConfigExtras(ModelConfigBase):
    system_prompt: Optional[str] = Field(default=DEFAULT_SYSTEM_PROMPT)
    user_prompt: Optional[str] = ""
    max_last_messages: Optional[int] = Field(default=5)

    @model_validator(mode="after")
    def strip_str_values(self) -> Self:
        for attr in self.__dict__.keys():
            obj = getattr(self, attr)
            if isinstance(obj, str):
                setattr(self, attr, obj.strip())

        self.credentials = {
            k: v.strip() for k, v in self.credentials.items() if isinstance(v, str)
        }
        return self

    @field_validator("max_last_messages")
    def validate_int_range(cls, v: int):
        if 0 <= v <= 20:
            return v

        raise ValueError("'max_last_messages' value must be 0 ≤ max_last_messages ≤ 20")


class ModelConfigCreate(ModelConfigExtras):
    provider: str


class ModelConfigUpdate(ModelConfigExtras):
    name: Optional[str] = None
    model: Optional[str] = None


class ModelConfigDelete(BaseUUIDToStrModel):
    pass


class ProviderCRUDUpdate(BaseModel):
    api_key: Optional[str] = None
    metadata: Optional[dict] = Field(default={})

    @field_validator("api_key")
    def encrypt_key(cls, v: str):
        if len(v) < 1:
            raise ValueError("'api_key' param cannot be empty")
        if isinstance(v, str):
            return encrypt_secret(v)
        return v

    def dump(self):
        r = {**self.model_dump(mode="json"), "provider_metadata": self.metadata}
        if not self.api_key:
            # prevent update with None as api_key
            r.pop("api_key")

        return r


class ProviderCRUDCreate(ProviderCRUDUpdate):
    api_key: str
    name: str
