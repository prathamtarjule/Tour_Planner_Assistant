import requests
import logging
from typing import List, Dict
from datetime import datetime, timedelta
from ..config import settings
from ..utils.exceptions import NewsAPIError

logger = logging.getLogger(__name__)

class NewsAgent:
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"

    def get_news(self, city: str, days_ahead: int = 7) -> List[Dict]:
        """
        Get relevant news and events for a specific city.
        
        Args:
            city (str): City name
            days_ahead (int): Number of days to look ahead for events
            
        Returns:
            List[Dict]: List of news articles and events
        """
        try:
            logger.info(f"Fetching news for {city}")
            
            # Calculate date range
            end_date = datetime.now() + timedelta(days=days_ahead)
            
            # Make API request
            response = requests.get(
                f"{self.base_url}/everything",
                params={
                    "apiKey": self.api_key,
                    "q": f"{city} (event OR festival OR closure OR construction)",
                    "from": datetime.now().strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d"),
                    "language": "en",
                    "sortBy": "relevancy"
                }
            )
            
            if response.status_code != 200:
                raise NewsAPIError(f"News API returned status code {response.status_code}")
            
            data = response.json()
            
            # Process and filter relevant news
            relevant_news = self._process_news(data['articles'])
            
            return relevant_news
            
        except requests.RequestException as e:
            logger.error(f"Error fetching news data: {str(e)}")
            raise NewsAPIError(f"Failed to fetch news data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in news fetch: {str(e)}")
            raise

    def _process_news(self, articles: List[Dict]) -> List[Dict]:
        """Process and filter news articles for relevancy."""
        processed_news = []
        
        for article in articles:
            # Check if article is relevant to tourism
            if self._is_tourism_relevant(article['title'] + ' ' + article['description']):
                processed_news.append({
                    "title": article['title'],
                    "description": article['description'],
                    "date": article['publishedAt'],
                    "source": article['source']['name'],
                    "url": article['url'],
                    "impact_level": self._assess_impact_level(article['title'], article['description'])
                })
                
        return processed_news

    def _is_tourism_relevant(self, text: str) -> bool:
        """Check if the news is relevant to tourism."""
        tourism_keywords = [
            'tourist', 'visitor', 'attraction', 'museum', 'festival',
            'event', 'closure', 'construction', 'celebration', 'exhibition',
            'monument', 'landmark', 'traffic', 'transport', 'holiday'
        ]
        
        return any(keyword in text.lower() for keyword in tourism_keywords)

    def _assess_impact_level(self, title: str, description: str) -> str:
        """Assess the impact level of news on tourism."""
        high_impact_keywords = ['closure', 'cancelled', 'emergency', 'warning', 'strike']
        medium_impact_keywords = ['delay', 'changed', 'construction', 'maintenance']
        
        text = (title + ' ' + description).lower()
        
        if any(keyword in text for keyword in high_impact_keywords):
            return "high"
        elif any(keyword in text for keyword in medium_impact_keywords):
            return "medium"
        return "low"

    def get_events(self, city: str) -> List[Dict]:
        """Get upcoming events in the city."""
        try:
            # This could use a different API specifically for events
            # For example, Eventbrite API or similar
            logger.info(f"Fetching events for {city}")
            
            # Placeholder for event data
            # In a real implementation, you would integrate with an events API
            events = [
                {
                    "name": "Local Food Festival",
                    "date": "2024-01-01",
                    "location": "City Center",
                    "type": "Food & Culture"
                }
            ]
            
            return events
            
        except Exception as e:
            logger.error(f"Error fetching events: {str(e)}")
            raise
