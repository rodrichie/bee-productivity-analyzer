import os
import google.generativeai as genai
from typing import Tuple, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BeeQueryClassifier:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Define query categories based on research findings
        self.categories = {
            'foraging': {
                'keywords': ['food', 'nectar', 'pollen', 'water', 'feeding', 'flowers', 'plants'],
                'description': 'Queries about bee foraging behavior and resources'
            },
            'hive_management': {
                'keywords': ['hive', 'placement', 'location', 'relocation', 'maintenance'],
                'description': 'Questions about hive placement and management'
            },
            'productivity': {
                'keywords': ['honey', 'yield', 'production', 'harvest', 'efficiency'],
                'description': 'Queries about honey production and hive productivity'
            },
            'environmental': {
                'keywords': ['weather', 'season', 'temperature', 'rain', 'drought'],
                'description': 'Questions about environmental factors affecting bees'
            },
            'health': {
                'keywords': ['disease', 'pests', 'competitors', 'parasites', 'health'],
                'description': 'Queries about bee health and threats'
            },
            'analysis': {
                'keywords': ['analyze', 'check', 'examine', 'photo', 'picture', 'image'],
                'description': 'Requests for analysis of images or data'
            }
        }

    def classify_query(self, query: str) -> Tuple[str, float]:
        """
        Classify a bee-related query into predefined categories.
        Returns category and confidence score.
        """
        try:
            classification_prompt = f"""
            Analyze this beekeeping query and classify it into one of these categories:
            
            Categories and their contexts:
            {self._format_categories()}
            
            Query: {query}
            
            Return a JSON-formatted response with:
            1. "category": The most appropriate category
            2. "confidence": Confidence score (0-1)
            3. "reasoning": Brief explanation for the classification
            """
            
            response = self.model.generate_content(classification_prompt)
            result = eval(response.text)  # Convert string response to dict
            
            return result['category'], result['confidence']
            
        except Exception as e:
            # Default to general foraging category if classification fails
            return 'foraging', 0.5

    def get_query_action_plan(self, query: str, category: str) -> Dict[str, Any]:
        """
        Generate an action plan for handling the classified query.
        """
        try:
            action_prompt = f"""
            Create an action plan for this beekeeping query:
            Query: {query}
            Category: {category}
            
            Consider:
            1. What specific information is needed to answer this query
            2. What research findings are relevant
            3. What practical advice should be included
            
            Return a JSON-formatted response with:
            1. "required_info": List of required information
            2. "research_points": Relevant research findings
            3. "advice_focus": Main points to address
            """
            
            response = self.model.generate_content(action_prompt)
            return eval(response.text)  # Convert string response to dict
            
        except Exception as e:
            return {
                "required_info": ["basic query information"],
                "research_points": ["general beekeeping practices"],
                "advice_focus": ["standard recommendations"]
            }

    def _format_categories(self) -> str:
        """Format categories and their descriptions for the prompt"""
        return "\n".join([
            f"{cat}: {details['description']} (Keywords: {', '.join(details['keywords'])})"
            for cat, details in self.categories.items()
        ])

    def is_image_analysis_required(self, query: str) -> bool:
        """
        Determine if the query requires image analysis.
        """
        image_related_keywords = [
            'photo', 'picture', 'image', 'show', 'look', 'check',
            'analyze', 'examine', 'see', 'visual', 'camera'
        ]
        return any(keyword in query.lower() for keyword in image_related_keywords)

    def get_specialized_prompt(self, category: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a specialized prompt based on query category and context.
        """
        context = context or {}
        
        prompts = {
            'foraging': """
                Analyze the foraging aspects considering:
                - Distance to water sources
                - Available flowering plants
                - Time of day
                - Weather conditions
                Provide specific recommendations for improving foraging efficiency.
                """,
            'hive_management': """
                Evaluate hive management practices focusing on:
                - Hive placement optimization
                - Maintenance requirements
                - Resource management
                - Seasonal adaptations
                Suggest practical improvements based on research findings.
                """,
            'productivity': """
                Assess productivity factors including:
                - Current yield metrics
                - Environmental conditions
                - Management practices
                - Resource availability
                Recommend specific actions to enhance productivity.
                """,
            'health': """
                Examine health considerations such as:
                - Common threats and diseases
                - Preventive measures
                - Treatment options
                - Environmental factors
                Provide evidence-based health management advice.
                """
        }
        
        base_prompt = prompts.get(category, """
            Analyze the query considering:
            - Best practices in beekeeping
            - Research findings
            - Practical implementation
            Provide specific, actionable recommendations.
        """)
        
        # Add context-specific information if available
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            base_prompt += f"\nAdditional Context:\n{context_str}"
        
        return base_prompt.strip()

# Example usage
if __name__ == "__main__":
    classifier = BeeQueryClassifier()
    
    # Test queries
    test_queries = [
        "How can I improve my bees' foraging?",
        "What's the best location for my hive?",
        "Can you check this photo of my hive?",
        "Why is my honey production low?",
        "How do I protect my bees from pests?"
    ]
    
    for query in test_queries:
        category, confidence = classifier.classify_query(query)
        print(f"\nQuery: {query}")
        print(f"Category: {category}")
        print(f"Confidence: {confidence:.2f}")
        
        if classifier.is_image_analysis_required(query):
            print("Image analysis required for this query")