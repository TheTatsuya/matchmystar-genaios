import json
from typing import Any

import jmespath
from genai_session.session import GenAISession
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from loguru import logger

from agents.base import BaseMasterAgent
from models.exceptions import AgentRunException, AgentNotFoundError
from models.states import ReActAgentState
from utils.common import bind_tools_safely
from utils.tracing import BaseTracer


class ReActMasterAgent(BaseMasterAgent):
    def __init__(self,
                 model: BaseChatModel,
                 agents: list[dict[str, Any]],
                 tracer: BaseTracer) -> None:
        """
        Supervisor agent building on top of ReAct framework to automatically execute available agents and flows.
        ReAct framework allows to continuously call tools (remote agents in this case) to complete task assigned by user.

        Args:
            model (BaseChatModel): Langchain chat model (preferably OpenAI or Azure OpenAI)
            agents (list[dict[str, Any]]): List of available agents
        """
        super().__init__(model, agents)
        # assign value of uuid field to title field
        # this retains compatibility with tool calling schema and prevents errors when two or more agents have the same name
        self._flows_to_bind_to_llm = [item["agent_input_schema"] for item in agents if "flow" in item]
        self._agents_to_bind_to_llm = [item["agent_input_schema"] for item in agents if "flow" not in item]
        self.agents_trace: list[dict[str, Any]] = []
        self.tracer = tracer
        self._is_flow_running = True

    async def select_agent(self, state: ReActAgentState):
        """
        Selects agent/flow to execute, determine input parameters for the agent/flow.
        Acts as main supervisor node.
        """
        messages = state.messages
        agents_queue = state.agents_queue

        if len(agents_queue) == 0:
            self._is_flow_running = True

            # if there are no next agent to execute, let the model decide
            model_with_flows = bind_tools_safely(self.model, self._flows_to_bind_to_llm)
            model_with_agents = bind_tools_safely(self.model, self._agents_to_bind_to_llm)

            response = await model_with_flows.ainvoke(messages)

            if response.tool_calls:
                self._is_flow_running = True
                flow_id = response.tool_calls[-1]["name"]
                flow_to_execute = jmespath.search(f"[?agent_id=='{flow_id}']", self.agents)[0]

                self.tracer.add_trace(
                    name="MasterAgent",
                    input=messages[-1].model_dump(),
                    output=response.model_dump(),
                    is_success=True
                )
                self.tracer.add_trace(id=flow_id, name=flow_to_execute["agent_name"])  # add initial tracing
            else:
                self._is_flow_running = False
                response = await model_with_agents.ainvoke(messages)

                self.tracer.add_trace(
                    name="MasterAgent",
                    input=messages[-1].model_dump(),
                    output=response.model_dump(),
                    is_success=True
                )

        else:
            self._is_flow_running = True

            # if we have next agent then we execute only this agent
            next_agent = jmespath.search(f"[?agent_id=='{agents_queue[0]}']", self.agents)[0]
            model_with_agent = bind_tools_safely(self.model, [next_agent["agent_input_schema"]], tool_choice="required")

            response = await model_with_agent.ainvoke(messages)

            self.tracer.add_subtrace(
                field_name="flow",
                name="MasterAgent",
                input=messages[-1].model_dump(),
                output=response.model_dump(),
                is_success=True
            )
        return {"messages": [response], "agent_queue": agents_queue}

    def should_continue(self, state: ReActAgentState):
        """
        Continues the flow if any agent/flow has been selected, ends the flow otherwise.
        """
        last_message = state.messages[-1]
        if last_message.tool_calls:
            return "create_flow"
        return END

    def create_flow(self, state: ReActAgentState):
        """
        Modifies queue of agents if any agent/flow has been selected by Supervisor.
        """
        agents_queue = state.agents_queue

        if len(agents_queue) == 0:
            agent_call = state.messages[-1].tool_calls[0]
            agent_name = agent_call['name']

            # search for agent/flow chosen by Supervisor and take the sequence of agents in the flow
            try:
                agent_flow_to_execute = jmespath.search(f"[?agent_id=='{agent_name}']",
                                                        data=self.agents)[0]
            except IndexError:
                raise AgentNotFoundError("Unable to find agent or flow to execute. "
                                         "Please check if the agent is registered or LLM returns correct agent name.")

            agents_queue = agent_flow_to_execute.get("flow") or [agent_flow_to_execute["agent_id"]]
        return {"agents_queue": agents_queue}

    async def execute_agent(self, state: ReActAgentState, config: RunnableConfig):
        """
        Calls remote agent selected by Supervisor using AIConnector library.
        """
        messages = state.messages
        agents_queue = state.agents_queue

        session: GenAISession | None = config.get("configurable", {}).get("session", None)

        agent_to_execute_id = agents_queue.pop(0)  # ID of the agent to execute
        agent_call = messages[-1].tool_calls[0]
        agent_call_args = agent_call["args"]
        agent_name = jmespath.search(f"[?agent_id=='{agent_to_execute_id}']",
                                     self.agents)[0]["agent_name"]

        logger.debug(f"Executing {agent_name} with ID {agent_to_execute_id}, args: {agent_call_args}")

        # call remote agent
        agent_response = await session.send(
            client_id=agent_to_execute_id,
            message=agent_call_args
        )

        tracing_data = {
            "id": agent_to_execute_id,
            "name": agent_name,
            "input": agent_call_args,
            "output": agent_response.response,
            "execution_time": agent_response.execution_time,
            "is_success": agent_response.is_success,
        }
        if self._is_flow_running:
            self.tracer.add_subtrace(
                field_name="flow",
                **tracing_data
            )
        else:
            self.tracer.add_trace(**tracing_data)

        if not agent_response.is_success:
            logger.error(f"Agent {agent_name} with ID {agent_to_execute_id} failed")
            raise AgentRunException(agent_response.response)

        logger.success(f"Agent {agent_name} with ID {agent_to_execute_id} executed successfully "
                       f"in {agent_response.execution_time:.2f} seconds")

        agent_call_message = ToolMessage(
                content=json.dumps(agent_response.response),
                name=agent_to_execute_id,
                tool_call_id=agent_call["id"],
            )
        return {"messages": [agent_call_message],
                "agents_queue": agents_queue}

    @property
    def graph(self) -> CompiledStateGraph:
        """
        Execution graph of Master Agent.
        """
        workflow = StateGraph(ReActAgentState)

        workflow.add_node("supervisor", self.select_agent)
        workflow.add_node("create_flow", self.create_flow)
        workflow.add_node("execute_agent", self.execute_agent)

        workflow.add_edge(START, "supervisor")
        workflow.add_conditional_edges("supervisor", self.should_continue, ["create_flow", END])
        workflow.add_edge("create_flow", "execute_agent")
        workflow.add_edge("execute_agent", "supervisor")

        compiled_graph = workflow.compile()
        return compiled_graph
