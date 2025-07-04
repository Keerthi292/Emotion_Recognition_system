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
import traceback

class VisualEmotionAnalyzer:
    def __init__(self):
        """Initialize DeepFace visual emotion analyzer"""
        self.logger = logging.getLogger(__name__)
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    
    def analyze_emotion(self, image_path: str) -> List[Dict[str, float]]:
        """
        Analyze facial emotions in image using DeepFace
        """
        try:
            # Preprocess image first
            processed_path = self.preprocess_image(image_path)
            if not processed_path or not os.path.exists(processed_path):
                self.logger.error("Image preprocessing failed or file doesn't exist.")
                return self._get_default_emotions()

            # Confirm image is readable
            if cv2.imread(processed_path) is None:
                self.logger.error(f"OpenCV could not read image at: {processed_path}")
                return self._get_default_emotions()

            # DeepFace emotion analysis
            result = DeepFace.analyze(
                img_path=processed_path,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )

            # Extract emotions
            emotions_dict = result[0]['emotion'] if isinstance(result, list) else result['emotion']
            emotions = [
                {'emotion': emotion.lower(), 'confidence': round(confidence, 2)}
                for emotion, confidence in emotions_dict.items()
            ]
            emotions = sorted(emotions, key=lambda x: x['confidence'], reverse=True)

            # Log and return
            self.logger.info(f"Visual emotion analysis completed. Top: {emotions[0]['emotion']} ({emotions[0]['confidence']}%)")
            return emotions

        except Exception as e:
            self.logger.error(f"Error analyzing visual emotion: {e}")
            self.logger.debug("Traceback:\n%s", traceback.format_exc())
            return self._get_default_emotions()

    def _get_default_emotions(self) -> List[Dict[str, float]]:
        """
        Return default emotion distribution when analysis fails
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
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                self.logger.error(f"Cannot read image for preprocessing: {image_path}")
                return None

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            height, width = img_rgb.shape[:2]
            if width > 1024 or height > 1024:
                scale = min(1024 / width, 1024 / height)
                img_rgb = cv2.resize(img_rgb, (int(width * scale), int(height * scale)))

            temp_path = tempfile.mktemp(suffix='.jpg')
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            cv2.imwrite(temp_path, img_bgr)

            return temp_path

        except Exception as e:
            self.logger.error(f"Error preprocessing image: {e}")
            self.logger.debug("Traceback:\n%s", traceback.format_exc())
            return None

    def detect_faces(self, image_path: str) -> int:
        """
        Detect number of faces in image
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                self.logger.warning(f"OpenCV failed to read image for face detection: {image_path}")
                return 0

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            self.logger.info(f"Detected {len(faces)} face(s) in image")
            return len(faces)

        except Exception as e:
            self.logger.error(f"Error detecting faces: {e}")
            self.logger.debug("Traceback:\n%s", traceback.format_exc())
            return 0
