from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from assistant_ai import AIvolutionCoachChat

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Azure Cognitive Services configuration
SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')

# Initialize AIvolutionCoachChat as a global variable
coach = AIvolutionCoachChat()

@app.route('/api/support', methods=['POST'])
def process_support_request():
    data = request.json
    # AI-powered support logic here
    return jsonify({
        "status": "success",
        "message": "Support request processed"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({
                "status": "error",
                "message": "No message provided"
            }), 400

        user_message = data['message']
        
        # Obtener respuesta del coach
        response = coach.search_and_answer(user_message)
        
        return jsonify({
            "status": "success",
            "response": response,
            "conversation_history": coach.conversation_history
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/chat/reset', methods=['POST'])
def reset_chat():
    try:
        # Reiniciar el histórico de conversación
        coach.conversation_history = []
        
        return jsonify({
            "status": "success",
            "message": "Chat history reset successfully"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)