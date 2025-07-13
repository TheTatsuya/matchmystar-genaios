import os
import httpx
import logging
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try multiple possible paths for the .env file
env_paths = [
    ".env",  # Current directory
    "genai-agentos/.env",  # From project root
    "../.env",  # From shared_utils directory
    "../../.env",  # From agents directory
]

for env_path in env_paths:
    if os.path.exists(env_path):
        logger.info(f"Loading .env from: {env_path}")
        load_dotenv(dotenv_path=env_path)
        break
else:
    # If no .env file found, try loading from current directory
    logger.warning("No .env file found in expected paths, trying current directory")
    load_dotenv()

async def get_access_token():
    """Get OAuth2 access token from Prokerala"""
    logger.info("Attempting to get Prokerala access token...")
    try:
        client_id = os.getenv("PROKERALA_CLIENT_ID")
        client_secret = os.getenv("PROKERALA_CLIENT_SECRET")
        
        logger.info(f"PROKERALA_CLIENT_ID: {'*' * 10 if client_id else 'NOT SET'}")
        logger.info(f"PROKERALA_CLIENT_SECRET: {'*' * 10 if client_secret else 'NOT SET'}")
        
        if not client_id or not client_secret:
            logger.error("PROKERALA_CLIENT_ID or PROKERALA_CLIENT_SECRET not found in environment variables!")
            return None
        
        logger.info("Making token request to Prokerala API...")
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            }
            response = await client.post("https://api.prokerala.com/token", data=data)
            result = response.json()
            logger.info(f"Token response status: {response.status_code}")
            logger.info(f"Token response: {result}")
            
            access_token = result.get("access_token")
            if access_token:
                logger.info("Successfully obtained access token")
            else:
                logger.error("No access token in response")
            return access_token
    except Exception as e:
        logger.error(f"Error getting access token: {e}")
        return None

def format_dob_for_api(dob: str, tob: str) -> str:
    """Convert date and time to ISO 8601 format for Prokerala API"""
    logger.info(f"Formatting DOB: {dob} {tob}")
    try:
        # Parse date and time
        date_obj = datetime.strptime(dob, "%Y-%m-%d")
        time_obj = datetime.strptime(tob, "%H:%M")
        
        # Combine date and time
        combined = date_obj.replace(
            hour=time_obj.hour,
            minute=time_obj.minute,
            second=0,
            microsecond=0
        )
        
        # Format as ISO 8601 with timezone
        formatted = combined.strftime("%Y-%m-%dT%H:%M:%S+05:30")
        logger.info(f"Formatted DOB: {formatted}")
        return formatted
    except Exception as e:
        logger.error(f"Error formatting DOB: {e}")
        fallback = f"{dob}T{tob}:00+05:30"
        logger.info(f"Using fallback format: {fallback}")
        return fallback

async def get_kundli_match(user_data: Dict[str, Any], candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get kundli matching using Prokerala API
    
    Args:
        user_data: Dict with 'dob', 'tob', 'lat', 'lon'
        candidate_data: Dict with 'dob', 'tob', 'lat', 'lon'
    
    Returns:
        Dict with compatibility analysis
    """
    logger.info("Starting kundli matching process...")
    logger.info(f"User data: {user_data}")
    logger.info(f"Candidate data: {candidate_data}")
    
    try:
        token = await get_access_token()
        if not token:
            logger.error("Failed to get access token for kundli matching")
            return {"error": "Failed to get access token"}
        
        logger.info("Got access token, making kundli matching request...")
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api.prokerala.com/v2/astrology/kundli-matching"
        
        # Format dates for API
        user_dob = format_dob_for_api(user_data["dob"], user_data["tob"])
        candidate_dob = format_dob_for_api(candidate_data["dob"], candidate_data["tob"])
        
        params = {
            "ayanamsa": 1,  # Lahiri ayanamsa
            "boy_dob": user_dob,
            "boy_coordinates": f"{user_data['lat']},{user_data['lon']}",
            "girl_dob": candidate_dob,
            "girl_coordinates": f"{candidate_data['lat']},{candidate_data['lon']}",
            "la": "en"
        }
        
        logger.info(f"Making API request to: {url}")
        logger.info(f"Request params: {params}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            logger.info(f"API response status: {response.status_code}")
            
            result = response.json()
            logger.info(f"API response: {result}")
            
            if result.get("status") == "ok":
                data = result.get("data", {})
                guna_milan = data.get("guna_milan", {})
                message = data.get("message", {})
                
                # Calculate compatibility score (out of 100)
                total_points = guna_milan.get("total_points", 0)
                max_points = guna_milan.get("maximum_points", 36)
                compatibility_score = int((total_points / max_points) * 100)
                
                logger.info(f"Kundli match results - Total points: {total_points}, Max points: {max_points}, Compatibility: {compatibility_score}%")
                
                return {
                    "compatibility_score": compatibility_score,
                    "total_points": total_points,
                    "maximum_points": max_points,
                    "message": message.get("description", ""),
                    "message_type": message.get("type", "neutral"),
                    "raw_response": data
                }
            else:
                error_msg = f"API Error: {result.get('message', 'Unknown error')}"
                logger.error(error_msg)
                return {
                    "error": error_msg,
                    "compatibility_score": 0
                }
                
    except Exception as e:
        logger.error(f"Error in kundli matching: {e}")
        return {
            "error": f"Request failed: {str(e)}",
            "compatibility_score": 0
        }
