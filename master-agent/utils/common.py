from typing import Any
import json

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama


def attach_files_to_message(message: str, files: list[dict[str, Any]]):
    str_formatted_files = json.dumps(files)
    formatted_message = f"{message}\n\nFILES:\n{str_formatted_files}"
    return formatted_message


def bind_tools_safely(model: BaseChatModel, tools: list[dict[str, Any]], **kwargs):
    if isinstance(model, ChatOllama):
        return model.bind_tools(tools, **kwargs)
    return model.bind_tools(tools, parallel_tool_calls=False, **kwargs)
