import string
import aiohttp
import jwt
import pytest_asyncio
import os
import random

from typing import Callable

from tests.constants import TEST_FILES_FOLDER
from pydantic import BaseModel, Field

os.environ["ROUTER_WS_URL"] = "ws://0.0.0.0:8080/ws"
os.environ["DEFAULT_FILES_FOLDER_NAME"] = TEST_FILES_FOLDER


class HttpClient:
    def __init__(self, base_url: str = ""):
        self.base_url = base_url.rstrip("/")

    async def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                return await response.json()

    async def get(self, path: str, **kwargs):
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs):
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs):
        return await self._request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs):
        return await self._request("DELETE", path, **kwargs)


http_client = HttpClient(base_url="http://localhost:8000")


def _generate_random_string(length: int):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


class DummyAgent(BaseModel):
    name: str = Field(default_factory=lambda x: _generate_random_string(8))
    description: str = Field(default_factory=lambda x: _generate_random_string(8))
    input_parameters: dict = Field({})


@pytest_asyncio.fixture(autouse=True)
async def registered_user():
    register_url = "/api/register"
    username = _generate_random_string(6)
    creds = {"username": username, "password": "test_pwd"}
    await http_client.post(path=register_url, json=creds)
    return creds


@pytest_asyncio.fixture(autouse=True)
async def user_jwt_token(registered_user):
    login_url = "/api/login/access-token"
    form_data = aiohttp.FormData()
    form_data.add_field(name="username", value=registered_user["username"])
    form_data.add_field(name="password", value=registered_user["password"])
    response = await http_client.post(path=login_url, data=form_data)
    return response["access_token"]


@pytest_asyncio.fixture(autouse=True)
async def dummy_agent():
    agent = DummyAgent()
    return agent


@pytest_asyncio.fixture(autouse=True)
async def agent_factory():
    def generate_dummy_agent():
        return DummyAgent()

    return generate_dummy_agent


@pytest_asyncio.fixture(autouse=True)
async def agent_jwt_factory(agent_factory: Callable[[], DummyAgent]):
    async def agent_jwt_token(user_jwt_token: str):
        login_url = "/api/agents/register"
        dummy_agent = agent_factory()
        response = await http_client.post(
            path=login_url,
            json=dummy_agent.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )
        return response["jwt"]

    return agent_jwt_token


@pytest_asyncio.fixture(autouse=True)
async def get_user():
    async def decode_token(user_jwt_token: str):
        decoded = jwt.decode(
            user_jwt_token, options={"verify_signature": False}, algorithms=["HS256"]
        )
        return decoded.get("sub")

    return decode_token
