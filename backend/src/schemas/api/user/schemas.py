from pydantic import BaseModel


class UserPassword(BaseModel):
    password: str


class UserCreate(UserPassword):
    username: str


class UserUpdate(UserPassword):
    pass


class TokenValidationInput(BaseModel):
    token: str
