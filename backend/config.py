from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    OPENAI_API_KEY: str = "your-api-key"
    WEATHER_API_KEY: str = "your-weather-api-key"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
