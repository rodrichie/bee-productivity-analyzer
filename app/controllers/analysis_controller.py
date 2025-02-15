from flask import jsonify
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from ..services.data_intergration_service import DataIntegrationService
from ..utils.error_middleware import handle_errors
from ..utils.session_manager import session_manager
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AnalysisController:
    def __init__(self):
        self.integration_service = DataIntegrationService()

    @handle_errors
    async def process_analysis_request(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an analysis request"""
        session = session_manager.get_session(user_id)
        if not session:
            return jsonify({
                'error': 'Invalid session',
                'status': 401
            })

        # Process data through integration service
        analysis_results = await self.integration_service.process_new_data(user_id, data)

        # Update session with results
        session_manager.add_to_history(user_id, {
            'type': 'analysis',
            'data': data,
            'results': analysis_results
        })

        return jsonify({
            'status': 200,
            'data': analysis_results
        })

    @handle_errors
    async def get_historical_analysis(self,
                                    user_id: str,
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get historical analysis"""
        session = session_manager.get_session(user_id)
        if not session:
            return jsonify({
                'error': 'Invalid session',
                'status': 401
            })

        # Convert date strings to datetime objects
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        # Get historical analysis
        analysis = await self.integration_service.get_historical_analysis(user_id, start, end)

        return jsonify({
            'status': 200,
            'data': analysis
        })

    @handle_errors
    def get_forecast(self, user_id: str) -> Dict[str, Any]:
        """Get forecasted analysis"""
        session = session_manager.get_session(user_id)
        if not session:
            return jsonify({
                'error': 'Invalid session',
                'status': 401
            })

        # Generate forecast
        forecast = self.integration_service.generate_forecast(user_id)

        return jsonify({
            'status': 200,
            'data': forecast
        })

    @handle_errors
    def get_current_status(self, user_id: str) -> Dict[str, Any]:
        """Get current hive status"""
        session = session_manager.get_session(user_id)
        if not session:
            return jsonify({
                'error': 'Invalid session',
                'status': 401
            })

        # Get latest analysis results from session
        history = session.get('history', [])
        if not history:
            return jsonify({
                'error': 'No analysis data available',
                'status': 404
            })

        latest_analysis = history[-1]
        
        return jsonify({
            'status': 200,
            'data': {
                'timestamp': latest_analysis.get('timestamp'),
                'current_status': latest_analysis.get('results', {}).get('report', {}).get('hive_status', {}),
                'latest_metrics': latest_analysis.get('results', {}).get('analysis_components', {}).get('metrics', {}),
                'active_alerts': self._get_active_alerts(latest_analysis)
            }
        })

    def _get_active_alerts(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract active alerts from analysis data"""
        alerts = []
        
        # Check for alerts in different components
        if 'results' in analysis_data:
            results = analysis_data['results']
            
            # Check media analysis alerts
            if 'analysis_components' in results:
                components = results['analysis_components']
                if 'media' in components:
                    media_alerts = components['media'].get('alerts', [])
                    alerts.extend([{
                        'type': 'media',
                        'message': alert,
                        'severity': self._determine_alert_severity(alert)
                    } for alert in media_alerts])
                
                # Check environmental alerts
                if 'environmental' in components:
                    env_analysis = components['environmental']
                    if 'risks' in env_analysis:
                        alerts.extend([{
                            'type': 'environmental',
                            'message': risk,
                            'severity': 'warning'
                        } for risk in env_analysis['risks']])
                
                # Check metrics alerts
                if 'metrics' in components:
                    metrics = components['metrics']
                    if 'status' in metrics:
                        status = metrics['status']
                        if status.get('current_status') == 'needs_attention':
                            alerts.append({
                                'type': 'metrics',
                                'message': 'Hive needs attention based on current metrics',
                                'severity': 'warning'
                            })
        
        return alerts

    def _determine_alert_severity(self, alert: str) -> str:
        """Determine alert severity based on content"""
        critical_keywords = ['critical', 'severe', 'immediate', 'dangerous']
        warning_keywords = ['warning', 'attention', 'monitor', 'check']
        
        if any(keyword in alert.lower() for keyword in critical_keywords):
            return 'critical'
        elif any(keyword in alert.lower() for keyword in warning_keywords):
            return 'warning'
        return 'info'

    @handle_errors
    async def analyze_media(self, user_id: str, media_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process media analysis request"""
        session = session_manager.get_session(user_id)
        if not session:
            return jsonify({
                'error': 'Invalid session',
                'status': 401
            })

        # Validate media data
        if not self._validate_media_data(media_data):
            return jsonify({
                'error': 'Invalid media data format',
                'status': 400
            })

        # Process media through integration service
        analysis_results = await self.integration_service.process_new_data(
            user_id,
            {'media_data': media_data}
        )

        return jsonify({
            'status': 200,
            'data': analysis_results
        })

    def _validate_media_data(self, media_data: Dict[str, Any]) -> bool:
        """Validate media data format"""
        required_fields = ['type', 'content']
        if not all(field in media_data for field in required_fields):
            return False
            
        allowed_types = ['image', 'video']
        if media_data['type'] not in allowed_types:
            return False
            
        return True

    @handle_errors
    async def get_recommendations(self, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get personalized recommendations"""
        session = session_manager.get_session(user_id)
        if not session:
            return jsonify({
                'error': 'Invalid session',
                'status': 401
            })

        # Get history from session
        history = session.get('history', [])
        if not history:
            return jsonify({
                'error': 'No analysis data available',
                'status': 404
            })

        # Generate recommendations based on history and context
        recommendations = self._generate_recommendations(history, context)

        return jsonify({
            'status': 200,
            'data': recommendations
        })

    def _generate_recommendations(self, history: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate personalized recommendations"""
        recommendations = {
            'immediate_actions': [],
            'short_term': [],
            'long_term': []
        }

        # Get latest analysis
        latest_analysis = history[-1]
        
        # Get recommendations from latest report
        if 'results' in latest_analysis and 'report' in latest_analysis['results']:
            report = latest_analysis['results']['report']
            
            # Add immediate actions
            if 'recommendations' in report:
                for rec in report['recommendations']:
                    if rec['priority'] == 'high':
                        recommendations['immediate_actions'].append(rec)
                    elif rec['priority'] == 'medium':
                        recommendations['short_term'].append(rec)
                    else:
                        recommendations['long_term'].append(rec)

        # Consider context if provided
        if context:
            seasonal_recs = self._get_seasonal_recommendations(context.get('season'))
            weather_recs = self._get_weather_recommendations(context.get('weather'))
            
            recommendations['short_term'].extend(seasonal_recs)
            recommendations['immediate_actions'].extend(weather_recs)

        return recommendations

    def _get_seasonal_recommendations(self, season: Optional[str]) -> List[Dict[str, Any]]:
        """Get season-specific recommendations"""
        if not season:
            return []

        season_recommendations = {
            'spring': [
                {
                    'recommendation': 'Prepare for increased foraging activity',
                    'priority': 'medium',
                    'category': 'management'
                },
                {
                    'recommendation': 'Monitor for swarm indicators',
                    'priority': 'medium',
                    'category': 'management'
                }
            ],
            'summer': [
                {
                    'recommendation': 'Ensure adequate ventilation',
                    'priority': 'medium',
                    'category': 'management'
                },
                {
                    'recommendation': 'Monitor water availability',
                    'priority': 'medium',
                    'category': 'management'
                }
            ],
            'fall': [
                {
                    'recommendation': 'Prepare for reduced foraging',
                    'priority': 'medium',
                    'category': 'management'
                },
                {
                    'recommendation': 'Consider supplementary feeding',
                    'priority': 'medium',
                    'category': 'management'
                }
            ],
            'winter': [
                {
                    'recommendation': 'Monitor food stores',
                    'priority': 'high',
                    'category': 'management'
                },
                {
                    'recommendation': 'Ensure adequate insulation',
                    'priority': 'high',
                    'category': 'management'
                }
            ]
        }

        return season_recommendations.get(season.lower(), [])

    def _get_weather_recommendations(self, weather: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get weather-specific recommendations"""
        if not weather:
            return []

        recommendations = []
        
        # Temperature recommendations
        if 'temperature' in weather:
            temp = weather['temperature']
            if temp > 35:
                recommendations.append({
                    'recommendation': 'Implement cooling measures immediately',
                    'priority': 'high',
                    'category': 'environmental'
                })
            elif temp < 10:
                recommendations.append({
                    'recommendation': 'Ensure adequate hive insulation',
                    'priority': 'high',
                    'category': 'environmental'
                })

        # Rainfall recommendations
        if 'rainfall' in weather and weather['rainfall'] > 0:
            recommendations.append({
                'recommendation': 'Check hive entrance for proper drainage',
                'priority': 'high',
                'category': 'environmental'
            })

        return recommendations