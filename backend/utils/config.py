"""
Configuration settings for the emotion detection system
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for the application"""
    
    # Flask settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/temp')
    ALLOWED_EXTENSIONS = {
        'audio': {'wav', 'mp3', 'flac', 'm4a', 'ogg'},
        'image': {'jpg', 'jpeg', 'png', 'bmp', 'gif'},
        'text': {'txt'}
    }
    
    # Model settings
    MODELS = {
        'text': {
            'name': 'j-hartmann/emotion-english-distilroberta-base',
            'cache_dir': 'data/models/text'
        },
        'audio': {
            'sample_rate': 16000,
            'cache_dir': 'data/models/audio'
        },
        'visual': {
            'cache_dir': 'data/models/visual'
        }
    }
    
    # Emotion combination weights
    EMOTION_WEIGHTS = {
        'text': 0.4,
        'audio': 0.3,
        'visual': 0.3
    }
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @staticmethod
    def init_directories():
        """Create necessary directories"""
        directories = [
            Config.UPLOAD_FOLDER,
            Config.MODELS['text']['cache_dir'],
            Config.MODELS['audio']['cache_dir'],
            Config.MODELS['visual']['cache_dir']
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def allowed_file(filename: str, file_type: str) -> bool:
        """Check if file extension is allowed"""
        if '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in Config.ALLOWED_EXTENSIONS.get(file_type, set())
