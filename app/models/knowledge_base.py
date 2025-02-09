from typing import Dict, Any, List
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BeekeepingKnowledgeBase:
    def __init__(self):
        self.knowledge_base = {
            "foraging_patterns": {
                "peak_times": {
                    "morning": "Early morning hours",
                    "afternoon": "Late afternoon",
                    "seasonal_variations": True
                },
                "distance_metrics": {
                    "optimal_water_distance": 3,  # in kilometers
                    "max_foraging_range": 5,  # in kilometers
                    "preferred_range": 2  # in kilometers
                },
                "environmental_factors": {
                    "temperature": {
                        "optimal_range": {
                            "min": 20,  # in Celsius
                            "max": 35
                        },
                        "critical_points": {
                            "too_cold": 10,
                            "too_hot": 40
                        }
                    },
                    "weather_conditions": [
                        "clear_sky",
                        "partial_clouds",
                        "light_wind",
                        "no_rain"
                    ]
                }
            },
            "hive_management": {
                "placement_criteria": {
                    "distance_from_water": {
                        "minimum": 100,  # in meters
                        "maximum": 3000  # in meters
                    },
                    "shade_requirements": {
                        "morning_sun": True,
                        "afternoon_shade": True,
                        "protection_from_elements": True
                    },
                    "orientation": {
                        "preferred": "southeast",
                        "alternatives": ["east", "south"],
                        "avoid": ["north", "northwest"]
                    }
                },
                "supplementary_feeding": {
                    "methods": [
                        {
                            "type": "sugar_syrup",
                            "ratio": "1:1",
                            "season": "spring"
                        },
                        {
                            "type": "sugar_syrup",
                            "ratio": "2:1",
                            "season": "fall"
                        },
                        {
                            "type": "pollen_substitute",
                            "timing": "early_spring"
                        }
                    ],
                    "natural_sources": [
                        "banana_juice",
                        "pineapple_peelings",
                        "cassava",
                        "sugarcane_peelings",
                        "maize_flour"
                    ]
                }
            },
            "productivity_metrics": {
                "honey_yield": {
                    "optimal": {
                        "traditional_hive": {
                            "range": [8, 15],  # kg per harvest
                            "frequency": 2  # harvests per year
                        },
                        "modern_hive": {
                            "range": [15, 25],
                            "frequency": 3
                        }
                    },
                    "factors_affecting": [
                        "flora_availability",
                        "colony_strength",
                        "weather_conditions",
                        "hive_management",
                        "pest_control"
                    ]
                },
                "colony_strength": {
                    "indicators": {
                        "forager_activity": {
                            "high": "> 40 bees/minute",
                            "medium": "20-40 bees/minute",
                            "low": "< 20 bees/minute"
                        },
                        "brood_pattern": {
                            "excellent": "> 90% coverage",
                            "good": "70-90% coverage",
                            "poor": "< 70% coverage"
                        }
                    }
                }
            },
            "health_indicators": {
                "visual_cues": {
                    "healthy_colony": [
                        "consistent_flight_patterns",
                        "regular_pollen_collection",
                        "guard_bees_present",
                        "clean_hive_entrance"
                    ],
                    "problems": [
                        "erratic_flight_patterns",
                        "dead_bees_at_entrance",
                        "reduced_activity",
                        "unusual_odors"
                    ]
                },
                "common_threats": {
                    "pests": [
                        "varroa_mites",
                        "wax_moths",
                        "small_hive_beetles"
                    ],
                    "environmental": [
                        "drought",
                        "excessive_rain",
                        "pesticides",
                        "habitat_loss"
                    ]
                }
            },
            "seasonal_management": {
                "dry_season": {
                    "challenges": [
                        "reduced_forage",
                        "water_scarcity",
                        "overheating"
                    ],
                    "recommendations": [
                        "provide_water_sources",
                        "supplementary_feeding",
                        "ventilation_management",
                        "shade_provision"
                    ]
                },
                "wet_season": {
                    "challenges": [
                        "excess_moisture",
                        "reduced_foraging_time",
                        "fungal_growth"
                    ],
                    "recommendations": [
                        "improve_drainage",
                        "maintain_dry_conditions",
                        "regular_inspections",
                        "entrance_reduction"
                    ]
                }
            }
        }

    def get_foraging_recommendations(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate foraging recommendations based on current conditions"""
        recommendations = {
            "timing": [],
            "management": [],
            "alerts": []
        }

        # Check temperature conditions
        temp = conditions.get('temperature')
        if temp:
            optimal_range = self.knowledge_base['foraging_patterns']['environmental_factors']['temperature']['optimal_range']
            if temp < optimal_range['min']:
                recommendations['alerts'].append("Temperature too low for optimal foraging")
            elif temp > optimal_range['max']:
                recommendations['alerts'].append("Temperature too high for optimal foraging")

        # Check distance to water
        water_distance = conditions.get('water_distance')
        if water_distance:
            max_distance = self.knowledge_base['hive_management']['placement_criteria']['distance_from_water']['maximum']
            if water_distance > max_distance:
                recommendations['management'].append("Consider providing closer water sources")

        return recommendations

    def analyze_productivity(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze hive productivity based on provided metrics"""
        analysis = {
            "status": "",
            "issues": [],
            "recommendations": []
        }

        # Analyze honey yield
        if 'honey_yield' in metrics:
            optimal_yield = self.knowledge_base['productivity_metrics']['honey_yield']['optimal']
            hive_type = metrics.get('hive_type', 'traditional_hive')
            
            if metrics['honey_yield'] < optimal_yield[hive_type]['range'][0]:
                analysis['issues'].append("Below optimal honey yield")
                analysis['recommendations'].append("Review foraging conditions and hive management")

        # Analyze colony strength
        if 'forager_activity' in metrics:
            activity_levels = self.knowledge_base['productivity_metrics']['colony_strength']['indicators']['forager_activity']
            if metrics['forager_activity'] < int(activity_levels['low'].split()[0]):
                analysis['issues'].append("Low forager activity")
                analysis['recommendations'].append("Check for health issues and forage availability")

        return analysis

    def get_seasonal_guidance(self, season: str) -> Dict[str, Any]:
        """Get season-specific management guidance"""
        season_data = self.knowledge_base['seasonal_management'].get(season)
        if not season_data:
            return {"error": "Invalid season specified"}
        return season_data

# Create global instance
knowledge_base = BeekeepingKnowledgeBase()