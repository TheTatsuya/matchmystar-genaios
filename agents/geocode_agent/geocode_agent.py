import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from dotenv import load_dotenv
import os
import supabase
import logging

load_dotenv()

AGENT_JWT = os.environ.get("GEOCODE_AGENT_JWT", "")
session = GenAISession(jwt_token=AGENT_JWT)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


@session.bind(
    name="geocode_agent",
    description=(
        "Receives a user profile dictionary with at least a 'place' field (e.g., 'place': 'Chennai, India'). "
        "Returns a new user profile dictionary with the same fields as input, plus 'lat' (float, e.g., 13.0827) and 'lon' (float, e.g., 80.2707) fields added. "
        "Input: user_profile (dict with at least 'place', e.g., {'place': 'Chennai, India', ...}). "
        "Output: user_profile (dict with all input fields plus 'lat' and 'lon', e.g., {'place': 'Chennai, India', 'lat': 13.0827, 'lon': 80.2707, ...})."
    )
)
async def geocode_agent(
    agent_context: GenAIContext,
    user_profile: Annotated[dict, "User profile with place, dob, etc."]
):
    place = user_profile.get("place", "")
    """
    Get coordinates from place name using OpenStreetMap Nominatim API
    """
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("https://nominatim.openstreetmap.org/search", params={
                "q": place,
                "format": "json",
                "limit": 1
            })
            data = response.json()
            if data:
                lat, lon = data[0]["lat"], data[0]["lon"]
                enriched_profile = user_profile.copy()
                enriched_profile["lat"] = lat
                enriched_profile["lon"] = lon

                # Insert into Supabase if not already present
                try:
                    if SUPABASE_URL and SUPABASE_KEY:
                        supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
                        # Check for existing user by name, place, dob, tob
                        query = supabase_client.table("profiles") \
                            .select("id") \
                            .eq("name", enriched_profile.get("name")) \
                            .eq("place", enriched_profile.get("place")) \
                            .eq("dob", enriched_profile.get("dob")) \
                            .eq("tob", enriched_profile.get("tob")) \
                            .execute()
                        if not query.data:
                            supabase_client.table("profiles").insert([enriched_profile]).execute()
                except Exception:
                    # Log error without exposing sensitive info
                    import logging
                    logging.warning("Supabase insert skipped or failed.")

                return enriched_profile
            else:
                return {"error": f"No coordinates found for {place}"}
    except Exception as e:
        return {"error": f"Geocoding failed: {str(e)}"}


async def main():
    logging.info("Geocode agent started.")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
