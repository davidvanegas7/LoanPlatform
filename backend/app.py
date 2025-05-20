from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity, jwt_required, get_jwt
import os
from dotenv import load_dotenv
from flasgger import Swagger
from functools import wraps
import werkzeug.datastructures
import logging
from config.celery_config import celery_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Import routes
from routes.auth import auth_bp
from routes.loan_applications import loan_app_bp
from routes.loans import loan_bp
from routes.payments import payment_bp

app = Flask(__name__)
celery_app.conf.update(app.config)

# CORS configuration with more specific settings
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "https://loantrackerapp.davidvanegasdev.com"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
         "expose_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True,
         "max_age": 86400
     }})

# JSON configuration to use UTF-8
app.config['JSON_AS_ASCII'] = False

# JWT configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_secret_key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 36000))
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
# Additional configurations for debugging
app.config["JWT_ERROR_MESSAGE_KEY"] = "error"
app.config["JWT_DECODE_LEEWAY"] = 10  # Give 10 seconds margin for token expiration

# Swagger configuration
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

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Loan Platform API",
        "description": "API for loan application, approval, and management",
        "contact": {
            "responsibleOrganization": "Loan Platform",
            "email": "david.vanegas.92@gmail.com"
        },
        "version": "1.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

logger.info(f"JWT Configuration: JWT_SECRET_KEY={app.config['JWT_SECRET_KEY'][:3]}..., JWT_ACCESS_TOKEN_EXPIRES={app.config['JWT_ACCESS_TOKEN_EXPIRES']}")

jwt = JWTManager(app)

