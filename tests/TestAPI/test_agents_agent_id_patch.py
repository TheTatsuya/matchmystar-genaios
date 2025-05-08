from typing import Awaitable, Callable
import uuid
import pytest
import asyncio
import logging

from datetime import datetime
from tests.http_client.AsyncHTTPClient import AsyncHTTPClient
from genai_session.session import GenAISession
from tests.conftest import DummyAgent

ENDPOINT = "/api/agents/{agent_id}"

http_client = AsyncHTTPClient(timeout=10)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_parameters",
    [({"input_params": {"input_1": True}})],
    ids=[
        "patch agent with valid full request and assert result",
    ],
)
async def test_agents_patch_agent_valid_full_request_body(
    input_parameters,
    user_jwt_token: str,
    get_user: Callable[[str], Awaitable[str]],
    agent_jwt_factory: Callable[[str], Awaitable[str]],
    agent_factory: Callable[[], DummyAgent],
):
    dummy_agent = agent_factory()

    JWT_TOKEN = await agent_jwt_factory(user_jwt_token)

    session = GenAISession(jwt_token=JWT_TOKEN)
    user_id = await get_user(user_jwt_token)
    print(f"{user_id=}")

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
            "description": "New Agent Description",
            "input_parameters": input_parameters,
        }
        response = await http_client.patch(
            path=ENDPOINT.format(agent_id=session.agent_id),
            json=json_data,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_response = {
            "name": dummy_agent.name,
            "creator_id": await get_user(user_jwt_token),
            "input_parameters": input_parameters,
            "id": session.agent_id,
            "description": "New Agent Description",
            "is_active": True,
            "jwt": JWT_TOKEN,
        }

        created_at_str = response.pop("created_at")
        updated_at_str = response.pop("updated_at")
        last_invoked_at_str = response.pop("last_invoked_at")

        created_at = datetime.fromisoformat(created_at_str)
        updated_at = datetime.fromisoformat(updated_at_str)
        last_invoked_at = datetime.fromisoformat(last_invoked_at_str)

        assert updated_at > created_at
        assert last_invoked_at > created_at
        assert last_invoked_at >= updated_at

        assert response == expected_response

        agent = await http_client.get(
            path=ENDPOINT.format(agent_id=session.agent_id),
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        created_at_str = agent.pop("created_at")
        updated_at_str = agent.pop("updated_at")

        created_at = datetime.fromisoformat(created_at_str)
        updated_at = datetime.fromisoformat(updated_at_str)

        assert updated_at > created_at

        expected_agent = {
            "agent_id": session.agent_id,
            "agent_name": dummy_agent.name,
            "agent_description": "New Agent Description",
            "agent_input_schema": input_parameters,
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
@pytest.mark.parametrize(
    "values, raise_for_status",
    [
        ({"agent_description": None}, True),
    ],
    ids=[
        "patch agent with None description",
    ],
)
async def test_agents_patch_agent_description_is_none(
    values,
    raise_for_status,
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
            "agent_id": session.agent_id,
            "agent_name": dummy_agent.name,
            "agent_description": dummy_agent.description,
            "agent_input_schema": {},
            "agent_output_schema": {},
        }

        json_data = {**json_data, **values}

        response = await http_client.patch(
            path=ENDPOINT.format(agent_id=session.agent_id),
            json=json_data,
            expected_status_codes=[422],
            raise_for_status=raise_for_status,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        [key] = list(values.keys())
        [value] = list(values.values())

        expected_response = {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["body", "name"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": session.agent_id,
                        "agent_name": dummy_agent.name,
                        "agent_description": value,
                        "agent_input_schema": {},
                        "agent_output_schema": {},
                    },
                },
                {
                    "type": "missing",
                    "loc": ["body", "description"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": session.agent_id,
                        "agent_name": dummy_agent.name,
                        "agent_description": value,
                        "agent_input_schema": {},
                        "agent_output_schema": {},
                    },
                },
                {
                    "type": "missing",
                    "loc": ["body", "input_parameters"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": session.agent_id,
                        "agent_name": dummy_agent.name,
                        "agent_description": value,
                        "agent_input_schema": {},
                        "agent_output_schema": {},
                    },
                },
            ]
        }

        assert response == expected_response

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            logging.info("Background task has been properly cancelled.")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values, raise_for_status",
    [
        ({"agent_name": None}, True),
    ],
    ids=[
        "patch agent with None name",
    ],
)
async def test_agents_patch_agent_name_is_none(
    values,
    raise_for_status,
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
            "agent_id": session.agent_id,
            "agent_name": dummy_agent.name,
            "agent_description": dummy_agent.description,
            "agent_input_schema": {},
        }

        json_data = {**json_data, **values}

        response = await http_client.patch(
            path=ENDPOINT.format(agent_id=session.agent_id),
            json=json_data,
            expected_status_codes=[422],
            raise_for_status=raise_for_status,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        [key] = list(values.keys())
        [value] = list(values.values())

        expected_response = {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["body", "name"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": session.agent_id,
                        "agent_name": value,
                        "agent_description": dummy_agent.description,
                        "agent_input_schema": {},
                    },
                },
                {
                    "type": "missing",
                    "loc": ["body", "description"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": session.agent_id,
                        "agent_name": value,
                        "agent_description": dummy_agent.description,
                        "agent_input_schema": {},
                    },
                },
                {
                    "type": "missing",
                    "loc": ["body", "input_parameters"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": session.agent_id,
                        "agent_name": value,
                        "agent_description": dummy_agent.description,
                        "agent_input_schema": {},
                    },
                },
            ]
        }

        assert response == expected_response

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            logging.info("Background task has been properly cancelled.")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values, raise_for_status",
    [
        ({"agent_id": None}, False),
    ],
    ids=[
        "patch agent with None agent_id",
    ],
)
async def test_agents_patch_agent_id_with_none(
    values,
    raise_for_status,
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
            "agent_id": session.agent_id,
            "agent_name": dummy_agent.name,
            "agent_description": dummy_agent.description,
            "agent_input_schema": {},
        }

        json_data = {**json_data, **values}

        response = await http_client.patch(
            path=ENDPOINT.format(agent_id=session.agent_id),
            json=json_data,
            expected_status_codes=[422],
            raise_for_status=raise_for_status,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        [value] = list(values.values())

        expected_response = {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["body", "name"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": value,
                        "agent_name": dummy_agent.name,
                        "agent_description": dummy_agent.description,
                        "agent_input_schema": {},
                    },
                },
                {
                    "type": "missing",
                    "loc": ["body", "description"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": value,
                        "agent_name": dummy_agent.name,
                        "agent_description": dummy_agent.description,
                        "agent_input_schema": {},
                    },
                },
                {
                    "type": "missing",
                    "loc": ["body", "input_parameters"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": value,
                        "agent_name": dummy_agent.name,
                        "agent_description": dummy_agent.description,
                        "agent_input_schema": {},
                    },
                },
            ]
        }

        assert response == expected_response

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            logging.info("Background task has been properly cancelled.")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values, raise_for_status",
    [
        ({"agent_input_schema": None}, True),
    ],
    ids=[
        "patch agent with None input_parameters",
    ],
)
async def test_agents_patch_agent_with_non_input_parameters(
    values,
    raise_for_status,
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
            "agent_id": session.agent_id,
            "agent_name": dummy_agent.name,
            "agent_description": dummy_agent.description,
            "agent_input_schema": {},
        }

        json_data = {**json_data, **values}

        response = await http_client.patch(
            path=ENDPOINT.format(agent_id=session.agent_id),
            json=json_data,
            expected_status_codes=[422],
            raise_for_status=raise_for_status,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        [value] = list(values.values())

        expected_response = {
            "detail": [
                {
                    "type": "missing",
                    "loc": ["body", "name"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": session.agent_id,
                        "agent_name": dummy_agent.name,
                        "agent_description": dummy_agent.description,
                        "agent_input_schema": value,
                    },
                },
                {
                    "type": "missing",
                    "loc": ["body", "description"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": session.agent_id,
                        "agent_name": dummy_agent.name,
                        "agent_description": dummy_agent.description,
                        "agent_input_schema": value,
                    },
                },
                {
                    "type": "missing",
                    "loc": ["body", "input_parameters"],
                    "msg": "Field required",
                    "input": {
                        "agent_id": session.agent_id,
                        "agent_name": dummy_agent.name,
                        "agent_description": dummy_agent.description,
                        "agent_input_schema": value,
                    },
                },
            ]
        }

        assert response == expected_response

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            logging.info("Background task has been properly cancelled.")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "values, raise_for_status",
    [
        ({"agent_output_schema": None}, True),
    ],
    ids=[
        "patch agent with None output_parameters",
    ],
)
async def test_agents_patch_agent_with_output_parameters(
    values,
    raise_for_status,
    user_jwt_token: str,
    get_user: Callable[[str], Awaitable[str]],
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

        json_data = {**json_data, **values}

        response = await http_client.patch(
            path=ENDPOINT.format(agent_id=session.agent_id),
            json=json_data,
            raise_for_status=raise_for_status,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        [key] = list(values.keys())
        [value] = list(values.values())

        expected_response = {
            "name": dummy_agent.name,
            "creator_id": await get_user(user_jwt_token),
            "input_parameters": {},
            "id": session.agent_id,
            "description": dummy_agent.description,
            "jwt": JWT_TOKEN,
            "is_active": True,
        }

        created_at_str = response.pop("created_at")
        updated_at_str = response.pop("updated_at")
        last_invoked_at_str = response.pop("last_invoked_at")

        created_at = datetime.fromisoformat(created_at_str)
        updated_at = datetime.fromisoformat(updated_at_str)
        last_invoked_at = datetime.fromisoformat(last_invoked_at_str)

        assert updated_at > created_at
        assert last_invoked_at > created_at
        assert last_invoked_at >= updated_at

        assert response == expected_response

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            logging.info("Background task has been properly cancelled.")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id, name, description, input_parameters",
    [
        (
            str(uuid.uuid4()),
            "New Agent Name",
            "New Agent Description",
            {"input_params": {"input_1": True}},
        )
    ],
    ids=[
        "patch inactive agent with valid full request body",
    ],
)
async def test_agents_patch_agent_inactive_agent(
    id,
    name,
    description,
    input_parameters,
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
            "id": id,
            "name": name,
            "description": description,
            "input_parameters": input_parameters,
        }
        response = await http_client.patch(
            path=ENDPOINT.format(agent_id=id),
            json=json_data,
            expected_status_codes=[400],
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_response = {"detail": f"Object {id} was not found"}

        assert response == expected_response

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            logging.info("Background task has been properly cancelled.")
