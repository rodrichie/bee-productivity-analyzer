import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logging():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = log_dir / f'beebot_{timestamp}.log'

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # Set specific levels for different components
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # Create logger instance
    logger = logging.getLogger('beebot')
    logger.setLevel(logging.INFO)

    return logger

# Create function to log specific events
def log_event(logger, event_type: str, user_id: str, details: dict):
    """Log specific events with structured data"""
    log_data = {
        'event_type': event_type,
        'user_id': user_id,
        'timestamp': datetime.now().isoformat(),
        'details': details
    }
    logger.info(f'Event: {event_type} - User: {user_id} - Details: {details}')