# JWT error handlers with detailed logs
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    logger.error(f"Expired token. Payload: {jwt_payload}")
    return jsonify({
        'error': 'Access token has expired',
        'message': 'Please login again'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    logger.error(f"Invalid token. Error: {error}")
    return jsonify({
        'error': 'Invalid access token',
        'message': 'Authentication failed'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    logger.error(f"Missing token. Error: {error}")
    return jsonify({
        'error': 'Missing access token',
        'message': 'Authentication required'
    }), 401

@jwt.token_verification_failed_loader
def token_verification_callback():
    logger.error("Token verification failed.")
    return jsonify({
        'error': 'Token verification failed',
        'message': 'Token could not be verified'
    }), 401

# Function to process authentication header and accept tokens with or without Bearer
def process_auth_header():
    # If there is an authorization header and it doesn't have the 'Bearer ' prefix
    auth_header = request.headers.get('Authorization')
    if auth_header:
        logger.info(f"Auth header received: {auth_header[:20] if auth_header else 'None'}...")
        if not auth_header.startswith('Bearer '):
            # Create a mutable copy of the headers
            patched_headers = werkzeug.datastructures.Headers(request.headers)
            # Add the 'Bearer ' prefix to the token
            patched_headers['Authorization'] = f'Bearer {auth_header}'
            # Save the original headers
            request.orig_headers = request.headers
            # Replace the headers
            request.headers = patched_headers
            logger.info(f"Added 'Bearer' prefix to token: {patched_headers['Authorization'][:20]}...")

# Apply processing on each request
@app.before_request
def before_request():
    # Log information about the request for debugging
    logger.info(f"New request: {request.method} {request.path}")
    for key, value in request.headers.items():
        # Hide the full token to avoid security issues in logs
        if key.lower() == 'authorization':
            # Show only the first 20 characters of the token
            if value and len(value) > 20:
                logger.info(f"Header - {key}: {value[:20]}...[truncated]")
            else:
                logger.info(f"Header - {key}: {value}")
        else:
            logger.info(f"Header - {key}: {value}")
    
    # Routes excluded from JWT verification
    excluded_routes = [
        '/',  # Main route
        '/docs/',  # Swagger documentation
        '/docs',  # Swagger documentation alternate
        '/apispec.json',  # Swagger specification
        '/flasgger_static',  # Swagger static files
        '/static'  # Additional static files
    ]
    
    excluded_prefixes = [
        '/api/v1/auth/login',  # Login endpoint
        '/api/v1/auth/register',  # Register endpoint
        '/flasgger_static/',  # Everything in flasgger_static
        'api/v1/payments/generate-ach-file',
        'api/v1/payments/process-return-file',
        'api/v1/payments/create-ach-batch',
    ]
    
    # Check if the current route is excluded
    current_path = request.path
    
    # Check exact routes
    if any(current_path == route for route in excluded_routes):
        logger.info(f"Route excluded from verification: {current_path}")
        return  # Do not process for excluded routes
    
    # Check prefixes
    if any(current_path.startswith(prefix) for prefix in excluded_prefixes):
        logger.info(f"Route with excluded prefix from verification: {current_path}")
        return  # Do not process for routes with excluded prefixes
    
    # Process the authorization header to add 'Bearer' if necessary
    process_auth_header()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(loan_app_bp, url_prefix='/api/v1/loan-applications')
app.register_blueprint(loan_bp, url_prefix='/api/v1/loans')
app.register_blueprint(payment_bp, url_prefix='/api/v1/payments')

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
              example: Welcome to the Loan Platform API! Do you want to see the docs? /docs/
            auth_info:
              type: string
              description: Authentication information
              example: This API requires JWT authentication. Get your token by using the /api/v1/auth/login endpoint.
            auth_example:
              type: string
              description: Authorization example
              example: "To authenticate, add the following header to your requests: Authorization: Bearer your_jwt_token"
    """
    return jsonify({
        "message": "Welcome to the Loan Platform API! Do you want to see the docs? /docs/",
        "auth_info": "This API requires JWT authentication. Get your token by using the /api/v1/auth/login endpoint.",
        "auth_example": "To authenticate, add the following header to your requests: Authorization: Bearer your_jwt_token"
    })

@app.route('/api/test-auth')
def test_auth():
    """
    Test authentication route
    ---
    tags:
      - Test
    security:
      - Bearer: []
    responses:
      200:
        description: Authentication successful
        schema:
          properties:
            message:
              type: string
              description: Success message
              example: Authentication successful
            user_id:
              type: integer
              description: ID of the authenticated user
              example: 1
            token_info:
              type: object
              description: Information about the token
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid access token
    """
    # Get the token manually for debugging
    auth_header = request.headers.get('Authorization')
    logger.info(f"Test-auth called with Auth header: {auth_header[:20] if auth_header else 'None'}...")
    
    try:
        # Try to extract and verify the token manually
        if not auth_header:
            return jsonify({"error": "No authentication token provided"}), 401
        
        # If it contains "Bearer ", extract it
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header
        
        logger.info(f"Extracted token: {token[:20]}...")
        
        try:
            # Verify the token using JWT decorators
            verify_jwt_in_request()
            user_id_str = get_jwt_identity()
            try:
                user_id = int(user_id_str)
                user_id_type = "int (converted from string)"
            except (TypeError, ValueError):
                user_id = user_id_str
                user_id_type = "string (not convertible to int)"
            
            jwt_data = get_jwt()
            
            logger.info(f"JWT verification successful for user ID: {user_id} (type: {user_id_type})")
            
            return jsonify({
                "message": "Authentication successful",
                "user_id": user_id,
                "user_id_original": user_id_str,
                "user_id_type": user_id_type,
                "token_info": jwt_data
            })
        except Exception as jwt_error:
            logger.error(f"Error in standard JWT verification: {str(jwt_error)}")
            
            # Try to decode the token manually
            import jwt
            try:
                # Decode manually with the same settings
                decoded = jwt.decode(
                    token,
                    app.config["JWT_SECRET_KEY"],
                    algorithms=["HS256"],
                    leeway=app.config["JWT_DECODE_LEEWAY"]
                )
                logger.info(f"Manual decoding successful: {decoded}")
                return jsonify({
                    "message": "Manual authentication successful",
                    "token_info": decoded,
                    "note": "The token was decoded manually, not through flask-jwt-extended"
                })
            except Exception as manual_error:
                logger.error(f"Error in manual decoding: {str(manual_error)}")
                return jsonify({
                    "error": "Error verifying token",
                    "jwt_error": str(jwt_error),
                    "manual_error": str(manual_error)
                }), 401
    
    except Exception as e:
        logger.error(f"General error in test-auth: {str(e)}")
        return jsonify({"error": f"General error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 