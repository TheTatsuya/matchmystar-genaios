import asyncio
from typing import Annotated, Optional
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkODBlNmJhNi00YjFhLTQzNjItYjBiNS1iOWJkNTQzZTA2OTIiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6IjIzYTEwZGRmLTk2NWMtNGEzMy05MmZkLWI4ZDNmMmJmMGQ1NiJ9.4fI7coEboFCHOOA1j5piaqvuedJVIPjPsKBbyOpGh3E" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)

@session.bind(
    name="results_formatter_agent",
    description=(
        "Receives a list of compatibility result dictionaries from kundli_match_agent and optionally a user profile. "
        "Formats and summarizes the matchmaking results for frontend display using actual astrological data. "
        "Input: compatibility_results (list of dicts from kundli_match_agent), user_profile (optional dict). "
        "Returns a summary dictionary with sorted matches, total_matches (int), best_match (dict), and analysis. "
        "Output: dict with keys 'matches' (list), 'total_matches' (int), 'best_match' (dict), 'analysis' (dict)."
    )
)
async def results_formatter_agent(
    agent_context: GenAIContext,
    compatibility_results: Annotated[list, "List of compatibility results from kundli_match_agent"],
    user_profile: Annotated[Optional[dict], "User profile details (optional)"] = None
):
    """
    Format and summarize matchmaking results using actual astrological data
    """
    formatted_matches = []
    
    for result in compatibility_results:
        match = result.get("match", {})
        compatibility = result.get("compatibility", {})
        
        # Calculate age if DOB is available
        age = 0
        if match.get("dob"):
            try:
                from datetime import datetime
                dob = datetime.strptime(match["dob"], "%Y-%m-%d")
                current_year = datetime.now().year
                age = current_year - dob.year
            except:
                age = 0
        
        # Get compatibility data
        compatibility_score = compatibility.get("compatibility_score", 0)
        message_type = compatibility.get("message_type", "neutral")
        
        # Use the message description from API response
        raw_response = compatibility.get("raw_response", {})
        message_data = raw_response.get("message", {})
        
        if isinstance(message_data, dict):
            message_description = message_data.get("description", "")
        else:
            message_description = compatibility.get("message", "")
            if isinstance(message_description, dict):
                message_description = message_description.get("description", "")
            elif not isinstance(message_description, str):
                message_description = ""
        
        # Get raw response for astrological details
        raw_response = compatibility.get("raw_response", {})
        
        # Create simple compatibility level
        compatibility_level = get_compatibility_level(compatibility_score, message_type)
        
        # Create enhanced match card with person details and compatibility
        formatted_match = {
            "id": match.get("id", ""),
            "name": match.get("name", "Unknown"),
            "age": age,
            "location": match.get("place", "Unknown"),
            "occupation": match.get("occupation", "Unknown"),
            "dob": match.get("dob", ""),
            "tob": match.get("tob", ""),
            "gender": match.get("gender", ""),
            "compatibility_score": compatibility_score,
            "compatibility_level": compatibility_level,
            "message_type": message_type,
            "message_description": message_description,
            "total_points": compatibility.get("total_points", 0),
            "maximum_points": compatibility.get("maximum_points", 36),
            "raw_response": raw_response,
            # Astrological details for display
            "astrological_details": extract_astrological_details(raw_response, match.get("gender", ""))
        }
        
        formatted_matches.append(formatted_match)
    
    # Sort by compatibility score (highest first)
    formatted_matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
    
    # Apply smart filtering logic
    filtered_matches = filter_best_matches(formatted_matches)
    
    # Analyze overall results
    analysis = analyze_compatibility_results(filtered_matches)
    
    return {
        "user_profile": user_profile,
        "matches": filtered_matches,
        "total_matches": len(filtered_matches),
        "best_match": filtered_matches[0] if filtered_matches else None,
        "analysis": analysis
    }

def filter_best_matches(matches: list) -> list:
    """Filter matches based on smart logic - return best matches only"""
    
    if not matches:
        return []
    
    # Separate matches by compatibility level
    good_matches = [m for m in matches if m["compatibility_score"] >= 70]
    moderate_matches = [m for m in matches if 50 <= m["compatibility_score"] < 70]
    low_matches = [m for m in matches if m["compatibility_score"] < 50]
    
    # If we have good matches, return top 5 good matches
    if good_matches:
        return good_matches[:5]
    
    # If we have moderate matches, return top 5 moderate matches
    if moderate_matches:
        return moderate_matches[:5]
    
    # If only low matches, return only the best one
    if low_matches:
        return [low_matches[0]]  # Return only the best low match
    
    return []

