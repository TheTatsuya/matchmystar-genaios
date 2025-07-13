import asyncio
import os
import supabase
import logging
from typing import List, Dict, Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

AGENT_JWT = os.environ.get("FILTER_PROFILE_AGENT_JWT", "")
session = GenAISession(jwt_token=AGENT_JWT)

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

logger.info(f"SUPABASE_URL: {SUPABASE_URL}")
logger.info(f"SUPABASE_KEY: {'*' * 10 if SUPABASE_KEY else 'NOT SET'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL or SUPABASE_KEY not found in environment variables!")
else:
    try:
        supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client created successfully")
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        supabase_client = None

def get_profiles(opposite_gender: str) -> List[Dict]:
    logger.info(f"Fetching profiles for gender: {opposite_gender}")
    
    if not supabase_client:
        logger.error("Supabase client not available")
        return []
    
    try:
        # First, let's check ALL profiles to see what's in the database
        logger.info("Checking ALL profiles in database...")
        all_profiles_response = supabase_client.table('profiles').select('*').execute()
        logger.info(f"Total profiles in database: {len(all_profiles_response.data) if all_profiles_response.data else 0}")
        
        if all_profiles_response.data:
            for i, profile in enumerate(all_profiles_response.data):
                logger.info(f"Profile {i+1}: {profile}")
        
        # Now try the specific gender query
        logger.info(f"Executing Supabase query for gender: '{opposite_gender}'")
        response = supabase_client.table('profiles').select('*').eq('gender', opposite_gender).execute()
        logger.info(f"Supabase response: {response}")
        logger.info(f"Found {len(response.data) if response.data else 0} profiles with gender '{opposite_gender}'")
        
        if response.data:
            logger.info(f"Sample profile: {response.data[0] if response.data else 'No data'}")
        
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error fetching profiles from Supabase: {e}")
        return []

@session.bind(
    name="filter_profile_agent",
    description=(
        "Receives a user profile dictionary with fields including 'lat' (float), 'lon' (float), 'gender' (str), etc. "
        "Returns a filtered list of candidate profile dictionaries, each with fields like 'name', 'dob', 'tob', 'place', 'gender', 'occupation', 'lat', 'lon'. "
        "Input: user_profile (dict with 'lat', 'lon', 'gender', ...). "
        "Output: candidates (list of dicts, each a candidate profile, e.g., [{'name': 'Priya', 'dob': '1995-02-02', ...}, ...])."
    )
)
async def filter_profile_agent(
    agent_context: GenAIContext,
    user_profile: Annotated[dict, "User profile with lat, lon, gender, etc."]
):
    logger.info(f"filter_profile_agent called with user_profile: {user_profile}")
    
    user_gender = user_profile.get('gender')
    logger.info(f"User gender: {user_gender}")
    
    if user_gender not in ('male', 'female'):
        logger.error(f"Invalid gender: {user_gender}")
        return {"error": "User gender must be 'male' or 'female'"}
    
    opposite_gender = 'female' if user_gender == 'male' else 'male'
    logger.info(f"Looking for profiles with gender: {opposite_gender}")
    
    matches = get_profiles(opposite_gender)
    logger.info(f"Returning {len(matches)} matches")
    
    return matches

async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
