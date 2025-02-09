from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
from .trend_analyzer import BeeTrendAnalyzer
from .analysis_metrics import BeeActivityAnalyzer
from .knowledge_base import knowledge_base
import logging

logger = logging.getLogger(__name__)

class BeekeepingReportGenerator:
    def __init__(self):
        self.trend_analyzer = BeeTrendAnalyzer()
        self.activity_analyzer = BeeActivityAnalyzer()

    def generate_comprehensive_report(self,
                                   user_id: str,
                                   current_data: Dict[str, Any],
                                   media_analysis: Optional[Dict[str, Any]] = None,
                                   environmental_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a comprehensive beekeeping report"""
        try:
            # Add current data point to trend analyzer
            self.trend_analyzer.add_data_point(user_id, current_data)
            
            # Get trend analysis
            trends = self.trend_analyzer.analyze_trends(user_id)
            
            # Get current status
            status = self.trend_analyzer.get_status_summary(user_id)
            
            # Analyze media if provided
            media_insights = self._analyze_media(media_analysis) if media_analysis else {}
            
            # Get environmental insights
            environmental_insights = self._analyze_environmental_data(environmental_data) if environmental_data else {}
            
            # Generate comprehensive report
            report = {
                'report_id': f"BEE-{user_id}-{datetime.now().strftime('%Y%m%d%H%M')}",
                'generated_at': datetime.now().isoformat(),
                'hive_status': {
                    'current_status': status['current_status'],
                    'key_metrics': status['key_metrics'],
                    'outlook': status['short_term_outlook']
                },
                'trend_analysis': {
                    'activity_trends': trends.get('activity_trend', {}),
                    'productivity_trends': trends.get('productivity_trend', {}),
                    'seasonal_patterns': trends.get('seasonal_pattern', {})
                },
                'media_analysis': media_insights,
                'environmental_analysis': environmental_insights,
                'recommendations': self._compile_recommendations(
                    status.get('immediate_actions', []),
                    trends.get('recommendations', []),
                    media_insights.get('recommendations', []),
                    environmental_insights.get('recommendations', [])
                )
            }
            
            # Add report summary
            report['summary'] = self._generate_report_summary(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                'error': 'Report generation failed',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _analyze_media(self, media_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process and structure media analysis results"""
        if not media_analysis:
            return {}
            
        return {
            'type': media_analysis.get('analysis_type', 'unknown'),
            'findings': media_analysis.get('findings', {}),
            'activity_metrics': self._extract_activity_metrics(media_analysis),
            'identified_issues': self._extract_issues(media_analysis),
            'recommendations': media_analysis.get('recommendations', [])
        }

    def _analyze_environmental_data(self, environmental_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environmental data and its impact"""
        if not environmental_data:
            return {}
            
        # Get recommendations from knowledge base
        foraging_recommendations = knowledge_base.get_foraging_recommendations(environmental_data)
        
        return {
            'conditions': environmental_data,
            'impact_assessment': self._assess_environmental_impact(environmental_data),
            'recommendations': foraging_recommendations.get('recommendations', [])
        }

    def _compile_recommendations(self, *recommendation_lists: List[str]) -> List[Dict[str, Any]]:
        """Compile and prioritize all recommendations"""
        all_recommendations = []
        priority_keywords = {
            'high': ['immediate', 'critical', 'urgent'],
            'medium': ['important', 'necessary', 'should'],
            'low': ['consider', 'may', 'could']
        }
        
        for rec_list in recommendation_lists:
            for rec in rec_list:
                priority = 'low'
                for p, keywords in priority_keywords.items():
                    if any(keyword in rec.lower() for keyword in keywords):
                        priority = p
                        break
                        
                all_recommendations.append({
                    'recommendation': rec,
                    'priority': priority,
                    'category': self._categorize_recommendation(rec)
                })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        all_recommendations.sort(key=lambda x: priority_order[x['priority']])
        
        return all_recommendations

    def _categorize_recommendation(self, recommendation: str) -> str:
        """Categorize a recommendation"""
        categories = {
            'foraging': ['forage', 'food', 'nectar', 'pollen'],
            'health': ['disease', 'pest', 'health', 'infection'],
            'management': ['hive', 'maintenance', 'clean', 'inspect'],
            'environment': ['weather', 'temperature', 'rain', 'shade']
        }
        
        for category, keywords in categories.items():
            if any(keyword in recommendation.lower() for keyword in keywords):
                return category
        return 'general'

    def _generate_report_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a concise summary of the report"""
        return {
            'status': report['hive_status']['current_status'],
            'outlook': report['hive_status']['outlook'],
            'key_findings': self._extract_key_findings(report),
            'priority_actions': [
                rec['recommendation'] for rec in report['recommendations']
                if rec['priority'] == 'high'
            ][:3]  # Top 3 priority actions
        }

    def _extract_key_findings(self, report: Dict[str, Any]) -> List[str]:
        """Extract key findings from the report"""
        findings = []
        
        # Add status-based finding
        findings.append(f"Hive status is {report['hive_status']['current_status']}")
        
        # Add trend-based finding
        if 'activity_trends' in report['trend_analysis']:
            trend = report['trend_analysis']['activity_trends'].get('trend_direction')
            if trend:
                findings.append(f"Activity is {trend}")
        
        # Add environmental finding if available
        if 'environmental_analysis' in report and 'impact_assessment' in report['environmental_analysis']:
            findings.append(report['environmental_analysis']['impact_assessment'])
        
        return findings

    def _extract_activity_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract activity metrics from media analysis"""
        metrics = {}
        
        if 'findings' in analysis:
            findings = analysis['findings']
            if 'image_analysis' in findings:
                metrics['instant_activity'] = findings['image_analysis'].get('bee_count')
            if 'video_analysis' in findings:
                metrics['activity_pattern'] = findings['video_analysis'].get('activity_summary', {})
                
        return metrics

    def _extract_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract identified issues from analysis"""
        issues = []
        
        if 'findings' in analysis:
            findings = analysis['findings']
            if 'issues' in findings:
                issues.extend(findings['issues'])
            if 'alerts' in findings:
                issues.extend(findings['alerts'])
                
        return issues

    def _assess_environmental_impact(self, environmental_data: Dict[str, Any]) -> str:
        """Assess the impact of environmental conditions"""
        optimal_conditions = knowledge_base.knowledge_base['foraging_patterns']['environmental_factors']
        
        # Check temperature
        if 'temperature' in environmental_data:
            temp = environmental_data['temperature']
            optimal_range = optimal_conditions['temperature']['optimal_range']
            if temp < optimal_range['min']:
                return "Temperature below optimal foraging range"
            elif temp > optimal_range['max']:
                return "Temperature above optimal foraging range"
            
        # Check other environmental factors
        if 'weather_condition' in environmental_data:
            if environmental_data['weather_condition'] not in optimal_conditions['weather_conditions']:
                return "Sub-optimal weather conditions for foraging"
                
        return "Environmental conditions within acceptable range"