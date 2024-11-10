from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from agents.user_interaction import UserInteractionAgent
from agents.itinerary_generation import ItineraryGenerationAgent
from database.neo4j_client import Neo4jClient

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
user_agent = UserInteractionAgent()
itinerary_agent = ItineraryGenerationAgent()
db_client = Neo4jClient()

class UserInput(BaseModel):
    user_id: str
    message: str

class ItineraryRequest(BaseModel):
    user_id: str
    city: str
    date: str
    start_time: str
    end_time: str
    interests: List[str]
    budget: Optional[float]
    starting_point: Optional[str]

@app.post("/process-input")
async def process_input(user_input: UserInput):
    """Process initial user input and extract relevant information."""
    try:
        extracted_info = user_agent.process_initial_input(
            user_input.user_id,
            user_input.message
        )
        print('extracted info:', extracted_info)
        return {"status": "success", "data": extracted_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-itinerary")
async def generate_itinerary(request: ItineraryRequest):
    """Generate a complete itinerary based on user preferences."""
    try:
        # Get suggested attractions based on interests
        attractions = user_agent.suggest_attractions(
            request.city,
            request.interests
        )
        
        # Generate itinerary
        itinerary = itinerary_agent.generate_itinerary(
            city=request.city,
            date=request.date,
            start_time=request.start_time,
            end_time=request.end_time,
            attractions=attractions,
            starting_point=request.starting_point,
            budget=request.budget
        )
        
        # Store the itinerary in the database
        place_names = [stop['location'] for stop in itinerary['schedule']]
        db_client.store_itinerary(request.user_id, request.city, place_names)
        
        return {"status": "success", "data": itinerary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class ItineraryAdjustment(BaseModel):
    user_id: str
    current_itinerary: Dict
    adjustment_type: str
    adjustment_details: Dict

class WeatherRequest(BaseModel):
    city: str
    date: str

class UserPreferences(BaseModel):
    user_id: str

@app.post("/adjust-itinerary")
async def adjust_itinerary(request: ItineraryAdjustment):
    """Adjust existing itinerary based on new requirements."""
    try:
        adjusted_itinerary = itinerary_agent.adjust_itinerary(
            current_itinerary=request.current_itinerary,
            adjustment_type=request.adjustment_type,
            adjustment_details=request.adjustment_details
        )
        return {"status": "success", "data": adjusted_itinerary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather")
async def get_weather(city: str, date: str):
    """Get weather forecast for the specified city and date."""
    try:
        from .agents.weather import WeatherAgent
        weather_agent = WeatherAgent()
        forecast = weather_agent.get_forecast(city, date)
        return {"status": "success", "data": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news")
async def get_news(city: str):
    """Get relevant news and events for the specified city."""
    try:
        from .agents.news import NewsAgent
        news_agent = NewsAgent()
        news = news_agent.get_news(city)
        return {"status": "success", "data": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get stored preferences for a specific user."""
    try:
        preferences = db_client.get_user_preferences(user_id)
        return {"status": "success", "data": preferences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-history/{user_id}")
async def get_user_history(user_id: str):
    """Get previous itineraries and preferences for a user."""
    try:
        history = db_client.get_user_history(user_id)
        return {"status": "success", "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
