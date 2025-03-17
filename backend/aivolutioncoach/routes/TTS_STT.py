from flask import Blueprint, jsonify, request
from aivolutioncoach.services.speech_utils import SpeechService

speech_bp = Blueprint('speech', __name__)
speech_service = SpeechService()

@speech_bp.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        command = speech_service.transcribe_command()
        return jsonify({'success': True, 'command': command})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@speech_bp.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        speech_service.speak_output(text)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500