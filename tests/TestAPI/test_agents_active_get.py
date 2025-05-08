from typing import Awaitable, Callable
import pytest
import asyncio

import logging
from tests.http_client.AsyncHTTPClient import AsyncHTTPClient
from genai_session.session import GenAISession
from tests.conftest import DummyAgent

ENDPOINT = "/api/agents/active"
http_client = AsyncHTTPClient(timeout=10)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "offset, limit, expected_active_connections",
    [(0, 1, 1), (0, 2, 1)],
    ids=[
        "valid offset less then limit, valid limit equals to active agents amount",
        "valid offset less then limit, valid limit above active agents amount",
    ],
)
async def test_active_agents_with_valid_limit_and_offset(
    offset,
    limit,
    expected_active_connections,
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

        params = {"offset": offset, "limit": limit}
        active_agents = await http_client.get(
            path=ENDPOINT,
            params=params,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_active_agents = {
            "count_active_connections": expected_active_connections,
            "active_connections": [
                {
                    "agent_id": session.agent_id,
                    "agent_name": dummy_agent.name,
                    "agent_description": dummy_agent.description,
                    "agent_input_schema": {
                        "type": "function",
                        "function": {
                            "name": session.agent_id,
                            "description": dummy_agent.description,
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                        },
                    },
                },
            ],
            **params,
        }

        assert active_agents == expected_active_agents

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            # logging.info("Background task has been properly cancelled.")
            pass


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "offset, limit, expected_active_connections",
    [(0, 0, 0)],
    ids=["valid offset equals to limit, limit less then active agents amount"],
)
async def test_active_agents_with_limit_less_then_active_agents_amount(
    offset,
    limit,
    expected_active_connections,
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

        params = {"offset": offset, "limit": limit}
        active_agents = await http_client.get(
            path=ENDPOINT,
            params=params,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_active_agents = {
            "count_active_connections": expected_active_connections,
            "active_connections": [],
            **params,
        }

        assert active_agents == expected_active_agents

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            # logging.info("Background task has been properly cancelled.")
            pass


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "offset, limit, expected_active_connections",
    [(1, 1, 0)],
    ids=["valid offset equals to limit and active agents amount"],
)
async def test_active_agents_with_offset_equal_to_active_agents_amount(
    offset,
    limit,
    expected_active_connections,
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

        params = {"offset": offset, "limit": limit}
        active_agents = await http_client.get(
            path=ENDPOINT,
            params=params,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_active_agents = {
            "count_active_connections": expected_active_connections,
            "active_connections": [],
            **params,
        }

        assert active_agents == expected_active_agents

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            # logging.info("Background task has been properly cancelled.")
            pass


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "offset, limit, expected_active_connections",
    [(1, 1, 1)],
    ids=["offset and limit are equal and less then active agents amount"],
)
async def test_active_agents_with_offset_and_limit_are_equal_and_less_then_active_agents_amount(
    offset,
    limit,
    expected_active_connections,
    user_jwt_token: str,
    agent_jwt_factory: Callable[[str], Awaitable[str]],
    agent_factory: Callable[[], DummyAgent],
):
    dummy_agent_1 = agent_factory()
    dummy_agent_2 = agent_factory()

    AUTH_JWT_1 = await agent_jwt_factory(user_jwt_token)
    AUTH_JWT_2 = await agent_jwt_factory(user_jwt_token)

    session_1 = GenAISession(jwt_token=AUTH_JWT_1)
    session_2 = GenAISession(jwt_token=AUTH_JWT_2)

    @session_1.bind(name=dummy_agent_1.name, description=dummy_agent_1.description)
    async def example_agent_1(agent_context=""):
        return True

    @session_2.bind(name=dummy_agent_2.name, description=dummy_agent_2.description)
    async def example_agent_2(agent_context=""):
        return False

    async def process_event_1():
        """Processes events for the GenAISession."""
        # logging.info(f"Agents with ID {AUTH_JWT_1} started")
        await session_1.process_events()

    async def process_event_2():
        """Processes events for the GenAISession."""
        # logging.info(f"Agents with ID {AUTH_JWT_2} started")
        await session_2.process_events()

    try:
        event_task_1 = asyncio.create_task(process_event_1())
        await asyncio.sleep(0.1)

        event_task_2 = asyncio.create_task(process_event_2())
        await asyncio.sleep(0.1)

        event_tasks = [event_task_1, event_task_2]

        params = {"offset": offset, "limit": limit}
        active_agents = await http_client.get(
            path=ENDPOINT,
            params=params,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_active_agents = {
            "count_active_connections": expected_active_connections,
            "active_connections": [
                {
                    "agent_id": session_2.agent_id,
                    "agent_name": dummy_agent_2.name,
                    "agent_description": dummy_agent_2.description,
                    "agent_input_schema": {
                        "type": "function",
                        "function": {
                            "name": session_2.agent_id,
                            "description": dummy_agent_2.description,
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                        },
                    },
                },
            ],
            **params,
        }

        assert active_agents == expected_active_agents

    finally:
        for task in event_tasks:
            task.cancel()

            try:
                await task

            except asyncio.CancelledError:
                # logging.info("Background task has been properly cancelled.")
                pass


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "offset, limit, expected_active_connections",
    [(0, 3, 2)],
    ids=["valid offset and valid limit above active agents amount"],
)
async def test_active_agents_offset_and_limit_above_active_agents_amount(
    offset,
    limit,
    expected_active_connections,
    user_jwt_token: str,
    agent_jwt_factory: Callable[[str], Awaitable[str]],
    agent_factory: Callable[[], DummyAgent],
):
    dummy_agent_1 = agent_factory()
    dummy_agent_2 = agent_factory()

    AUTH_JWT_1 = await agent_jwt_factory(user_jwt_token)
    AUTH_JWT_2 = await agent_jwt_factory(user_jwt_token)

    session_1 = GenAISession(jwt_token=AUTH_JWT_1)
    session_2 = GenAISession(jwt_token=AUTH_JWT_2)

    @session_1.bind(name=dummy_agent_1.name, description=dummy_agent_1.description)
    async def example_agent_1(agent_context=""):
        return True

    @session_2.bind(name=dummy_agent_2.name, description=dummy_agent_2.description)
    async def example_agent_2(agent_context=""):
        return False

    async def process_event_1():
        """Processes events for the GenAISession."""
        # logging.info(f"Agents with ID {AUTH_JWT_1} started")
        await asyncio.gather(session_1.process_events())

    async def process_event_2():
        """Processes events for the GenAISession."""
        # logging.info(f"Agents with ID {AUTH_JWT_2} started")
        await asyncio.gather(session_2.process_events())

    try:
        event_task_1 = asyncio.create_task(process_event_1())

        await asyncio.sleep(0.1)

        event_task_2 = asyncio.create_task(process_event_2())

        await asyncio.sleep(0.1)

        event_tasks = [event_task_1, event_task_2]

        params = {"offset": offset, "limit": limit}
        active_agents = await http_client.get(
            path=ENDPOINT,
            params=params,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_active_agents = {
            "count_active_connections": expected_active_connections,
            "active_connections": [
                {
                    "agent_id": session_1.agent_id,
                    "agent_name": dummy_agent_1.name,
                    "agent_description": dummy_agent_1.description,
                    "agent_input_schema": {
                        "type": "function",
                        "function": {
                            "name": session_1.agent_id,
                            "description": dummy_agent_1.description,
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                        },
                    },
                },
                {
                    "agent_id": session_2.agent_id,
                    "agent_name": dummy_agent_2.name,
                    "agent_description": dummy_agent_2.description,
                    "agent_input_schema": {
                        "type": "function",
                        "function": {
                            "name": session_2.agent_id,
                            "description": dummy_agent_2.description,
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                        },
                    },
                },
            ],
            **params,
        }

        assert active_agents == expected_active_agents

    finally:
        for task in event_tasks:
            task.cancel()

            try:
                await task

            except asyncio.CancelledError:
                # logging.info("Background task has been properly cancelled.")
                pass


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "offset, limit, expected_active_connections",
    [(0, 1, 0)],
    ids=["valid offset and valid limit with no active agents"],
)
async def test_active_agents_with_valid_offset_and_limit_and_no_active_agents(
    offset, limit, expected_active_connections, user_jwt_token: str
):
    await asyncio.sleep(3)

    params = {"offset": offset, "limit": limit}
    active_agents = await http_client.get(
        path=ENDPOINT,
        params=params,
        headers={"Authorization": f"Bearer {user_jwt_token}"},
    )

    expected_active_agents = {
        "count_active_connections": expected_active_connections,
        "active_connections": [],
        **params,
    }

    assert active_agents == expected_active_agents


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expected_active_connections",
    [1],
    ids=["default offset and limit with active agent"],
)
async def test_active_agents_with_default_offset_and_limit_with_active_agent(
    expected_active_connections,
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

        active_agents = await http_client.get(
            path=ENDPOINT,
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_active_agents = {
            "count_active_connections": expected_active_connections,
            "active_connections": [
                {
                    "agent_id": session.agent_id,
                    "agent_name": dummy_agent.name,
                    "agent_description": dummy_agent.description,
                    "agent_input_schema": {
                        "type": "function",
                        "function": {
                            "name": session.agent_id,
                            "description": dummy_agent.description,
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                        },
                    },
                }
            ],
            "limit": 100,
            "offset": 0,
        }

        assert active_agents == expected_active_agents

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            # logging.info("Background task has been properly cancelled.")
            pass


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "offset, limit, param, error_msg",
    [
        (
            0.1,
            1,
            "offset",
            "Input should be a valid integer, unable to parse string as an integer",
        ),
        (
            "zero",
            1,
            "offset",
            "Input should be a valid integer, unable to parse string as an integer",
        ),
        (
            "",
            1,
            "offset",
            "Input should be a valid integer, unable to parse string as an integer",
        ),
    ],
    ids=[
        "float offset",
        "string offset",
        "empty string offset",
    ],
)
async def test_active_agents_with_invalid_params_offset(
    offset,
    limit,
    param,
    error_msg,
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

        params = {"offset": offset, "limit": limit}
        respounse = await http_client.get(
            ENDPOINT,
            params=params,
            expected_status_codes=[422],
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_respounse = {
            "detail": [
                {
                    "type": "int_parsing",
                    "loc": ["query", f"{param}"],
                    "msg": f"{error_msg}",
                    "input": f"{offset}",
                }
            ]
        }

        assert respounse == expected_respounse

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            # logging.info("Background task has been properly cancelled.")
            pass


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "offset, limit, param, error_msg",
    [
        (
            1,
            0.1,
            "limit",
            "Input should be a valid integer, unable to parse string as an integer",
        ),
        (
            1,
            "one",
            "limit",
            "Input should be a valid integer, unable to parse string as an integer",
        ),
        (
            1,
            "",
            "limit",
            "Input should be a valid integer, unable to parse string as an integer",
        ),
    ],
    ids=[
        "float limit",
        "string limit",
        "empty string limit",
    ],
)
async def test_active_agents_with_invalid_params_limit(
    offset,
    limit,
    param,
    error_msg,
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

        params = {"offset": offset, "limit": limit}
        respounse = await http_client.get(
            ENDPOINT,
            params=params,
            expected_status_codes=[422],
            headers={"Authorization": f"Bearer {user_jwt_token}"},
        )

        expected_respounse = {
            "detail": [
                {
                    "type": "int_parsing",
                    "loc": ["query", f"{param}"],
                    "msg": f"{error_msg}",
                    "input": f"{limit}",
                }
            ]
        }

        assert respounse == expected_respounse

    finally:
        event_task.cancel()

        try:
            await event_task

        except asyncio.CancelledError:
            logging.info("Background task has been properly cancelled.")
