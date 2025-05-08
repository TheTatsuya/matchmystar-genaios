from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # App settings
    ROUTER_WS_URL: str = Field(default="ws://router:8080/ws", alias="ROUTER_WS_URL")
    MASTER_AGENT_API_KEY: str = Field(
        default="e1adc3d8-fca1-40b2-b90a-7b48290f2d6a::master_server_ml",
        alias="MASTER_AGENT_API_KEY",
    )
