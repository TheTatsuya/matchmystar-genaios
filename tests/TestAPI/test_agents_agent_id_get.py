from typing import Awaitable, Callable
import uuid
import pytest
import asyncio

import logging
from tests.http_client.AsyncHTTPClient import AsyncHTTPClient
from genai_session.session import GenAISession
from tests.conftest import DummyAgent

ENDPOINT = "/api/agents/{agent_id}"

http_client = AsyncHTTPClient(timeout=10)


@pytest.mark.asyncio
async def test_agent_agent_id_valid_agent_id(
    user_jwt_token: str,
    agent_jwt_factory: Callable[[str], Awaitable[str]],
    agent_factory: Callable[[], DummyAgent],
):
    dummy_agent = agent_factory()

    JWT_TOKEN = await agent_jwt_factory(user_jwt_token)

    session = GenAISession(jwt_token=JWT_TOKEN)

    @session.bind(name=dummy_agent.name, description=dummy_agent.description)
    async def example_agent(agent_context=""):
        return True

    async def process_events():
        """Processes events for the GenAISession."""
        # logging.info(f"Agent with ID {JWT_TOKEN} started")
        await session.process_events()

    try:
        event_task = asyncio.create_task(process_events())

        await asyncio.sleep(0.1)

        agent = await http_client.get(
            path=ENDPOINT.format(agent_id=session.agent_id),
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        created_at = agent.pop("created_at")
        updated_at = agent.pop("updated_at")
        assert created_at
        assert updated_at

        expected_agent = {
            "agent_id": session.agent_id,
            "agent_name": dummy_agent.name,
            "agent_description": dummy_agent.description,
            "agent_input_schema": {
                "type": "function",
                "function": {
                    "name": session.agent_id,
                    "description": dummy_agent.description,
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            "agent_jwt": JWT_TOKEN,
            "is_active": True,
        }

        assert agent == expected_agent

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            logging.info("Background task has been properly cancelled.")


@pytest.mark.asyncio
async def test_agent_agent_id_wrong_agent_id(
    user_jwt_token: str,
    agent_jwt_factory: Callable[[str], Awaitable[str]],
    agent_factory: Callable[[], DummyAgent],
):
    dummy_agent = agent_factory()

    session = GenAISession(jwt_token=await agent_jwt_factory(user_jwt_token))

    @session.bind(name=dummy_agent.name, description=dummy_agent.description)
    async def example_agent(agent_context=""):
        return True

    async def process_events():
        """Processes events for the GenAISession."""
        # logging.info(f"Agent with ID {JWT_TOKEN} started")
        await session.process_events()

    try:
        event_task = asyncio.create_task(process_events())

        await asyncio.sleep(0.1)

        invalid_agent_id = str(uuid.uuid4())

        agent = await http_client.get(
            path=ENDPOINT.format(agent_id=invalid_agent_id),
            expected_status_codes=[400],
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_agent = {"detail": f"Agent {invalid_agent_id} was not found."}

        assert agent == expected_agent

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            logging.info("Background task has been properly cancelled.")


@pytest.mark.asyncio
async def test_agent_agent_id_invalid_agent_id(
    user_jwt_token: str,
    agent_jwt_factory: Callable[[str], Awaitable[str]],
    agent_factory: Callable[[], DummyAgent],
):
    dummy_agent = agent_factory()

    JWT_TOKEN = await agent_jwt_factory(user_jwt_token)

    session = GenAISession(jwt_token=JWT_TOKEN)

    @session.bind(name=dummy_agent.name, description=dummy_agent.description)
    async def example_agent(agent_context=""):
        return True

    async def process_events():
        """Processes events for the GenAISession."""
        # logging.info(f"Agent with ID {JWT_TOKEN} started")
        await session.process_events()

    try:
        event_task = asyncio.create_task(process_events())

        await asyncio.sleep(0.1)

        agent = await http_client.get(
            path=ENDPOINT.format(agent_id=None),
            expected_status_codes=[422],
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_agent = {
            "detail": [
                {
                    "type": "uuid_parsing",
                    "loc": ["path", "agent_id"],
                    "msg": "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `N` at 1",  # noqa: E501
                    "input": f"{str(None)}",
                    "ctx": {
                        "error": "invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `N` at 1"  # noqa: E501
                    },
                }
            ]
        }

        assert agent == expected_agent

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            logging.info("Background task has been properly cancelled.")
