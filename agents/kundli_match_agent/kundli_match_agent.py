import asyncio
import sys
import os
from typing import Annotated, List, Dict, Any
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from dotenv import load_dotenv
import logging

# Add the current directory to the path so we can import prokerala
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_utils'))
from prokerala import get_kundli_match

load_dotenv()

AGENT_JWT = os.environ.get("KUNDLI_MATCH_AGENT_JWT", "")
session = GenAISession(jwt_token=AGENT_JWT)

@session.bind(
    name="kundli_match_agent",
    description=(
        "For each candidate profile, calculate kundli compatibility with the user profile using Prokerala API."
        "Receives a user profile dictionary and a list of candidate profile dictionaries. "
        "Input: user_profile (dict with 'name', 'dob', 'tob', 'place', 'gender', 'occupation', 'lat', 'lon', ...), candidates (list of dicts, each a candidate profile). "
        "Returns a list of match result dictionaries, each with 'match' (candidate profile dict) and 'compatibility' (dict with 'compatibility_score', 'summary', etc.). "
        "Output: list of dicts, e.g., [{'match': {...}, 'compatibility': {...}}, ...]."
    )
)
async def kundli_match_agent(
    agent_context: GenAIContext,
    user_profile: Annotated[dict, "User profile details (with dob, tob, lat, lon, etc.)"],
    candidates: Annotated[List[Dict[str, Any]], "List of candidate profiles to match against"]
):
    """
    For each candidate profile, calculate kundli compatibility with the user profile using Prokerala API.
    Returns a list of dicts: {match: <candidate_profile>, compatibility: <compatibility_result>}
    """
    results = []
    for candidate in candidates:
        user_data = {
            "dob": user_profile.get("dob"),
            "tob": user_profile.get("tob"),
            "lat": user_profile.get("lat"),
            "lon": user_profile.get("lon")
        }
        match_data = {
            "dob": candidate.get("dob"),
            "tob": candidate.get("tob"),
            "lat": candidate.get("lat"),
            "lon": candidate.get("lon")
        }
        try:
            compatibility_result = await get_kundli_match(user_data, match_data)
            if "error" in compatibility_result:
                compatibility = {
                    "compatibility_score": 0,
                    "summary": f"Error: {compatibility_result['error']}",
                    "message_type": "error"
                }
            else:
                compatibility = {
                    "compatibility_score": compatibility_result.get("compatibility_score", 0),
                    "total_points": compatibility_result.get("total_points", 0),
                    "maximum_points": compatibility_result.get("maximum_points", 36),
                    "summary": compatibility_result.get("message", "Compatibility analysis completed"),
                    "message_type": compatibility_result.get("message_type", "neutral"),
                    "raw_response": compatibility_result.get("raw_response", {})
                }
        except Exception as e:
            compatibility = {
                "compatibility_score": 0,
                "total_points": 0,
                "maximum_points": 36,
                "summary": f"Error: {str(e)}",
                "message_type": "error"
            }
        results.append({"match": candidate, "compatibility": compatibility})
    return results

async def main():
    logging.info("Kundli matching agent started.")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
