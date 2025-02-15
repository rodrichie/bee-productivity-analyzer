from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import numpy as np
from ..models.trend_analyzer import BeeTrendAnalyzer
from ..models.analysis_metrics import BeeActivityAnalyzer
from ..models.knowledge_base import knowledge_base
from ..models.reporting_system import BeekeepingReportGenerator

logger = logging.getLogger(__name__)

class DataIntegrationService:
    def __init__(self):
        self.trend_analyzer = BeeTrendAnalyzer()
        self.activity_analyzer = BeeActivityAnalyzer()
        self.report_generator = BeekeepingReportGenerator()
        self.data_cache = {}

    async def process_new_data(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process new data and generate integrated analysis"""
        try:
            # Extract different types of data
            media_data = data.get('media_data')
            environmental_data = data.get('environmental_data')
            metrics_data = data.get('metrics_data')

            # Store in cache
            self._update_cache(user_id, data)

            # Process each data type
            analysis_results = {
                'timestamp': datetime.now().isoformat(),
                'analysis_components': {}
            }

            # Media analysis if available
            if media_data:
                analysis_results['analysis_components']['media'] = \
                    await self._process_media_data(media_data)

            # Environmental analysis
            if environmental_data:
                analysis_results['analysis_components']['environmental'] = \
                    self._process_environmental_data(environmental_data)

            # Metrics analysis
            if metrics_data:
                analysis_results['analysis_components']['metrics'] = \
                    self._process_metrics_data(user_id, metrics_data)

            # Generate comprehensive report
            analysis_results['report'] = self.report_generator.generate_comprehensive_report(
                user_id=user_id,
                current_data=metrics_data or {},
                media_analysis=analysis_results['analysis_components'].get('media'),
                environmental_data=environmental_data
            )

            return analysis_results

        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return {
                'error': 'Data processing failed',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def _process_media_data(self, media_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process media data for analysis"""
        try:
            if media_data['type'] == 'image':
                return await self.activity_analyzer.analyze_image(media_data['content'])
            elif media_data['type'] == 'video':
                return await self.activity_analyzer.analyze_video(media_data['content'])
            else:
                raise ValueError(f"Unsupported media type: {media_data['type']}")
        except Exception as e:
            logger.error(f"Error processing media: {str(e)}")
            return {'error': str(e)}

    def _process_environmental_data(self, environmental_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process environmental data"""
        try:
            # Get recommendations from knowledge base
            recommendations = knowledge_base.get_foraging_recommendations(environmental_data)

            # Analyze environmental impact
            impact_analysis = self._analyze_environmental_impact(environmental_data)

            return {
                'conditions': environmental_data,
                'recommendations': recommendations,
                'impact_analysis': impact_analysis
            }
        except Exception as e:
            logger.error(f"Error processing environmental data: {str(e)}")
            return {'error': str(e)}

    def _process_metrics_data(self, user_id: str, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process metrics data"""
        try:
            # Add to trend analyzer
            self.trend_analyzer.add_data_point(user_id, metrics_data)

            # Get trend analysis
            trends = self.trend_analyzer.analyze_trends(user_id)

            return {
                'metrics': metrics_data,
                'trends': trends,
                'status': self.trend_analyzer.get_status_summary(user_id)
            }
        except Exception as e:
            logger.error(f"Error processing metrics: {str(e)}")
            return {'error': str(e)}

    def _analyze_environmental_impact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environmental impact on bee activity"""
        impact_analysis = {
            'foraging_conditions': 'optimal',
            'risks': [],
            'opportunities': []
        }

        # Check temperature
        if 'temperature' in data:
            temp = data['temperature']
            if temp < 15:
                impact_analysis['risks'].append('Temperature too low for optimal foraging')
                impact_analysis['foraging_conditions'] = 'suboptimal'
            elif temp > 35:
                impact_analysis['risks'].append('Temperature too high for optimal foraging')
                impact_analysis['foraging_conditions'] = 'suboptimal'
            else:
                impact_analysis['opportunities'].append('Temperature within optimal range')

        # Check humidity
        if 'humidity' in data:
            humidity = data['humidity']
            if humidity > 80:
                impact_analysis['risks'].append('High humidity may affect nectar concentration')
            elif humidity < 30:
                impact_analysis['risks'].append('Low humidity may affect nectar availability')

        # Check rainfall
        if 'rainfall' in data:
            rainfall = data['rainfall']
            if rainfall > 0:
                impact_analysis['risks'].append('Active rainfall may limit foraging activity')
                impact_analysis['foraging_conditions'] = 'limited'

        return impact_analysis

    def _update_cache(self, user_id: str, data: Dict[str, Any]) -> None:
        """Update data cache for user"""
        if user_id not in self.data_cache:
            self.data_cache[user_id] = []

        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()

        # Add to cache
        self.data_cache[user_id].append(data)

        # Maintain cache size (keep last 30 days of data)
        self._cleanup_cache(user_id)

    def _cleanup_cache(self, user_id: str) -> None:
        """Clean up old cache entries"""
        if user_id in self.data_cache:
            # Keep only last 30 days of data
            thirty_days_ago = datetime.now() - timedelta(days=30)
            self.data_cache[user_id] = [
                entry for entry in self.data_cache[user_id]
                if datetime.fromisoformat(entry['timestamp']) > thirty_days_ago
            ]

    async def get_historical_analysis(self, user_id: str, 
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get historical analysis for a date range"""
        try:
            # Get cached data for date range
            filtered_data = self._get_filtered_data(user_id, start_date, end_date)

            if not filtered_data:
                return {
                    'error': 'No data available for specified date range',
                    'timestamp': datetime.now().isoformat()
                }

            # Analyze trends
            trend_analysis = self._analyze_historical_trends(filtered_data)

            # Generate insights
            insights = self._generate_historical_insights(trend_analysis)

            return {
                'date_range': {
                    'start': start_date.isoformat() if start_date else 'earliest',
                    'end': end_date.isoformat() if end_date else 'latest'
                },
                'trend_analysis': trend_analysis,
                'insights': insights,
                'recommendations': self._generate_historical_recommendations(trend_analysis)
            }

        except Exception as e:
            logger.error(f"Error generating historical analysis: {str(e)}")
            return {
                'error': 'Historical analysis failed',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _get_filtered_data(self, user_id: str,
                          start_date: Optional[datetime],
                          end_date: Optional[datetime]) -> List[Dict[str, Any]]:
        """Get data filtered by date range"""
        if user_id not in self.data_cache:
            return []

        filtered_data = self.data_cache[user_id]

        if start_date:
            filtered_data = [
                entry for entry in filtered_data
                if datetime.fromisoformat(entry['timestamp']) >= start_date
            ]

        if end_date:
            filtered_data = [
                entry for entry in filtered_data
                if datetime.fromisoformat(entry['timestamp']) <= end_date
            ]

        return filtered_data

    def _analyze_historical_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze historical trends in data"""
        trends = {
            'activity': self._analyze_activity_trends(data),
            'productivity': self._analyze_productivity_trends(data),
            'environmental': self._analyze_environmental_trends(data)
        }

        # Calculate correlations
        trends['correlations'] = self._calculate_correlations(data)

        return trends

    def _analyze_activity_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze bee activity trends"""
        activity_data = [
            (datetime.fromisoformat(entry['timestamp']), 
             entry.get('metrics_data', {}).get('bee_count', 0))
            for entry in data
            if 'metrics_data' in entry and 'bee_count' in entry['metrics_data']
        ]

        if not activity_data:
            return {'error': 'No activity data available'}

        return {
            'average_activity': np.mean([count for _, count in activity_data]),
            'peak_activity': max(count for _, count in activity_data),
            'activity_pattern': self._analyze_daily_patterns(activity_data),
            'trend': self._calculate_trend([count for _, count in activity_data])
        }

    def _analyze_productivity_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze productivity trends"""
        productivity_data = [
            (datetime.fromisoformat(entry['timestamp']),
             entry.get('metrics_data', {}).get('honey_yield', 0))
            for entry in data
            if 'metrics_data' in entry and 'honey_yield' in entry['metrics_data']
        ]

        if not productivity_data:
            return {'error': 'No productivity data available'}

        return {
            'total_yield': sum(yield_ for _, yield_ in productivity_data),
            'average_yield': np.mean([yield_ for _, yield_ in productivity_data]),
            'yield_pattern': self._analyze_seasonal_patterns(productivity_data),
            'trend': self._calculate_trend([yield_ for _, yield_ in productivity_data])
        }

    def _analyze_environmental_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze environmental trends"""
        env_data = [
            entry.get('environmental_data', {})
            for entry in data
            if 'environmental_data' in entry
        ]

        if not env_data:
            return {'error': 'No environmental data available'}

        return {
            'temperature_range': {
                'min': min(d.get('temperature', float('inf')) for d in env_data),
                'max': max(d.get('temperature', float('-inf')) for d in env_data),
                'avg': np.mean([d.get('temperature', 0) for d in env_data])
            },
            'humidity_range': {
                'min': min(d.get('humidity', float('inf')) for d in env_data),
                'max': max(d.get('humidity', float('-inf')) for d in env_data),
                'avg': np.mean([d.get('humidity', 0) for d in env_data])
            },
            'weather_patterns': self._analyze_weather_patterns(env_data)
        }

    def _calculate_correlations(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate correlations between different metrics"""
        correlations = {}
        
        # Extract time series for different metrics
        metrics = {
            'bee_count': [],
            'temperature': [],
            'humidity': [],
            'honey_yield': []
        }

        for entry in data:
            if 'metrics_data' in entry:
                metrics['bee_count'].append(entry['metrics_data'].get('bee_count', None))
                metrics['honey_yield'].append(entry['metrics_data'].get('honey_yield', None))
            
            if 'environmental_data' in entry:
                metrics['temperature'].append(entry['environmental_data'].get('temperature', None))
                metrics['humidity'].append(entry['environmental_data'].get('humidity', None))

        # Calculate correlations between available metrics
        for metric1 in metrics:
            for metric2 in metrics:
                if metric1 < metric2:  # Avoid duplicate correlations
                    # Filter out None values
                    valid_data = [
                        (m1, m2) for m1, m2 in zip(metrics[metric1], metrics[metric2])
                        if m1 is not None and m2 is not None
                    ]
                    
                    if valid_data:
                        correlation = np.corrcoef(
                            [d[0] for d in valid_data],
                            [d[1] for d in valid_data]
                        )[0, 1]
                        
                        correlations[f'{metric1}_vs_{metric2}'] = correlation

        return correlations

    def _generate_historical_insights(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from historical trend analysis"""
        insights = []

        # Activity insights
        if 'activity' in trend_analysis and 'trend' in trend_analysis['activity']:
            activity_trend = trend_analysis['activity']['trend']
            insights.append(f"Bee activity shows {activity_trend} trend")

        # Productivity insights
        if 'productivity' in trend_analysis and 'trend' in trend_analysis['productivity']:
            prod_trend = trend_analysis['productivity']['trend']
            insights.append(f"Honey yield shows {prod_trend} trend")

        # Correlation insights
        if 'correlations' in trend_analysis:
            for correlation_type, value in trend_analysis['correlations'].items():
                if abs(value) > 0.7:
                    insights.append(f"Strong correlation found between {correlation_type.replace('_vs_', ' and ')}")

        return insights

    def _generate_historical_recommendations(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on historical analysis"""
        recommendations = []

        # Activity-based recommendations
        if 'activity' in trend_analysis:
            activity_data = trend_analysis['activity']
            if activity_data.get('trend') == 'decreasing':
                recommendations.extend([
                    "Review and optimize hive placement",
                    "Check for environmental stressors",
                    "Consider supplementary feeding"
                ])

        # Productivity-based recommendations
        if 'productivity' in trend_analysis:
            prod_data = trend_analysis['productivity']
            if prod_data.get('trend') == 'decreasing':
                recommendations.extend([
                    "Evaluate queen performance",
                    "Review disease prevention measures",
                    "Assess nectar source availability"
                ])

        # Environmental recommendations
        if 'environmental' in trend_analysis:
            env_data = trend_analysis['environmental']
            if 'temperature_range' in env_data:
                temp_range = env_data['temperature_range']
                if temp_range['avg'] > 35:
                    recommendations.append("Consider additional cooling measures")
                elif temp_range['avg'] < 15:
                    recommendations.append("Implement winter preparation measures")

        return recommendations

    def generate_forecast(self, user_id: str) -> Dict[str, Any]:
        """Generate forecasts based on historical data"""
        try:
            historical_data = self.data_cache.get(user_id, [])
            if not historical_data:
                return {'error': 'Insufficient data for forecasting'}

            # Generate forecasts
            activity_forecast = self._forecast_activity(historical_data)
            productivity_forecast = self._forecast_productivity(historical_data)
            environmental_forecast = self._forecast_environmental_conditions(historical_data)

            return {
                'activity_forecast': activity_forecast,
                'productivity_forecast': productivity_forecast,
                'environmental_forecast': environmental_forecast,
                'recommendations': self._generate_forecast_recommendations(
                    activity_forecast,
                    productivity_forecast,
                    environmental_forecast
                )
            }

        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            return {'error': 'Forecast generation failed'}