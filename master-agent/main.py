import asyncio
from typing import Any, Optional

from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from agents import ReActMasterAgent
from config.settings import Settings
from llms import LLMFactory
from prompts import FILE_RELATED_SYSTEM_PROMPT
from utils.common import attach_files_to_message
from utils.tracing import AgentTracer

app_settings = Settings()

session = GenAISession(
    api_key=app_settings.MASTER_AGENT_API_KEY,
    ws_url=app_settings.ROUTER_WS_URL
)


@session.bind(name="MasterAgent", description="Master agent that orchestrates other agents")
async def receive_message(
        agent_context: GenAIContext,
        message: str,
        agents: list[dict[str, Any]],
        configs: dict[str, Any],
        files: Optional[list[dict[str, Any]]],
):
    graph_config = {"configurable": {"session": session}}
    output = {"is_success": False}

    tracer = AgentTracer()

    base_system_prompt = configs.get("llm", {}).get("system_prompt")

    system_prompt = f"{base_system_prompt}\n\n{FILE_RELATED_SYSTEM_PROMPT}"
    message = attach_files_to_message(message=message, files=files) if files else message

    init_messages = [SystemMessage(content=system_prompt), HumanMessage(content=message)]

    try:
        llm = LLMFactory.create(configs=configs.get("llm", {}))
        master_agent = ReActMasterAgent(model=llm, agents=agents, tracer=tracer)

        logger.info("Running Master Agent")

        final_state = await master_agent.graph.ainvoke(
            input={"messages": init_messages},
            config=graph_config
        )

        response = final_state["messages"][-1].content
        output["is_success"] = True
        logger.success("Master Agent run successfully")

    except Exception as e:
        response = f"An error occurred: {type(e).__name__} - {e}"
        logger.exception(response)

    return {"agents_trace": tracer.traces, "response": response, **output}


async def main():
    logger.info("Master Agent started")
    await session.process_events()


if __name__ == "__main__":
    asyncio.run(main())
