from flask import Blueprint, request, jsonify
from aivolutioncoach.services.coach import AIvolutionCoachChat

chat_bp = Blueprint('chat', __name__)

# Instancia única o compartida de la clase AIvolutionCoachChat
coach = AIvolutionCoachChat()

@chat_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"status": "error", "message": "No message provided"}), 400

        user_message = data['message']
        response = coach.search_and_answer(user_message)

        return jsonify({
            "status": "success",
            "response": response,
            "conversation_history": coach.conversation_history
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@chat_bp.route('/chat/reset', methods=['POST'])
def reset_chat():
    try:
        coach.conversation_history = []
        return jsonify({"status": "success", "message": "Chat history reset successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500