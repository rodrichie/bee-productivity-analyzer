# Import all model components
from .gemini_model import GeminiHandler
from .classifier import BeeQueryClassifier

# Initialize global instances
gemini_handler = GeminiHandler()
bee_classifier = BeeQueryClassifier()

# Export for use in other modules
__all__ = ['gemini_handler', 'bee_classifier']