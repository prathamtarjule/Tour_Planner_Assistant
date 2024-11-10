class TourPlannerException(Exception):
    """Base exception for Tour Planner application."""
    pass

class WeatherAPIError(TourPlannerException):
    """Raised when there's an error with the weather API."""
    pass

class NewsAPIError(TourPlannerException):
    """Raised when there's an error with the news API."""
    pass

class DatabaseError(TourPlannerException):
    """Raised when there's an error with the database operations."""
    pass

class AuthenticationError(TourPlannerException):
    """Raised when there's an authentication error."""
    pass

class ValidationError(TourPlannerException):
    """Raised when there's a validation error."""
    pass

class ExternalAPIError(TourPlannerException):
    """Raised when there's an error with external API calls."""
    pass
