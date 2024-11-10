from typing import Dict, List, Optional
import openai
from datetime import datetime, timedelta
from config import settings

class ItineraryGenerationAgent:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def generate_itinerary(self, 
                          city: str,
                          date: str,
                          start_time: str,
                          end_time: str,
                          attractions: List[Dict],
                          starting_point: Optional[str] = None,
                          budget: Optional[float] = None) -> Dict:
        """Generate a complete itinerary based on user preferences and constraints."""
        
        # Create a prompt for the LLM to generate an optimized itinerary
        system_prompt = f"""
        Create an optimized itinerary for {city} on {date} from {start_time} to {end_time}.
        Starting point: {starting_point or 'First attraction'}
        Budget: ${budget if budget else 'Not specified'}
        
        Available attractions:
        {self._format_attractions(attractions)}
        
        Consider:
        1. Opening hours
        2. Travel time between locations
        3. Typical duration at each spot
        4. Budget constraints
        5. Optimal sequence to minimize travel time
        
        Provide a detailed schedule with:
        - Times for each activity
        - Travel methods and durations
        - Costs
        - Suggested meal breaks
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt}
            ]
        )
        
        return self._parse_itinerary(response.choices[0].message['content'])
    
    def adjust_itinerary(self, 
                        current_itinerary: Dict,
                        adjustment_type: str,
                        adjustment_details: Dict) -> Dict:
        """Adjust existing itinerary based on new constraints or preferences."""
        
        system_prompt = f"""
        Modify the following itinerary:
        {current_itinerary}
        
        Adjustment type: {adjustment_type}
        New requirements: {adjustment_details}
        
        Maintain the original schedule structure while accommodating the new requirements.
        Ensure all timing and sequence adjustments are logical and maintain the flow of the day.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt}
            ]
        )
        
        return self._parse_itinerary(response.choices[0].message['content'])
    
    def _format_attractions(self, attractions: List[Dict]) -> str:
        """Format attractions list for the prompt."""
        formatted = []
        for attraction in attractions:
            formatted.append(
                f"- {attraction['name']}\n"
                f"  Duration: {attraction['duration']}\n"
                f"  Cost: ${attraction['cost']}\n"
                f"  Category: {attraction['category']}\n"
            )
        return "\n".join(formatted)
    
    def _parse_itinerary(self, response: str) -> Dict:
        """Parse the LLM response into a structured itinerary format."""
        try:
            structuring_prompt = f"""
            Convert this itinerary into a structured Python dictionary with the following format:
            {{
                'schedule': [
                    {{
                        'time': 'start-end time',
                        'activity': 'name of activity',
                        'location': 'place name',
                        'duration': 'duration in minutes',
                        'travel_method': 'how to get there',
                        'travel_time': 'time in minutes',
                        'cost': 'cost in dollars'
                    }}
                ],
                'total_cost': 'total cost in dollars',
                'total_distance': 'total distance in km'
            }}
            
            Original itinerary:
            {response}
            """
            
            structured_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": structuring_prompt}]
            )
            
            return eval(structured_response.choices[0].message['content'])
        except Exception as e:
            return {"error": str(e)}
