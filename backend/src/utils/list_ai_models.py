import aiohttp

from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from logging import getLogger

from src.schemas.utils.openai import OpenAIListModelsDTO
from src.core.settings import get_settings

logger = getLogger(__name__)
settings = get_settings()
T = TypeVar("T", bound=BaseModel)


class AIOHTTPClient:
    async def _get(
        self,
        session: aiohttp.ClientSession,
        url: str,
        parse_as: Optional[Type[T]] = None,
    ):
        async with session.get(url) as response:
            if parse_as and response.status < 300:
                resp = await response.json()
                return parse_as(**resp)
            # raw response as the response with the error might not be castable to json
            return response


async def list_openai_models() -> Optional[list[Optional[str]]]:
    openai_key = settings.OPENAI_API_KEY
    if not openai_key:
        logger.warning(
            "OPENAI_API_KEY environment variable is not set, defaulting to a '[]' in the response"
        )
        return

    http_client = AIOHTTPClient()

    async with aiohttp.ClientSession(
        headers={"Authorization": f"Bearer {openai_key}"}
    ) as session:
        response = await http_client._get(
            session,
            url="https://api.openai.com/v1/models",
            parse_as=OpenAIListModelsDTO,
        )
        if isinstance(response, OpenAIListModelsDTO):
            return response.get_model_names()

        logger.error(
            f"Request to list OpenAI models failed. Details: status_code: {response.status} - {response.text()}"
        )
        return
