"""
Text Emotion Analysis using BERT v9.0
Handles text input and returns emotion classifications
"""

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import logging
from typing import List, Dict
import torch

class TextEmotionAnalyzer:
    def __init__(self):
        """Initialize BERT-based text emotion analyzer"""
        self.logger = logging.getLogger(__name__)
        self.model_name = "j-hartmann/emotion-english-distilroberta-base"
        self.tokenizer = None
        self.model = None
        self.classifier = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()
    
    def load_model(self):
        """Load the pretrained BERT model for emotion classification"""
        try:
            self.logger.info(f"Loading BERT model for text emotion analysis on {self.device}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            self.classifier = pipeline(
                "text-classification", 
                model=self.model, 
                tokenizer=self.tokenizer,
                return_all_scores=True,
                device=0 if self.device == "cuda" else -1
            )
            
            self.logger.info("✅ BERT model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading BERT model: {e}")
            raise
    
    def analyze_emotion(self, text: str) -> List[Dict[str, float]]:
        """
        Analyze emotions in text using BERT
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            List[Dict]: List of emotions with confidence scores
        """
        try:
            if not text or not text.strip():
                return []
            
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Get predictions from BERT
            results = self.classifier(processed_text)
            
            # Format results
            emotions = []
            for result in results[0]:  # results is a list of lists
                emotions.append({
                    'emotion': result['label'].lower(),
                    'confidence': result['score'] * 100
                })
            
            # Sort by confidence
            emotions = sorted(emotions, key=lambda x: x['confidence'], reverse=True)
            
            self.logger.info(f"Text emotion analysis completed. Top emotion: {emotions[0]['emotion']} ({emotions[0]['confidence']:.1f}%)")
            return emotions
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing text emotion: {e}")
            return []
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better emotion detection
        
        Args:
            text (str): Raw input text
            
        Returns:
            str: Preprocessed text
        """
        # Basic preprocessing
        text = text.strip()
        # Remove excessive whitespace
        text = ' '.join(text.split())
        # Limit length for BERT (512 tokens max)
        if len(text) > 500:
            text = text[:500]
        return text
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'tokenizer_vocab_size': len(self.tokenizer) if self.tokenizer else 0,
            'model_parameters': sum(p.numel() for p in self.model.parameters()) if self.model else 0
        }
