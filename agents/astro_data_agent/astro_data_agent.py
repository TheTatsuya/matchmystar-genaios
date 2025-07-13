import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
import os
from dotenv import load_dotenv

load_dotenv()

# If AGENT_JWT is present, replace with os.environ.get usage
AGENT_JWT = os.environ.get("ASTRO_DATA_AGENT_JWT", "")
session = GenAISession(jwt_token=AGENT_JWT)

@session.bind(
    name="astro_data_agent",
    description=(
        "Receives a user profile dictionary from the frontend with the following fields: 'name' (str), 'dob' (str, e.g., '2000-01-01'), 'tob' (str, e.g., '06:00'), 'place' (str, e.g., 'Chennai, India'), 'gender' (str), 'occupation' (str). "
        "Returns the same user profile dictionary as output. "
        "Input: user_profile (dict with 'name', 'dob', 'tob', 'place', 'gender', 'occupation'). "
        "Output: user_profile (dict with the same fields as input)."
    )
)
async def astro_data_agent(
    agent_context: GenAIContext,
    user_profile: Annotated[dict, "User profile with name, dob, tob, place, gender, occupation"]
):
    # Just return the profile as-is, or with a placeholder for lat/lon
    return user_profile

async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
