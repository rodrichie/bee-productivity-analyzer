import os
import google.generativeai as genai
from PIL import Image
import cv2
import numpy as np
import base64
import io
from typing import Union, List, Dict
from datetime import datetime
import tempfile
from pathlib import Path

class MediaAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        
        # Create temp directory for media files
        self.temp_dir = Path(tempfile.gettempdir()) / 'bee_analysis'
        self.temp_dir.mkdir(exist_ok=True)

    def analyze_image(self, image_data: Union[str, bytes], analysis_type: str = 'general') -> Dict:
        """
        Analyze a single image with specified analysis type.
        
        Args:
            image_data: Image data in bytes or base64 string
            analysis_type: Type of analysis ('general', 'foraging', 'health', 'productivity')
        
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Handle base64 encoded images
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
                image_data = base64.b64decode(image_data)
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Get appropriate prompt based on analysis type
            prompt = self._get_analysis_prompt(analysis_type)
            
            # Generate analysis
            response = self.vision_model.generate_content([prompt, image])
            
            return {
                'success': True,
                'analysis': response.text,
                'timestamp': datetime.now().isoformat(),
                'type': analysis_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def analyze_video(self, video_data: bytes, analysis_type: str = 'general') -> Dict:
        """
        Analyze a video by extracting key frames and analyzing them.
        
        Args:
            video_data: Video file data in bytes
            analysis_type: Type of analysis ('general', 'foraging', 'health', 'productivity')
        
        Returns:
            Dictionary containing analysis results from key frames
        """
        try:
            # Save video temporarily
            video_path = self.temp_dir / f'temp_video_{datetime.now().timestamp()}.mp4'
            with open(video_path, 'wb') as f:
                f.write(video_data)
            
            # Extract key frames
            frames = self._extract_key_frames(str(video_path))
            
            # Analyze each key frame
            frame_analyses = []
            for i, frame in enumerate(frames):
                # Convert frame to PIL Image
                frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # Get analysis prompt
                prompt = self._get_analysis_prompt(analysis_type, frame_number=i+1)
                
                # Generate analysis
                response = self.vision_model.generate_content([prompt, frame_pil])
                frame_analyses.append(response.text)
            
            # Summarize analyses
            summary_prompt = f"""
            Summarize these analyses of {len(frames)} video frames:
            {frame_analyses}
            
            Provide:
            1. Key observations
            2. Consistent patterns
            3. Notable changes between frames
            4. Overall recommendations
            """
            
            summary = self.vision_model.generate_content(summary_prompt).text
            
            # Cleanup
            video_path.unlink()
            
            return {
                'success': True,
                'summary': summary,
                'frame_analyses': frame_analyses,
                'timestamp': datetime.now().isoformat(),
                'type': analysis_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _extract_key_frames(self, video_path: str, max_frames: int = 5) -> List[np.ndarray]:
        """Extract key frames from video using scene detection."""
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        try:
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            # Calculate frame interval
            interval = max(total_frames // max_frames, fps)  # At least 1 second apart
            
            frame_count = 0
            while len(frames) < max_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frames.append(frame)
                frame_count += interval
                
        finally:
            cap.release()
        
        return frames

    def _get_analysis_prompt(self, analysis_type: str, frame_number: int = None) -> str:
        """Get appropriate analysis prompt based on type."""
        frame_context = f"In frame {frame_number} of the video" if frame_number else "In this image"
        
        prompts = {
            'general': f"""
                {frame_context}, analyze the beekeeping scene and provide:
                1. Overall assessment of visible conditions
                2. Identification of any issues or concerns
                3. Recommendations for improvement
                4. Potential impact on hive productivity
            """,
            'foraging': f"""
                {frame_context}, analyze bee foraging activity:
                1. Assess visible foraging patterns
                2. Evaluate available food sources
                3. Identify potential foraging obstacles
                4. Suggest improvements for foraging efficiency
            """,
            'health': f"""
                {frame_context}, examine bee and hive health:
                1. Look for signs of disease or pests
                2. Assess hive condition
                3. Evaluate bee activity and behavior
                4. Recommend health management actions
            """,
            'productivity': f"""
                {frame_context}, evaluate productivity factors:
                1. Assess hive strength and activity
                2. Examine visible honey production signs
                3. Identify productivity limiters
                4. Suggest productivity improvements
            """
        }
        
        return prompts.get(analysis_type, prompts['general'])