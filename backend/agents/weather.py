import requests
import logging
from datetime import datetime
from typing import Dict, Optional
from ..config import settings
from ..utils.exceptions import WeatherAPIError

logger = logging.getLogger(__name__)

class WeatherAgent:
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = "http://api.weatherapi.com/v1"

    def get_forecast(self, city: str, date: str) -> Dict:
        """
        Get weather forecast for a specific city and date.
        
        Args:
            city (str): City name
            date (str): Date in YYYY-MM-DD format
            
        Returns:
            Dict: Weather forecast information
        """
        try:
            logger.info(f"Fetching weather forecast for {city} on {date}")
            
            # Convert date to required format
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            days_ahead = (parsed_date - datetime.now()).days
            
            # Make API request
            response = requests.get(
                f"{self.base_url}/forecast.json",
                params={
                    "key": self.api_key,
                    "q": city,
                    "days": max(1, days_ahead + 1),
                    "aqi": "no"
                }
            )
            
            if response.status_code != 200:
                raise WeatherAPIError(f"Weather API returned status code {response.status_code}")
            
            data = response.json()
            
            # Extract relevant forecast data
            forecast_day = data['forecast']['forecastday'][-1]['day']
            
            # Prepare recommendations based on weather conditions
            recommendations = self._generate_recommendations(forecast_day)
            
            return {
                "temperature": {
                    "max": forecast_day['maxtemp_c'],
                    "min": forecast_day['mintemp_c'],
                    "avg": forecast_day['avgtemp_c']
                },
                "conditions": forecast_day['condition']['text'],
                "precipitation_chance": forecast_day['daily_chance_of_rain'],
                "humidity": forecast_day['avghumidity'],
                "uv": forecast_day['uv'],
                "recommendations": recommendations
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            raise WeatherAPIError(f"Failed to fetch weather data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in weather forecast: {str(e)}")
            raise
    
    def _generate_recommendations(self, forecast: Dict) -> list:
        """Generate weather-based recommendations."""
        recommendations = []
        
        # Temperature-based recommendations
        if forecast['maxtemp_c'] > 30:
            recommendations.append("Bring sunscreen and stay hydrated")
        elif forecast['maxtemp_c'] < 10:
            recommendations.append("Bring warm clothing")
            
        # Rain-based recommendations
        if forecast['daily_chance_of_rain'] > 50:
            recommendations.append("Bring an umbrella")
            recommendations.append("Consider indoor backup activities")
            
        # UV-based recommendations
        if forecast['uv'] > 7:
            recommendations.append("Wear sun protection and seek shade during peak hours")
            
        # Time of day recommendations
        if abs(forecast['maxtemp_c'] - forecast['mintemp_c']) > 10:
            recommendations.append("Dress in layers for temperature changes throughout the day")
            
        return recommendations

    def get_hourly_forecast(self, city: str, date: str) -> Dict:
        """Get hourly weather forecast for better tour planning."""
        try:
            response = requests.get(
                f"{self.base_url}/forecast.json",
                params={
                    "key": self.api_key,
                    "q": city,
                    "days": 1,
                    "hour": 24
                }
            )
            
            if response.status_code != 200:
                raise WeatherAPIError(f"Weather API returned status code {response.status_code}")
            
            data = response.json()
            
            # Extract hourly forecast
            hourly_forecast = []
            for hour in data['forecast']['forecastday'][0]['hour']:
                hourly_forecast.append({
                    "time": hour['time'],
                    "temp_c": hour['temp_c'],
                    "condition": hour['condition']['text'],
                    "rain_chance": hour['chance_of_rain']
                })
                
            return {"hourly_forecast": hourly_forecast}
            
        except Exception as e:
            logger.error(f"Error fetching hourly forecast: {str(e)}")
            raise WeatherAPIError(f"Failed to fetch hourly forecast: {str(e)}")
