from typing import Awaitable, Callable
import uuid
import pytest
import asyncio
import logging

from tests.http_client.AsyncHTTPClient import AsyncHTTPClient
from genai_session.session import GenAISession
from tests.conftest import DummyAgent

AGENTS_REGISTER_ENDPOINT = "/api/agents/register"
AGENT_ENDPOINT = "/api/agents/{agent_id}"

http_client = AsyncHTTPClient(timeout=10)


@pytest.mark.asyncio
async def test_agents_register_inactive_agent(
    user_jwt_token: str,
    agent_factory: Callable[[], DummyAgent],
):
    dummy_agent = agent_factory()

    agent_id = str(uuid.uuid4())
    json_data = {
        "id": agent_id,
        "name": dummy_agent.name,
        "description": dummy_agent.description,
        "input_parameters": {},
    }

    await http_client.post(
        path=AGENTS_REGISTER_ENDPOINT,
        json=json_data,
        expected_status_codes=[200],
        headers={"Authorization": f"Bearer {user_jwt_token}"},
    )

    agent = await http_client.get(
        path=AGENT_ENDPOINT.format(agent_id=agent_id),
        headers={"Authorization": f"Bearer {user_jwt_token}"},
    )

    agent_jwt = agent.get("agent_jwt")
    created_at = agent.pop("created_at")
    updated_at = agent.pop("updated_at")

    assert created_at
    assert updated_at

    expected_agent = {
        "agent_id": agent_id,
        "agent_name": dummy_agent.name,
        "agent_description": dummy_agent.description,
        "agent_input_schema": {},
        "agent_jwt": agent_jwt,
        "is_active": False,
    }

    assert agent == expected_agent


@pytest.mark.asyncio
async def test_agents_register_already_ative_agent(
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

        await asyncio.sleep(0.3)

        json_data = {
            "id": session.agent_id,
            "name": dummy_agent.name,
            "description": dummy_agent.description,
            "input_parameters": {},
        }

        await http_client.post(
            path=AGENTS_REGISTER_ENDPOINT,
            json=json_data,
            expected_status_codes=[400],
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        agent = await http_client.get(
            path=AGENT_ENDPOINT.format(agent_id=session.agent_id),
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
async def test_agents_register_inactive_agent_with_invalid_id(
    user_jwt_token: str,
    agent_factory: Callable[[], DummyAgent],
):
    dummy_agent = agent_factory()

    json_data = {
        "id": str(uuid.uuid4())[:-1],
        "name": dummy_agent.name,
        "description": dummy_agent.description,
        "input_parameters": {},
    }

    await http_client.post(
        path=AGENTS_REGISTER_ENDPOINT,
        json=json_data,
        expected_status_codes=[400],
        headers={"Authorization": f"Bearer {user_jwt_token}"},
    )


@pytest.mark.asyncio
async def test_agents_register_inactive_agent_with_none_as_id(
    user_jwt_token: str,
    agent_factory: Callable[[], DummyAgent],
):
    dummy_agent = agent_factory()

    json_data = {
        "id": None,
        "name": dummy_agent.name,
        "description": dummy_agent.description,
        "input_parameters": {},
    }

    await http_client.post(
        path=AGENTS_REGISTER_ENDPOINT,
        json=json_data,
        expected_status_codes=[400],
        headers={"Authorization": f"Bearer {user_jwt_token}"},
    )


@pytest.mark.asyncio
async def test_agents_register_incative_agent_with_none_as_name(user_jwt_token: str):
    AGENT_DESCRIPTION = "Agent Description"

    agent_id = str(uuid.uuid4())

    json_data = {
        "id": agent_id,
        "name": None,
        "description": AGENT_DESCRIPTION,
        "input_parameters": {},
    }

    await http_client.post(
        path=AGENTS_REGISTER_ENDPOINT,
        json=json_data,
        expected_status_codes=[422],
        headers={"Authorization": f"Bearer {user_jwt_token}"},
    )


@pytest.mark.asyncio
async def test_agents_register_incative_agent_with_none_as_description(
    user_jwt_token: str,
):
    AGENT_NAME = "Agent Name"

    agent_id = str(uuid.uuid4())

    json_data = {
        "id": agent_id,
        "name": AGENT_NAME,
        "description": None,
        "input_parameters": {},
    }

    await http_client.post(
        path=AGENTS_REGISTER_ENDPOINT,
        json=json_data,
        expected_status_codes=[422],
        headers={"Authorization": f"Bearer {user_jwt_token}"},
    )


@pytest.mark.asyncio
async def test_agents_register_incative_agent_with_none_as_input_parameters(
    user_jwt_token: str,
    agent_factory: Callable[[], DummyAgent],
):
    dummy_agent = agent_factory()

    json_data = {
        "id": str(uuid.uuid4()),
        "name": dummy_agent.name,
        "description": dummy_agent.description,
        "input_parameters": None,
    }

    await http_client.post(
        path=AGENTS_REGISTER_ENDPOINT,
        json=json_data,
        expected_status_codes=[422],
        headers={"Authorization": f"Bearer {user_jwt_token}"},
    )