def extract_astrological_details(raw_response: dict, gender: str) -> dict:
    """Extract astrological details for display"""
    details = {}
    
    if not raw_response:
        return details
    
    # Get the person's info (girl_info or boy_info)
    person_key = "girl_info" if gender == "female" else "boy_info"
    person_info = raw_response.get(person_key, {})
    
    if person_info:
        # Nakshatra details
        nakshatra = person_info.get("nakshatra", {})
        if nakshatra:
            details["nakshatra"] = {
                "name": nakshatra.get("name", ""),
                "lord": nakshatra.get("lord", {}).get("name", ""),
                "pada": nakshatra.get("pada", "")
            }
        
        # Rashi details
        rashi = person_info.get("rasi", {})
        if rashi:
            details["rashi"] = {
                "name": rashi.get("name", ""),
                "lord": rashi.get("lord", {}).get("name", "")
            }
        
        # Koot details
        koot = person_info.get("koot", {})
        if koot:
            details["koot"] = {
                "varna": koot.get("varna", ""),
                "gana": koot.get("gana", ""),
                "nadi": koot.get("nadi", "")
            }
    
    return details

def get_compatibility_level(score: int, message_type: str) -> str:
    """Get simple compatibility level based on score and message type"""
    
    if message_type == "not-preferable":
        return "Not Recommended"
    elif score >= 70:
        return "Good Compatibility"
    elif score >= 50:
        return "Moderate Compatibility"
    else:
        return "Low Compatibility"

def analyze_compatibility_results(matches: list) -> dict:
    """Analyze overall compatibility results"""
    
    if not matches:
        return {
            "overall_assessment": "No matches found",
            "recommendation": "Try adjusting your search criteria or adding more profiles to the database.",
            "message": "We couldn't find any compatible matches in our database."
        }
    
    # Calculate statistics
    scores = [match["compatibility_score"] for match in matches]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    # Count by categories
    good_matches = len([m for m in matches if m["compatibility_score"] >= 70])
    moderate_matches = len([m for m in matches if 50 <= m["compatibility_score"] < 70])
    low_matches = len([m for m in matches if m["compatibility_score"] < 50])
    
    # Determine overall assessment and filtering message
    if good_matches > 0:
        overall_assessment = f"Found {good_matches} good match(es)"
        recommendation = "You have some compatible matches. Consider these top choices."
        filtering_message = f"Showing top {min(good_matches, 5)} good matches out of available profiles."
    elif moderate_matches > 0:
        overall_assessment = f"Found {moderate_matches} moderate match(es)"
        recommendation = "Some matches show potential. Consider consulting an astrologer for guidance."
        filtering_message = f"Showing top {min(moderate_matches, 5)} moderate matches out of available profiles."
    else:
        overall_assessment = "Limited compatibility found"
        recommendation = "The available matches have low compatibility. Consider consulting an astrologer."
        filtering_message = "Showing the best available match despite low compatibility."
    
    # Create analysis
    analysis = {
        "overall_assessment": overall_assessment,
        "recommendation": recommendation,
        "filtering_message": filtering_message,
        "statistics": {
            "total_matches": len(matches),
            "average_score": round(avg_score, 1),
            "highest_score": max_score,
            "lowest_score": min_score,
            "good_matches": good_matches,
            "moderate_matches": moderate_matches,
            "low_matches": low_matches
        },
        "message": generate_analysis_message(matches, avg_score, max_score)
    }
    
    return analysis

def generate_analysis_message(matches: list, avg_score: float, max_score: int) -> str:
    """Generate analysis message based on actual data"""
    
    if not matches:
        return "No matches were found in our database."
    
    if max_score >= 70:
        return f"Your best match has a {max_score}% compatibility score."
    elif max_score >= 50:
        return f"Your best match shows {max_score}% compatibility."
    else:
        return f"Your best match shows {max_score}% compatibility. Consider consulting an astrologer for guidance."

async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
