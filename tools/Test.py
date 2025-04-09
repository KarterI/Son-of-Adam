from smolagents import tool
from duckduckgo_search import DDGS  # Updated import
import pytz
import os
from datetime import datetime
from typing import Dict

@tool
def duckduckgo_search(query: str, max_results: int = 5) -> str:
    """Performs a web search using DuckDuckGo.
    
    Args:
        query: The search query string to look up.
        max_results: Maximum number of results to return (default: 5).
    
    Returns:
        A formatted string containing search results.
    """
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
            
            if not results:
                return "No results found"
            
            return "\n".join(
                f"{i}. {r['title']}\n   URL: {r['href']}\n   {r['body']}"
                for i, r in enumerate(results, 1)
            )
    except Exception as e:
        return f"Search error: {str(e)}"

# --- Tool Definitions (same as in your main agent) ---


@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """Gets current time in specified timezone.
    
    Args:
        timezone: A valid timezone (e.g. 'America/New_York').
    
    Returns:
        Formatted datetime string.
    """
    try:
        tz = pytz.timezone(timezone)
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return f"Error: {str(e)}"

@tool 
def google_maps_navigation(origin: str, destination: str) -> Dict:
    """Gets navigation directions using Google Maps API.
    
    Args:
        origin: Starting location.
        destination: Target location.
    
    Returns:
        Dictionary with route information.
    """
    try:
        # Mock response for testing
        return {
            "route": f"From {origin} to {destination}",
            "duration": "2 hours 15 mins",
            "distance": "120 km",
            "steps": ["Head north on Main St", "Turn right on 5th Ave"]
        }
    except Exception as e:
        return {"error": str(e)}

# --- Test Cases ---
def test_tools():
    """Run comprehensive tests on all tools"""
    print("\n=== Starting Tool Tests ===")
    
    # Test DuckDuckGo Search
    print("\n1. Testing DuckDuckGo Search:")
    search_results = duckduckgo_search('Python programming', max_results=2)
    print(search_results[:500] + "...")  # Show first 500 chars
    
    # Test Timezone
    print("\n2. Testing Timezone Tool:")
    time_str = get_current_time_in_timezone("Europe/Paris")
    print(f"Paris time: {time_str}")
    
    # Test Maps (mock)
    print("\n3. Testing Maps Navigation:")
    maps_result = google_maps_navigation("New York", "Boston")
    print(f"Route: {maps_result.get('route', 'Error')}")
    print(f"Steps: {maps_result.get('steps', [])[:2]}...")
    
    print("\n=== All Tests Completed ===")

# --- Main Execution ---
if __name__ == "__main__":
    # Verify environment variables
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        print("Warning: GOOGLE_MAPS_API_KEY not set (maps may fail)")
    
    # Run tests
    test_tools()
    
    # Keep terminal open to see results
    input("\nPress Enter to exit...")