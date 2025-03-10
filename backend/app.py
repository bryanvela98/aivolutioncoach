from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Azure Cognitive Services configuration
SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')

@app.route('/api/support', methods=['POST'])
def process_support_request():
    data = request.json
    # AI-powered support logic here
    return jsonify({
        "status": "success",
        "message": "Support request processed"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)