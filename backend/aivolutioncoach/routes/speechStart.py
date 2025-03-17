from flask import Blueprint, jsonify, request
from aivolutioncoach.services.speech_utils import SpeechService

speech_bp = Blueprint('speech', __name__)
speech_service = SpeechService()

@speech_bp.route('/api/speech-to-text-start', methods=['POST'])
def speech_to_text():
    try:
        command = speech_service.transcribe_command()
        if command.lower() == "start.":
            return jsonify({'success': True, 'message': 'Start command recognized', 'command': command})
        else:
            return jsonify({'success': False, 'message': 'Waiting for "Start" command', 'command': command})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@speech_bp.route('/api/text-to-speech-start', methods=['POST'])
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