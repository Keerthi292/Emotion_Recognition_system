from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import logging
from datetime import datetime
import numpy as np

# Import AI model modules
from models.text_analyzer import TextEmotionAnalyzer
from models.audio_analyzer import AudioEmotionAnalyzer
from models.visual_analyzer import VisualEmotionAnalyzer
from utils.emotion_combiner import EmotionCombiner
from utils.config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler('logs/emotion_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Initialize models
text_analyzer = None
audio_analyzer = None
visual_analyzer = None
emotion_combiner = None

def initialize_models():
    global text_analyzer, audio_analyzer, visual_analyzer, emotion_combiner
    try:
        logger.info("Initializing AI Emotion Detection System v9.0...")
        text_analyzer = TextEmotionAnalyzer()
        audio_analyzer = AudioEmotionAnalyzer()
        visual_analyzer = VisualEmotionAnalyzer()
        emotion_combiner = EmotionCombiner()
        logger.info("All AI models loaded successfully.")
        return True
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        return False

# Convert NumPy types to native Python types
def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

@app.route('/health', methods=['GET'])
def health_check():
    try:
        return jsonify({
            'status': 'healthy',
            'version': '9.0.0',
            'message': 'AI Emotion Detection System is running',
            'timestamp': datetime.now().isoformat(),
            'models_loaded': {
                'text_analyzer': text_analyzer is not None,
                'audio_analyzer': audio_analyzer is not None,
                'visual_analyzer': visual_analyzer is not None,
                'emotion_combiner': emotion_combiner is not None
            },
            'supported_formats': {
                'audio': list(Config.ALLOWED_EXTENSIONS['audio']),
                'image': list(Config.ALLOWED_EXTENSIONS['image']),
                'text': list(Config.ALLOWED_EXTENSIONS['text'])
            }
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_emotions():
    try:
        start_time = datetime.now()
        results = {
            'version': '9.0.0',
            'timestamp': start_time.isoformat(),
            'analysis_id': f"analysis_{int(start_time.timestamp())}"
        }

        # Text input
        if 'text' in request.form and request.form['text'].strip():
            text = request.form['text']
            logger.info(f"Analyzing text: {len(text)} characters")
            results['text_emotions'] = convert_numpy(text_analyzer.analyze_emotion(text)) if text_analyzer else []

        # Audio input
        if 'audio' in request.files:
            audio_file = request.files['audio']
            if audio_file and Config.allowed_file(audio_file.filename, 'audio'):
                logger.info(f"Analyzing audio: {audio_file.filename}")
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio:
                    tmp_path = tmp_audio.name
                    audio_file.save(tmp_path)
                try:
                    results['audio_emotions'] = convert_numpy(audio_analyzer.analyze_emotion(tmp_path)) if audio_analyzer else []
                finally:
                    try:
                        os.remove(tmp_path)
                    except Exception as e:
                        logger.warning(f"Audio file deletion failed: {e}")

        # Image input
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and Config.allowed_file(image_file.filename, 'image'):
                logger.info(f"Analyzing image: {image_file.filename}")
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_image:
                        tmp_path = tmp_image.name
                        image_file.save(tmp_path)
                        tmp_image.close()  # Ensure file is flushed
                    if visual_analyzer:
                        processed = visual_analyzer.preprocess_image(tmp_path)
                        if processed:
                            results['visual_emotions'] = convert_numpy(visual_analyzer.analyze_emotion(processed))
                            os.remove(processed)
                        else:
                            logger.warning("Image preprocessing failed.")
                            results['visual_emotions'] = []
                    else:
                        results['visual_emotions'] = []
                except Exception as e:
                    logger.error(f"Image analysis failed: {e}")
                    results['visual_emotions'] = []
                finally:
                    try:
                        os.remove(tmp_path)
                    except Exception as e:
                        logger.warning(f"Image file deletion failed: {e}")

        # Combined emotion
        if emotion_combiner:
            combined = emotion_combiner.combine_emotions(
                results.get('text_emotions', []),
                results.get('audio_emotions', []),
                results.get('visual_emotions', [])
            )
            results['combined_emotions'] = convert_numpy(combined)

        results['processing_time'] = f"{(datetime.now() - start_time).total_seconds():.2f}s"
        logger.info(f"Analysis complete in {results['processing_time']}")
        return jsonify(results)

    except Exception as e:
        logger.error(f"Error in analyze_emotions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/models/status', methods=['GET'])
def models_status():
    try:
        return jsonify({
            'text_analyzer': {
                'loaded': text_analyzer is not None,
                'model_name': getattr(text_analyzer, 'model_name', None),
                'status': 'ready' if text_analyzer else 'not_loaded'
            },
            'audio_analyzer': {
                'loaded': audio_analyzer is not None,
                'model_name': getattr(audio_analyzer, 'model_name', None),
                'status': 'ready' if audio_analyzer else 'not_loaded'
            },
            'visual_analyzer': {
                'loaded': visual_analyzer is not None,
                'emotion_labels': getattr(visual_analyzer, 'emotion_labels', None),
                'status': 'ready' if visual_analyzer else 'not_loaded'
            },
            'emotion_combiner': {
                'loaded': emotion_combiner is not None,
                'strategy': getattr(emotion_combiner, 'strategy', 'weighted_average'),
                'status': 'ready' if emotion_combiner else 'not_loaded'
            }
        })
    except Exception as e:
        logger.error(f"Model status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def file_too_large(e):
    return jsonify({
        'error': 'File too large',
        'max_size': f"{Config.MAX_CONTENT_LENGTH / (1024*1024):.0f}MB"
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/health', '/analyze', '/models/status']
    }), 404

if __name__ == '__main__':
    print("Starting AI Emotion Detection System v9.0...")
    print("=" * 60)
    Config.init_directories()
    os.makedirs('logs', exist_ok=True)
    if initialize_models():
        print("All models loaded successfully.")
        print(f"Server running at: http://{Config.HOST}:{Config.PORT}")
        print("=" * 60)
        app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT, threaded=True)
    else:
        print("Failed to load models. Run: cd backend && python setup.py")
        exit(1)
