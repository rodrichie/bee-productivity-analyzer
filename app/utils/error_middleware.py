from functools import wraps
from typing import Callable, Any, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BeeAnalysisError(Exception):
    """Base exception class for bee analysis errors"""
    def __init__(self, message: str, error_type: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

class MediaProcessingError(BeeAnalysisError):
    """Exception for media processing failures"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "MediaProcessingError", details)

class AnalysisError(BeeAnalysisError):
    """Exception for analysis failures"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "AnalysisError", details)

def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors in socket events"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BeeAnalysisError as e:
            logger.error(f"{e.error_type}: {str(e)}", extra={
                'error_details': e.details,
                'timestamp': e.timestamp
            })
            return {
                'status': 'error',
                'type': e.error_type,
                'message': str(e),
                'details': e.details,
                'timestamp': e.timestamp
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'type': 'UnexpectedError',
                'message': 'An unexpected error occurred',
                'timestamp': datetime.now().isoformat()
            }
    return wrapper