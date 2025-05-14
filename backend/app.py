from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from flasgger import Swagger

# Cargar variables de entorno desde .env
load_dotenv()

# Importar routes
from routes.auth import auth_bp

app = Flask(__name__)

# Configuración de CORS
CORS(app)

# Configuración de JSON para usar UTF-8
app.config['JSON_AS_ASCII'] = False

# Configuración de JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_secret_key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))
jwt = JWTManager(app)

# Configuración de Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "Loan Platform API",
        "description": "API for business loan management",
        "version": "1.0.0",
        "contact": {
            "email": "david.vanegas.92@gmail.com"
        }
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Add JWT token with Bearer prefix"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=template)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

@app.route('/')
def hello():
    """
    Main API route
    ---
    responses:
      200:
        description: Welcome message
        schema:
          properties:
            message:
              type: string
              description: Welcome message
              example: Welcome to the Loan Platform API! Do you want to see the docs? /docs
    """
    return jsonify({"message": "Welcome to the Loan Platform API! Do you want to see the docs? /docs"})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 