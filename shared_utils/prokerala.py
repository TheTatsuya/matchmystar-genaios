import os
import httpx
from datetime import datetime
from typing import Dict, Any

async def get_access_token():
    """Get OAuth2 access token from Prokerala"""
    try:
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "client_credentials",
                "client_id": os.getenv("PROKERALA_CLIENT_ID"),
                "client_secret": os.getenv("PROKERALA_CLIENT_SECRET")
            }
            response = await client.post("https://api.prokerala.com/token", data=data)
            return response.json()["access_token"]
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def format_dob_for_api(dob: str, tob: str) -> str:
    """Convert date and time to ISO 8601 format for Prokerala API"""
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
        return combined.strftime("%Y-%m-%dT%H:%M:%S+05:30")
    except Exception as e:
        print(f"Error formatting DOB: {e}")
        return f"{dob}T{tob}:00+05:30"

async def get_kundli_match(user_data: Dict[str, Any], candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get kundli matching using Prokerala API
    
    Args:
        user_data: Dict with 'dob', 'tob', 'lat', 'lon'
        candidate_data: Dict with 'dob', 'tob', 'lat', 'lon'
    
    Returns:
        Dict with compatibility analysis
    """
    try:
        token = await get_access_token()
        if not token:
            return {"error": "Failed to get access token"}
        
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
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            result = response.json()
            
            if result.get("status") == "ok":
                data = result.get("data", {})
                guna_milan = data.get("guna_milan", {})
                message = data.get("message", {})
                
                # Calculate compatibility score (out of 100)
                total_points = guna_milan.get("total_points", 0)
                max_points = guna_milan.get("maximum_points", 36)
                compatibility_score = int((total_points / max_points) * 100)
                
                return {
                    "compatibility_score": compatibility_score,
                    "total_points": total_points,
                    "maximum_points": max_points,
                    "message": message.get("description", ""),
                    "message_type": message.get("type", "neutral"),
                    "raw_response": data
                }
            else:
                return {
                    "error": f"API Error: {result.get('message', 'Unknown error')}",
                    "compatibility_score": 0
                }
                
    except Exception as e:
        print(f"Error in kundli matching: {e}")
        return {
            "error": f"Request failed: {str(e)}",
            "compatibility_score": 0
        }
