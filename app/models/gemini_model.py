import os
import google.generativeai as genai
from PIL import Image
import base64
import io
from typing import Optional, Union, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiHandler:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.text_model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        
        # Load bee knowledge base
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> dict:
        """Load bee-related knowledge from the research report"""
        return {
            "foraging_patterns": {
                "peak_times": "Early morning and late afternoon",
                "water_distance": "Optimal within 3km of hive",
                "feeding_methods": [
                    "Sugar mixed in water",
                    "Banana juice",
                    "Pineapple peelings",
                    "Cassava",
                    "Sugarcane peelings",
                    "Maize flour"
                ]
            },
            "productivity_factors": {
                "location": [
                    "Proximity to water",
                    "Availability of flowering plants",
                    "Protection from harsh weather"
                ],
                "management": [
                    "Regular monitoring",
                    "Supplementary feeding during scarcity",
                    "Protection from competitors"
                ]
            },
            "common_issues": {
                "environmental": ["Drought", "Bush fires", "Deforestation"],
                "pests": ["Beetles", "Ants", "Wax moths"],
                "management": ["Poor hive placement", "Inadequate feeding", "Lack of water"]
            }
        }

    def generate_response(self, query: str) -> str:
        """Generate a response using the text model"""
        try:
            # Enhance the query with context from knowledge base
            enhanced_query = f"""
            As a bee productivity expert, answer this query using the following knowledge:
            {self.knowledge_base}
            
            User Query: {query}
            
            Provide specific, actionable advice based on research findings.
            """
            
            response = self.text_model.generate_content(enhanced_query)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def analyze_image(self, image_data: Union[str, bytes], query: Optional[str] = None) -> str:
        """Analyze an image using the vision model"""
        try:
            # Handle base64 encoded images
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
                image_data = base64.b64decode(image_data)
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Prepare analysis prompt
            default_prompt = """
            Analyze this beekeeping image and provide:
            1. Assessment of bee activity and foraging conditions
            2. Identification of any visible issues or concerns
            3. Specific recommendations for improvement
            4. Potential impact on hive productivity
            
            Base your analysis on established beekeeping research and best practices.
            """
            
            prompt = query if query else default_prompt
            
            response = self.vision_model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Error analyzing image: {str(e)}"

    def get_foraging_advice(self, location: str, season: str) -> str:
        """Get specific foraging advice based on location and season"""
        try:
            query = f"""
            Provide specific foraging advice for:
            Location: {location}
            Season: {season}
            
            Consider:
            1. Optimal foraging times
            2. Water source recommendations
            3. Supplementary feeding needs
            4. Environmental considerations
            
            Base recommendations on the research findings in our knowledge base.
            """
            
            response = self.text_model.generate_content(query)
            return response.text
        except Exception as e:
            return f"Error generating foraging advice: {str(e)}"

    def analyze_productivity(self, metrics: dict) -> str:
        """Analyze hive productivity based on provided metrics"""
        try:
            metrics_str = "\n".join([f"{k}: {v}" for k, v in metrics.items()])
            query = f"""
            Analyze these hive productivity metrics:
            {metrics_str}
            
            Provide:
            1. Performance assessment
            2. Comparison with expected benchmarks
            3. Specific recommendations for improvement
            4. Potential issues to address
            
            Base analysis on research findings and best practices.
            """
            
            response = self.text_model.generate_content(query)
            return response.text
        except Exception as e:
            return f"Error analyzing productivity: {str(e)}"