from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool
import datetime
import requests
import pytz
import yaml
import os
from typing import Dict, List
from tools.final_answer import FinalAnswerTool
from Gradio_UI import GradioUI

# Below is an example of a tool that does nothing. Amaze us with your creativity !
@tool
def my_custom_tool(arg1:str, arg2:int)-> str: #it's import to specify the return type
    #Keep this format for the description / args / args description but feel free to modify the tool
    """A tool that does nothing yet 
    Args:
        arg1: the first argument
        arg2: the second argument
    """
    return "What magic will you build ?"

@tool
def duckduckgo_search(query: str, max_results: int = 5) -> str:
    """
    Perform a web search using DuckDuckGo.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default 5)
    
    Returns:
        A formatted string containing search results with titles, URLs and snippets
    """
    results = DuckDuckGoSearchTool().run(query, max_results=max_results)
    
    if not results:
        return "No results found"
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"{i}. {result['title']}\n"
            f"   URL: {result['href']}\n"
            f"   {result['body']}\n"
        )
    
    return "\n".join(formatted_results)


@tool
def google_maps_navigation(
    origin: str,
    destination: str,
    mode: str = "driving",
    avoid: str = None,
    departure_time: str = "now"
) -> Dict:
    """
    Get navigation directions using Google Maps API with traffic information.
    
    Args:
        origin: Starting address or coordinates (e.g., "New York, NY" or "40.7128,-74.0060")
        destination: Destination address or coordinates
        mode: Transportation mode (driving, walking, bicycling, transit)
        avoid: Route features to avoid (tolls, highways, ferries)
        departure_time: Either 'now' or a specific datetime in 'YYYY-MM-DDTHH:MM:SS' format
    
    Returns:
        Dictionary containing navigation information with traffic data
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "Google Maps API key not found in environment variables"}
    
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": api_key,
        "departure_time": departure_time if departure_time == "now" else None,
        "traffic_model": "best_guess"
    }
    
    if avoid:
        params["avoid"] = avoid
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if data["status"] != "OK":
            return {"error": f"Google Maps API error: {data.get('error_message', 'Unknown error')}"}
        
        route = data["routes"][0]
        legs = route["legs"][0]
        
        # Format the response for better readability
        steps = []
        for step in legs["steps"]:
            steps.append({
                "instruction": step["html_instructions"].replace('<b>', '').replace('</b>', ''),
                "distance": step["distance"]["text"],
                "duration": step["duration"]["text"]
            })
        
        result = {
            "summary": f"Route from {legs['start_address']} to {legs['end_address']}",
            "distance": legs["distance"]["text"],
            "duration": legs["duration"]["text"],
            "duration_in_traffic": legs.get("duration_in_traffic", {}).get("text", "N/A"),
            "steps": steps,
            "map_url": f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
        }
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to get directions: {str(e)}"}

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"


final_answer = FinalAnswerTool()

# If the agent does not answer, the model is overloaded, please use another model or the following Hugging Face Endpoint that also contains qwen2.5 coder:
# model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud' 

model = HfApiModel(
max_tokens=2096,
temperature=0.5,
model_id='Qwen/Qwen2.5-Coder-32B-Instruct',# it is possible that this model may be overloaded
custom_role_conversions=None,
)



# Import tool from Hub
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[final_answer], ## add your tools here (don't remove final answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)




GradioUI(agent).launch()