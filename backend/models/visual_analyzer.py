"""
Visual Emotion Analysis using DeepFace
Handles image input and returns facial emotion classifications
"""

from deepface import DeepFace
import cv2
import numpy as np
import logging
from typing import List, Dict, Optional
import tempfile 
import os

class VisualEmotionAnalyzer:
    def __init__(self):
        """Initialize DeepFace visual emotion analyzer"""
        self.logger = logging.getLogger(__name__)
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    
    def analyze_emotion(self, image_path: str) -> List[Dict[str, float]]:
        """
        Analyze facial emotions in image using DeepFace
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            List[Dict]: List of emotions with confidence scores
        """
        try:
            # Analyze the image using DeepFace
            result = DeepFace.analyze(
                img_path=image_path, 
                actions=['emotion'], 
                enforce_detection=False,
                silent=True
            )
            
            # Extract emotions
            if isinstance(result, list):
                emotions_dict = result[0]['emotion']
            else:
                emotions_dict = result['emotion']
            
            # Convert to our format
            emotions = []
            for emotion, confidence in emotions_dict.items():
                emotions.append({
                    'emotion': emotion.lower(),
                    'confidence': confidence
                })
            
            # Sort by confidence
            emotions = sorted(emotions, key=lambda x: x['confidence'], reverse=True)
            
            self.logger.info(f"Visual emotion analysis completed. Top emotion: {emotions[0]['emotion']}")
            return emotions
            
        except Exception as e:
            self.logger.error(f"Error analyzing visual emotion: {e}")
            # Return default emotions if analysis fails
            return self._get_default_emotions()
    
    def _get_default_emotions(self) -> List[Dict[str, float]]:
        """
        Return default emotion distribution when analysis fails
        
        Returns:
            List[Dict]: Default emotion classifications
        """
        default_emotions = {
            'neutral': 40,
            'happy': 25,
            'surprise': 15,
            'fear': 10,
            'sad': 5,
            'angry': 3,
            'disgust': 2
        }
        
        return [{'emotion': k, 'confidence': v} for k, v in default_emotions.items()]
    
    def preprocess_image(self, image_path: str) -> Optional[str]:
        """
        Preprocess image for better emotion detection
        
        Args:
            image_path (str): Path to input image
            
        Returns:
            str: Path to preprocessed image or None if error
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Convert to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize if too large
            height, width = img_rgb.shape[:2]
            if width > 1024 or height > 1024:
                scale = min(1024/width, 1024/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img_rgb = cv2.resize(img_rgb, (new_width, new_height))
            
            # Save preprocessed image
            temp_path = tempfile.mktemp(suffix='.jpg')
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            cv2.imwrite(temp_path, img_bgr)
            
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {e}")
            return None
    
    def detect_faces(self, image_path: str) -> int:
        """
        Detect number of faces in image
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            int: Number of faces detected
        """
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Use OpenCV's face detector
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)          
            return len(faces)
            
        except Exception as e:
            self.logger.error(f"Error detecting faces: {e}")
            return 0
