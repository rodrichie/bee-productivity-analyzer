import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from .knowledge_base import knowledge_base
import logging

logger = logging.getLogger(__name__)

class BeeTrendAnalyzer:
    def __init__(self):
        self.data_points = {}
        self.seasonal_patterns = {}
        self.trend_thresholds = {
            'significant_change': 0.2,  # 20% change
            'trend_period_days': 30,    # analyze trends over 30 days
            'minimum_data_points': 5     # minimum points needed for analysis
        }

    def add_data_point(self, user_id: str, data: Dict[str, Any]) -> None:
        """Add a new data point for trend analysis"""
        if user_id not in self.data_points:
            self.data_points[user_id] = []
        
        data['timestamp'] = datetime.now()
        self.data_points[user_id].append(data)
        
        # Maintain data for last 365 days only
        cutoff_date = datetime.now() - timedelta(days=365)
        self.data_points[user_id] = [
            point for point in self.data_points[user_id]
            if point['timestamp'] > cutoff_date
        ]

    def analyze_trends(self, user_id: str) -> Dict[str, Any]:
        """Analyze trends for a specific user"""
        if user_id not in self.data_points:
            return {'error': 'No data available for analysis'}
        
        data = self.data_points[user_id]
        if len(data) < self.trend_thresholds['minimum_data_points']:
            return {'error': 'Insufficient data for trend analysis'}
        
        # Convert data to pandas DataFrame for easier analysis
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        # Calculate various trends
        activity_trend = self._analyze_activity_trend(df)
        productivity_trend = self._analyze_productivity_trend(df)
        seasonal_pattern = self._analyze_seasonal_pattern(df)
        
        return {
            'activity_trend': activity_trend,
            'productivity_trend': productivity_trend,
            'seasonal_pattern': seasonal_pattern,
            'recommendations': self._generate_trend_recommendations(
                activity_trend,
                productivity_trend,
                seasonal_pattern
            )
        }

    def _analyze_activity_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze bee activity trends"""
        recent_period = df.last('30D')
        
        if 'bee_count' in recent_period.columns:
            avg_activity = recent_period['bee_count'].mean()
            activity_change = (
                recent_period['bee_count'].iloc[-1] - 
                recent_period['bee_count'].iloc[0]
            ) / recent_period['bee_count'].iloc[0]
            
            return {
                'average_activity': avg_activity,
                'activity_change': activity_change,
                'trend_direction': self._get_trend_direction(activity_change),
                'consistency': self._calculate_consistency(recent_period['bee_count'])
            }
        
        return {'error': 'No activity data available'}

    def _analyze_productivity_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze productivity trends"""
        if 'honey_yield' in df.columns:
            recent_yields = df['honey_yield'].dropna()
            if len(recent_yields) >= 2:
                yield_change = (
                    recent_yields.iloc[-1] - recent_yields.iloc[0]
                ) / recent_yields.iloc[0]
                
                return {
                    'average_yield': recent_yields.mean(),
                    'yield_change': yield_change,
                    'trend_direction': self._get_trend_direction(yield_change),
                    'comparison_to_optimal': self._compare_to_optimal(recent_yields.mean())
                }
        
        return {'error': 'No productivity data available'}

    def _analyze_seasonal_pattern(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze seasonal patterns"""
        df['month'] = df.index.month
        
        if 'bee_count' in df.columns:
            monthly_averages = df.groupby('month')['bee_count'].mean()
            
            return {
                'peak_month': monthly_averages.idxmax(),
                'low_month': monthly_averages.idxmin(),
                'seasonal_variation': monthly_averages.std() / monthly_averages.mean(),
                'monthly_patterns': monthly_averages.to_dict()
            }
        
        return {'error': 'Insufficient data for seasonal analysis'}

    def _get_trend_direction(self, change: float) -> str:
        """Determine trend direction based on change value"""
        if change > self.trend_thresholds['significant_change']:
            return 'increasing'
        elif change < -self.trend_thresholds['significant_change']:
            return 'decreasing'
        return 'stable'

    def _calculate_consistency(self, series: pd.Series) -> str:
        """Calculate consistency of measurements"""
        cv = series.std() / series.mean()  # coefficient of variation
        
        if cv < 0.1:
            return 'very_consistent'
        elif cv < 0.2:
            return 'consistent'
        elif cv < 0.3:
            return 'moderately_variable'
        return 'highly_variable'

    def _compare_to_optimal(self, value: float) -> str:
        """Compare value to optimal ranges from knowledge base"""
        optimal_range = knowledge_base.knowledge_base['productivity_metrics']['honey_yield']['optimal']['modern_hive']['range']
        
        if value >= optimal_range[1]:
            return 'above_optimal'
        elif value >= optimal_range[0]:
            return 'optimal'
        return 'below_optimal'

    def _generate_trend_recommendations(self,
                                     activity_trend: Dict[str, Any],
                                     productivity_trend: Dict[str, Any],
                                     seasonal_pattern: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on trend analysis"""
        recommendations = []
        
        # Activity trend recommendations
        if 'trend_direction' in activity_trend:
            if activity_trend['trend_direction'] == 'decreasing':
                recommendations.extend([
                    "Review recent changes in environment or management",
                    "Check for potential stressors affecting foraging",
                    "Consider supplementary feeding if needed"
                ])
            elif activity_trend['consistency'] == 'highly_variable':
                recommendations.append("Investigate causes of variable activity levels")
        
        # Productivity trend recommendations
        if 'comparison_to_optimal' in productivity_trend:
            if productivity_trend['comparison_to_optimal'] == 'below_optimal':
                recommendations.extend([
                    "Review hive management practices",
                    "Assess food source availability",
                    "Consider colony strength assessment"
                ])
        
        # Seasonal pattern recommendations
        if 'seasonal_variation' in seasonal_pattern:
            if seasonal_pattern['seasonal_variation'] > 0.5:
                recommendations.extend([
                    "Plan for seasonal variations in foraging conditions",
                    "Prepare supplementary feeding for low activity periods",
                    "Consider seasonal hive management adjustments"
                ])
        
        return recommendations

    def get_status_summary(self, user_id: str) -> Dict[str, Any]:
        """Get current status summary for a hive"""
        trends = self.analyze_trends(user_id)
        
        return {
            'current_status': self._determine_overall_status(trends),
            'key_metrics': self._extract_key_metrics(trends),
            'short_term_outlook': self._generate_outlook(trends),
            'immediate_actions': self._prioritize_recommendations(trends),
            'timestamp': datetime.now().isoformat()
        }

    def _determine_overall_status(self, trends: Dict[str, Any]) -> str:
        """Determine overall hive status based on trends"""
        if 'error' in trends:
            return 'unknown'
            
        status_indicators = []
        
        if 'activity_trend' in trends:
            if trends['activity_trend'].get('trend_direction') == 'increasing':
                status_indicators.append(1)
            elif trends['activity_trend'].get('trend_direction') == 'decreasing':
                status_indicators.append(-1)
            else:
                status_indicators.append(0)
                
        if 'productivity_trend' in trends:
            if trends['productivity_trend'].get('comparison_to_optimal') == 'above_optimal':
                status_indicators.append(1)
            elif trends['productivity_trend'].get('comparison_to_optimal') == 'below_optimal':
                status_indicators.append(-1)
            else:
                status_indicators.append(0)
        
        avg_indicator = np.mean(status_indicators) if status_indicators else 0
        
        if avg_indicator > 0.3:
            return 'excellent'
        elif avg_indicator > 0:
            return 'good'
        elif avg_indicator > -0.3:
            return 'fair'
        return 'needs_attention'

    def _extract_key_metrics(self, trends: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from trend data"""
        metrics = {}
        
        if 'activity_trend' in trends:
            metrics['activity'] = {
                'level': trends['activity_trend'].get('average_activity'),
                'trend': trends['activity_trend'].get('trend_direction')
            }
            
        if 'productivity_trend' in trends:
            metrics['productivity'] = {
                'level': trends['productivity_trend'].get('average_yield'),
                'status': trends['productivity_trend'].get('comparison_to_optimal')
            }
            
        return metrics

    def _generate_outlook(self, trends: Dict[str, Any]) -> str:
        """Generate short-term outlook based on trends"""
        if 'error' in trends:
            return 'insufficient_data'
            
        positive_indicators = 0
        total_indicators = 0
        
        if 'activity_trend' in trends:
            if trends['activity_trend'].get('trend_direction') == 'increasing':
                positive_indicators += 1
            total_indicators += 1
            
        if 'productivity_trend' in trends:
            if trends['productivity_trend'].get('trend_direction') != 'decreasing':
                positive_indicators += 1
            total_indicators += 1
            
        if total_indicators == 0:
            return 'uncertain'
            
        outlook_score = positive_indicators / total_indicators
        
        if outlook_score > 0.7:
            return 'positive'
        elif outlook_score > 0.3:
            return 'stable'
        return 'cautious'

    def _prioritize_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """Prioritize and limit recommendations to most important actions"""
        if 'recommendations' not in trends:
            return []
            
        # Sort recommendations by urgency/importance
        urgent_keywords = ['immediate', 'critical', 'urgent', 'required']
        important_keywords = ['review', 'consider', 'assess', 'monitor']
        
        prioritized = []
        for rec in trends['recommendations']:
            if any(keyword in rec.lower() for keyword in urgent_keywords):
                prioritized.append(('urgent', rec))
            elif any(keyword in rec.lower() for keyword in important_keywords):
                prioritized.append(('important', rec))
            else:
                prioritized.append(('normal', rec))
                
        # Sort by priority and limit to top 5
        prioritized.sort(key=lambda x: {'urgent': 0, 'important': 1, 'normal': 2}[x[0]])
        return [rec[1] for rec in prioritized[:5]]

    def correlate_with_environment(self, user_id: str, environmental_data: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate trend data with environmental factors"""
        trends = self.analyze_trends(user_id)
        if 'error' in trends:
            return {'error': 'Insufficient trend data for correlation'}
            
        correlations = {
            'activity_correlations': self._analyze_environmental_correlations(
                self.data_points[user_id], 'bee_count', environmental_data
            ),
            'productivity_correlations': self._analyze_environmental_correlations(
                self.data_points[user_id], 'honey_yield', environmental_data
            )
        }
        
        return {
            'correlations': correlations,
            'insights': self._generate_correlation_insights(correlations),
            'recommendations': self._generate_environmental_recommendations(correlations)
        }

    def _analyze_environmental_correlations(self, 
                                         data_points: List[Dict[str, Any]], 
                                         metric: str,
                                         environmental_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze correlations between metrics and environmental factors"""
        df = pd.DataFrame(data_points)
        correlations = {}
        
        for env_factor, values in environmental_data.items():
            if metric in df.columns and len(df[metric]) > 0:
                correlation = df[metric].corr(pd.Series(values))
                if not np.isnan(correlation):
                    correlations[env_factor] = correlation
                    
        return correlations

    def _generate_correlation_insights(self, correlations: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate insights based on environmental correlations"""
        insights = []
        
        for metric_type, corrs in correlations.items():
            strong_correlations = {
                factor: corr for factor, corr in corrs.items() 
                if abs(corr) > 0.7
            }
            
            moderate_correlations = {
                factor: corr for factor, corr in corrs.items() 
                if 0.4 <= abs(corr) <= 0.7
            }
            
            if strong_correlations:
                insights.append(f"Strong {metric_type} correlations found with: {', '.join(strong_correlations.keys())}")
            
            if moderate_correlations:
                insights.append(f"Moderate {metric_type} correlations found with: {', '.join(moderate_correlations.keys())}")
                
        return insights

    def _generate_environmental_recommendations(self, correlations: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate recommendations based on environmental correlations"""
        recommendations = []
        
        for metric_type, corrs in correlations.items():
            for factor, correlation in corrs.items():
                if abs(correlation) > 0.7:
                    if correlation > 0:
                        recommendations.append(f"Maintain favorable {factor} conditions to optimize {metric_type}")
                    else:
                        recommendations.append(f"Consider mitigation strategies for negative {factor} impact on {metric_type}")
                        
        return recommendations

    def export_trend_report(self, user_id: str) -> Dict[str, Any]:
        """Generate a comprehensive trend report for export"""
        trends = self.analyze_trends(user_id)
        status = self.get_status_summary(user_id)
        
        return {
            'report_date': datetime.now().isoformat(),
            'hive_id': user_id,
            'overall_status': status['current_status'],
            'trend_analysis': {
                'activity': trends.get('activity_trend', {}),
                'productivity': trends.get('productivity_trend', {}),
                'seasonal_patterns': trends.get('seasonal_pattern', {})
            },
            'metrics_summary': status['key_metrics'],
            'outlook': status['short_term_outlook'],
            'action_items': status['immediate_actions'],
            'long_term_recommendations': trends.get('recommendations', [])
        }