import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging
from .knowledge_base import knowledge_base

logger = logging.getLogger(__name__)

class BeeActivityAnalyzer:
    def __init__(self):
        self.activity_history = {}
        self.metrics_threshold = {
            'minimum_bee_size': 20,  # pixels
            'maximum_bee_size': 100,  # pixels
            'motion_threshold': 25,
            'activity_threshold': 20  # bees per minute
        }

    def analyze_image(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze a single image for bee activity"""
        try:
            # Convert image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detect potential bees using contour detection
            _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours based on size constraints
            bee_contours = [c for c in contours if 
                          self.metrics_threshold['minimum_bee_size'] < 
                          cv2.contourArea(c) < 
                          self.metrics_threshold['maximum_bee_size']]
            
            return {
                'bee_count': len(bee_contours),
                'activity_level': self._calculate_activity_level(len(bee_contours)),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def analyze_video(self, video_frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze video frames for bee activity patterns"""
        try:
            frame_results = []
            motion_vectors = []
            
            for i in range(len(video_frames) - 1):
                # Analyze individual frame
                frame_analysis = self.analyze_image(video_frames[i])
                frame_results.append(frame_analysis)
                
                # Calculate motion between consecutive frames
                motion = self._calculate_motion(video_frames[i], video_frames[i + 1])
                motion_vectors.append(motion)
            
            return {
                'frame_analysis': frame_results,
                'motion_patterns': self._analyze_motion_patterns(motion_vectors),
                'activity_summary': self._generate_activity_summary(frame_results),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _calculate_activity_level(self, bee_count: int) -> str:
        """Calculate activity level based on bee count"""
        activity_levels = knowledge_base.knowledge_base['productivity_metrics']['colony_strength']['indicators']['forager_activity']
        
        if bee_count > int(activity_levels['high'].split('>')[1].split()[0]):
            return 'high'
        elif bee_count > int(activity_levels['medium'].split('-')[0]):
            return 'medium'
        else:
            return 'low'

    def _calculate_motion(self, frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        """Calculate motion between consecutive frames"""
        # Convert frames to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(
            gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        return flow

    def _analyze_motion_patterns(self, motion_vectors: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze motion patterns from optical flow data"""
        # Calculate average motion magnitude
        magnitudes = [np.sqrt(flow[..., 0]**2 + flow[..., 1]**2).mean() 
                     for flow in motion_vectors]
        
        # Analyze motion directions
        directions = []
        for flow in motion_vectors:
            angles = np.arctan2(flow[..., 1], flow[..., 0]) * 180 / np.pi
            directions.append(np.histogram(angles, bins=8)[0])
        
        return {
            'average_magnitude': np.mean(magnitudes),
            'direction_histogram': np.mean(directions, axis=0).tolist(),
            'activity_consistency': self._calculate_consistency(magnitudes)
        }

    def _calculate_consistency(self, values: List[float]) -> str:
        """Calculate consistency of activity"""
        std_dev = np.std(values)
        if std_dev < 0.2:
            return 'very_consistent'
        elif std_dev < 0.5:
            return 'consistent'
        else:
            return 'variable'

    def _generate_activity_summary(self, frame_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of activity analysis"""
        bee_counts = [result['bee_count'] for result in frame_results if 'bee_count' in result]
        
        if not bee_counts:
            return {'error': 'No valid bee counts found'}
        
        return {
            'average_bee_count': np.mean(bee_counts),
            'peak_activity': max(bee_counts),
            'activity_trend': self._calculate_trend(bee_counts),
            'recommendations': self._generate_recommendations(bee_counts)
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend in values"""
        if len(values) < 2:
            return 'insufficient_data'
        
        slope = np.polyfit(range(len(values)), values, 1)[0]
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'

    def _generate_recommendations(self, bee_counts: List[float]) -> List[str]:
        """Generate recommendations based on activity analysis"""
        recommendations = []
        avg_count = np.mean(bee_counts)
        trend = self._calculate_trend(bee_counts)
        
        # Get reference values from knowledge base
        activity_levels = knowledge_base.knowledge_base['productivity_metrics']['colony_strength']['indicators']['forager_activity']
        
        # Convert string thresholds to numeric values
        high_threshold = float(activity_levels['high'].split('>')[1].split()[0])
        low_threshold = float(activity_levels['low'].split('<')[1].split()[0])
        
        # Activity level recommendations
        if avg_count < low_threshold:
            recommendations.extend([
                "Colony shows low foraging activity",
                "Check for potential health issues",
                "Verify adequate food sources within foraging range",
                "Consider supplementary feeding"
            ])
        elif avg_count > high_threshold:
            recommendations.extend([
                "Strong foraging activity observed",
                "Ensure adequate water sources",
                "Monitor for signs of swarming",
                "Consider adding supers if needed"
            ])
        
        # Trend-based recommendations
        if trend == 'decreasing':
            recommendations.extend([
                "Declining foraging activity detected",
                "Check for environmental stressors",
                "Evaluate nectar source availability",
                "Inspect for disease or pest issues"
            ])
        elif trend == 'increasing':
            recommendations.append("Positive trend in foraging activity - maintain current conditions")
        
        return recommendations

    def integrate_environmental_data(self, environmental_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate environmental data with activity analysis"""
        foraging_guidance = knowledge_base.get_foraging_recommendations(environmental_data)
        
        return {
            'environmental_conditions': environmental_data,
            'foraging_recommendations': foraging_guidance,
            'timestamp': datetime.now().isoformat()
        }

    def get_comprehensive_analysis(self, 
                                 image_data: np.ndarray = None,
                                 video_data: List[np.ndarray] = None,
                                 environmental_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive analysis combining all available data"""
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'comprehensive',
            'findings': {},
            'recommendations': []
        }
        
        # Image analysis if available
        if image_data is not None:
            image_analysis = self.analyze_image(image_data)
            analysis_results['findings']['image_analysis'] = image_analysis
        
        # Video analysis if available
        if video_data is not None:
            video_analysis = self.analyze_video(video_data)
            analysis_results['findings']['video_analysis'] = video_analysis
        
        # Environmental data integration
        if environmental_data is not None:
            env_analysis = self.integrate_environmental_data(environmental_data)
            analysis_results['findings']['environmental_analysis'] = env_analysis
        
        # Generate combined recommendations
        analysis_results['recommendations'] = self._generate_combined_recommendations(analysis_results['findings'])
        
        return analysis_results

    def _generate_combined_recommendations(self, findings: Dict[str, Any]) -> List[str]:
        """Generate combined recommendations based on all findings"""
        combined_recommendations = set()  # Use set to avoid duplicates
        
        # Process image analysis findings
        if 'image_analysis' in findings:
            if 'bee_count' in findings['image_analysis']:
                combined_recommendations.update(
                    self._generate_recommendations([findings['image_analysis']['bee_count']])
                )
        
        # Process video analysis findings
        if 'video_analysis' in findings:
            if 'activity_summary' in findings['video_analysis']:
                combined_recommendations.update(
                    findings['video_analysis']['activity_summary'].get('recommendations', [])
                )
        
        # Process environmental findings
        if 'environmental_analysis' in findings:
            if 'foraging_recommendations' in findings['environmental_analysis']:
                combined_recommendations.update(
                    findings['environmental_analysis']['foraging_recommendations'].get('management', [])
                )
        
        return list(combined_recommendations)