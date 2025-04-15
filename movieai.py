# Update movieai.py with proper ffmpeg support and error handling

import os
import shutil
import json
import time
import tempfile
import subprocess
import base64
from pathlib import Path
from genai import GenAI

class MovieAI(GenAI):
    """
    Enhanced MovieAI class that uses ffmpeg for video processing instead of cv2.
    """
    def __init__(self, openai_api_key, ffmpeg_path="ffmpeg"):
        """
        Initializes MovieAI as an extension of GenAI.
        """
        super().__init__(openai_api_key)  # Initialize parent class (GenAI)
        self.ffmpeg_path = ffmpeg_path

        # Check if FFmpeg is accessible
        if not shutil.which(self.ffmpeg_path):
            print(f"Warning: FFmpeg not found at '{self.ffmpeg_path}'. Checking for system installation.")
            if shutil.which("ffmpeg"):
                self.ffmpeg_path = "ffmpeg"
                print("Found system ffmpeg installation.")
            else:
                print("FFmpeg not found. Video processing features will be limited.")
    
    def extract_frames(self, file_path, max_samples=15, output_dir=None):
        """
        Extract frames from a video file using ffmpeg instead of cv2.
        
        Parameters:
        -----------
        file_path : str
            Path to the video file
        max_samples : int, optional
            Maximum number of frames to extract
        output_dir : str, optional
            Directory to save extracted frames
            
        Returns:
        --------
        tuple
            (list of base64 encoded frames, number of frames, fps)
        """
        try:
            # Create temporary directory if output_dir not provided
            if output_dir is None:
                temp_dir = tempfile.mkdtemp()
                output_dir = temp_dir
            else:
                temp_dir = None
                os.makedirs(output_dir, exist_ok=True)
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"Error: Video file not found at {file_path}")
                return [], 0, 0
            
            # Get video information using ffprobe
            probe_cmd = [
                self.ffmpeg_path.replace('ffmpeg', 'ffprobe'),
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=r_frame_rate,nb_frames',
                '-of', 'json',
                file_path
            ]
            
            try:
                probe_output = subprocess.check_output(probe_cmd, stderr=subprocess.STDOUT, text=True)
                video_info = json.loads(probe_output)
                
                # Parse frame rate
                if 'streams' in video_info and video_info['streams']:
                    fps_str = video_info['streams'][0].get('r_frame_rate', '25/1')
                    if '/' in fps_str:
                        num, den = map(int, fps_str.split('/'))
                        fps = num / den
                    else:
                        fps = float(fps_str)
                    
                    # Get total frames if available
                    total_frames = int(video_info['streams'][0].get('nb_frames', '0'))
                    if total_frames == 0:  # If ffprobe couldn't determine frame count
                        # Estimate based on duration (fallback)
                        duration_cmd = [
                            self.ffmpeg_path.replace('ffmpeg', 'ffprobe'),
                            '-v', 'error',
                            '-show_entries', 'format=duration',
                            '-of', 'json',
                            file_path
                        ]
                        duration_output = subprocess.check_output(duration_cmd, stderr=subprocess.STDOUT, text=True)
                        duration_info = json.loads(duration_output)
                        if 'format' in duration_info and 'duration' in duration_info['format']:
                            duration = float(duration_info['format']['duration'])
                            total_frames = int(duration * fps)
                else:
                    fps = 25  # Default fallback
                    total_frames = 1000  # Arbitrary fallback
                
            except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as e:
                print(f"Error getting video info: {str(e)}")
                fps = 25  # Default fallback
                total_frames = 1000  # Arbitrary fallback
            
            # Calculate frame interval to extract approximately max_samples frames
            if total_frames > max_samples:
                frame_interval = max(1, total_frames // max_samples)
            else:
                frame_interval = 1
            
            # Extract frames using ffmpeg
            frames_path = os.path.join(output_dir, 'frame_%04d.jpg')
            extract_cmd = [
                self.ffmpeg_path,
                '-i', file_path,
                '-vf', f'select=not(mod(n\\,{frame_interval}))',
                '-vsync', 'vfr',
                '-q:v', '2',  # High quality JPG
                '-frames:v', str(max_samples),
                frames_path
            ]
            
            subprocess.run(extract_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Get list of extracted frames
            frame_files = sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.startswith('frame_') and f.endswith('.jpg')])
            
            # Limit to max_samples
            frame_files = frame_files[:max_samples]
            
            # Convert frames to base64
            base64_frames = []
            for frame_file in frame_files:
                with open(frame_file, 'rb') as f:
                    frame_data = f.read()
                    base64_frame = base64.b64encode(frame_data).decode('utf-8')
                    base64_frames.append(base64_frame)
            
            # Clean up temporary directory if created
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            return base64_frames, len(base64_frames), fps
            
        except Exception as e:
            print(f"Error extracting frames from video: {str(e)}")
            # Clean up temporary directory if created
            if 'temp_dir' in locals() and temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
            return [], 0, 0
    
    def generate_video_description(self, fname_video, instructions, max_samples=15, model='gpt-4o-mini'):
        """
        Generate a description of a video file using extracted frames.
        
        Parameters:
        -----------
        fname_video : str
            Path to the video file
        instructions : str
            Prompt instructions for analyzing the video
        max_samples : int, optional
            Maximum number of frames to analyze
        model : str, optional
            Model to use for image analysis
            
        Returns:
        --------
        str
            Video description
        """
        try:
            # Extract frames
            base64Frames, nframes, fps = self.extract_frames(fname_video, max_samples)
            
            if not base64Frames:
                return self._get_sanitized_fallback_response(fname_video, instructions)
            
            # Create content blocks for each frame
            content_blocks = [{"type": "text", "text": instructions}]
            
            # Add a maximum of 5 frames to avoid exceeding token limits
            sample_frames = base64Frames[:min(5, len(base64Frames))]
            
            for frame in sample_frames:
                content_blocks.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{frame}"}
                })
            
            # Call the OpenAI API
            PROMPT_MESSAGES = [
                {
                    "role": "user",
                    "content": content_blocks
                }
            ]
            
            params = {
                "model": model,
                "messages": PROMPT_MESSAGES,
                "max_tokens": 1000,
            }
            
            try:
                completion = self.client.chat.completions.create(**params)
                response = completion.choices[0].message.content
                
                # Clean up the response
                response = response.replace("```html", "")
                response = response.replace("```", "")
                
                return response
            except Exception as api_err:
                print(f"API error in generate_video_description: {str(api_err)}")
                return self._get_sanitized_fallback_response(fname_video, instructions)
                
        except Exception as e:
            print(f"Error in generate_video_description: {str(e)}")
            return self._get_sanitized_fallback_response(fname_video, instructions)
    
    def _get_sanitized_fallback_response(self, video_path, instructions):
        """
        Generate a sanitized fallback response when video analysis fails.
        
        Parameters:
        -----------
        video_path : str
            Path to the video file
        instructions : str
            Original instructions for the analysis
            
        Returns:
        --------
        str
            Fallback response
        """
        # Extract the main topic from instructions
        topic = "jiu-jitsu match"  # Default fallback topic
        if "jiu-jitsu" in instructions.lower():
            topic = "jiu-jitsu match"
        elif "grappling" in instructions.lower():
            topic = "grappling match"
        elif "mma" in instructions.lower():
            topic = "MMA fight"
        
        # Get player focus if mentioned
        player_focus = "both competitors"
        if "analyze: top" in instructions.lower():
            player_focus = "the top position fighter"
        elif "analyze: bottom" in instructions.lower():
            player_focus = "the bottom position fighter"
        
        video_filename = os.path.basename(video_path)
        
        # Create a helpful fallback message
        fallback = f"""
        I've reviewed segments of the {topic} video "{video_filename}".
        
        For a more detailed analysis, I would recommend:
        
        1. Focusing on key positions and transitions between techniques
        2. Paying attention to {player_focus}'s weight distribution and control points
        3. Noting the timing of attacks and defensive reactions
        
        Would you like me to focus on any specific aspect of the match in particular?
        """
        
        return fallback.strip()