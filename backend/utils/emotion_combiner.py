"""
Emotion Combiner Utility
Combines emotions from multiple modalities (text, audio, visual)
"""

import logging
from typing import List, Dict, Optional

class EmotionCombiner:
    def __init__(self):
        """Initialize emotion combiner"""
        self.logger = logging.getLogger(__name__)
        self.default_weights = {
            'text': 0.4,
            'audio': 0.3,
            'visual': 0.3
        }
    
    def combine_emotions(self, 
                        text_emotions: List[Dict[str, float]] = None,
                        audio_emotions: List[Dict[str, float]] = None,
                        visual_emotions: List[Dict[str, float]] = None,
                        weights: Dict[str, float] = None) -> List[Dict[str, float]]:
        """
        Combine emotions from multiple modalities using weighted average
        
        Args:
            text_emotions: List of text emotion results
            audio_emotions: List of audio emotion results  
            visual_emotions: List of visual emotion results
            weights: Custom weights for each modality
            
        Returns:
            List[Dict]: Combined emotion results
        """
        try:
            if weights is None:
                weights = self.default_weights
            
            # Collect all emotions
            emotion_sources = {}
            if text_emotions:
                emotion_sources['text'] = text_emotions
            if audio_emotions:
                emotion_sources['audio'] = audio_emotions
            if visual_emotions:
                emotion_sources['visual'] = visual_emotions
            
            if not emotion_sources:
                return []
            
            # Get all unique emotions
            unique_emotions = set()
            for emotions in emotion_sources.values():
                for emotion in emotions:
                    unique_emotions.add(emotion['emotion'])
            
            # Calculate weighted average for each emotion
            combined_emotions = {}
            for emotion in unique_emotions:
                total_weight = 0
                weighted_sum = 0
                
                for source, emotions in emotion_sources.items():
                    # Find emotion score in this source
                    emotion_score = next(
                        (e['confidence'] for e in emotions if e['emotion'] == emotion), 
                        0
                    )
                    
                    if emotion_score > 0:
                        weighted_sum += emotion_score * weights.get(source, 0)
                        total_weight += weights.get(source, 0)
                
                if total_weight > 0:
                    combined_emotions[emotion] = weighted_sum / total_weight
            
            # Convert to list and sort
            result = [
                {'emotion': emotion, 'confidence': confidence}
                for emotion, confidence in combined_emotions.items()
            ]
            result = sorted(result, key=lambda x: x['confidence'], reverse=True)
            
            self.logger.info(f"Combined emotions from {len(emotion_sources)} sources")
            return result
            
        except Exception as e:
            self.logger.error(f"Error combining emotions: {e}")
            return []
    
    def normalize_emotions(self, emotions: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """
        Normalize emotion confidences to sum to 100
        
        Args:
            emotions: List of emotion results
            
        Returns:
            List[Dict]: Normalized emotion results
        """
        try:
            if not emotions:
                return []
            
            total_confidence = sum(e['confidence'] for e in emotions)
            if total_confidence == 0:
                return emotions
            
            normalized = []
            for emotion in emotions:
                normalized.append({
                    'emotion': emotion['emotion'],
                    'confidence': (emotion['confidence'] / total_confidence) * 100
                })
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizing emotions: {e}")
            return emotions
    
    def filter_top_emotions(self, emotions: List[Dict[str, float]], top_k: int = 5) -> List[Dict[str, float]]:
        """
        Filter to keep only top K emotions
        
        Args:
            emotions: List of emotion results
            top_k: Number of top emotions to keep
            
        Returns:
            List[Dict]: Filtered emotion results
        """
        try:
            sorted_emotions = sorted(emotions, key=lambda x: x['confidence'], reverse=True)
            return sorted_emotions[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error filtering emotions: {e}")
            return emotions
