import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Importa los blueprints
from aivolutioncoach.routes.chat import chat_bp
from aivolutioncoach.routes.report import report_bp

def create_app():
    load_dotenv()  # Carga variables de entorno

    app = Flask(__name__)
    CORS(app)

    # Registrar blueprints
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(report_bp, url_prefix='/api')

    # Configuraciones adicionales, inicialización de extensiones, DB, etc.
    # ...
    
    return app