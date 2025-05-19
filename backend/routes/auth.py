from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
import json
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
user_model = User()

# Create necessary tables on startup
@auth_bp.before_app_first_request
def setup_db():
    user_model.create_tables()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User Registration
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              description: User email
              example: user@example.com
            password:
              type: string
              description: User password
              example: password123
            first_name:
              type: string
              description: User first name
              example: John
            last_name:
              type: string
              description: User last name
              example: Doe
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: User registered successfully
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                email:
                  type: string
                  example: user@example.com
                first_name:
                  type: string
                  example: John
                last_name:
                  type: string
                  example: Doe
                role:
                  type: string
                  example: user
            access_token:
              type: string
              description: JWT token to use for authentication. IMPORTANT! You must add 'Bearer ' prefix before this token in the Authorization header.
              example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
      400:
        description: Error in provided data
        schema:
          type: object
          properties:
            error:
              type: string
              example: Email is already registered
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Internal server error
    """
    try:
        data = request.get_json()
        logger.info(f"Register request with data: {data}")
        
        # Validate required data
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400
        
        # Create user
        user_data = user_model.create_user(
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            role=data.get('role', 'user')
        )
        
        if "error" in user_data:
            logger.error(f"Error creating user: {user_data['error']}")
            return jsonify({"error": user_data["error"]}), 400
        
        # Generate JWT token - convertir ID a string para evitar errores
        user_id_str = str(user_data['id'])
        access_token = create_access_token(identity=user_id_str)
        logger.info(f"User registered successfully with ID: {user_data['id']} (string: {user_id_str})")
        
        return jsonify({
            "message": "User registered successfully",
            "user": user_data,
            "access_token": access_token
        }), 201
        
    except Exception as e:
        logger.error(f"Exception in register: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User Login
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              description: User email
              example: user@example.com
            password:
              type: string
              description: User password
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                email:
                  type: string
                  example: user@example.com
                first_name:
                  type: string
                  example: John
                last_name:
                  type: string
                  example: Doe
                role:
                  type: string
                  example: user
            access_token:
              type: string
              description: JWT token to use for authentication. IMPORTANT! You must add 'Bearer ' prefix before this token in the Authorization header. Example format 'Bearer eyJhbGciOiJ...'
              example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
            token_info:
              type: object
              description: Información detallada sobre el token
              properties:
                expires_in:
                  type: integer
                  example: 36000
                issued_at:
                  type: string
                  example: "2025-05-15T12:00:00Z"
                expires_at:
                  type: string
                  example: "2025-05-15T13:00:00Z"
      400:
        description: Missing required data
        schema:
          type: object
          properties:
            error:
              type: string
              example: Email and password are required
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid credentials
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Internal server error
    """
    try:
        data = request.get_json()
        logger.info(f"Login request with email: {data.get('email')}")
        
        # Validate required data
        if not data or not data.get('email') or not data.get('password'):
            logger.warning("Missing email or password in login request")
            return jsonify({"error": "Email and password are required"}), 400
        
        # Verify credentials
        user = user_model.verify_user(
            email=data.get('email'),
            password=data.get('password')
        )
        
        if not user:
            logger.warning(f"Invalid credentials for email: {data.get('email')}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Generate JWT token
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        expires = now + datetime.timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 36000)))
        
        # Convertir el ID de usuario a string para evitar el error "Subject must be a string"
        user_id_str = str(user['id'])
        access_token = create_access_token(identity=user_id_str)
        
        logger.info(f"Login successful for user ID: {user['id']} (string: {user_id_str})")
        logger.info(f"Generated token: {access_token}")
        logger.info(f"Token issued at: {now}")
        logger.info(f"Token expires at: {expires}")
        
        return jsonify({
            "message": "Login successful",
            "user": user,
            "access_token": access_token,
            "token_info": {
                "expires_in": int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 36000)),
                "issued_at": now.isoformat(),
                "expires_at": expires.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in login: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    """
    Get User Profile
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: User profile retrieved successfully
        schema:
          type: object
          properties:
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                email:
                  type: string
                  example: user@example.com
                first_name:
                  type: string
                  example: John
                last_name:
                  type: string
                  example: Doe
                role:
                  type: string
                  example: user
                phone:
                  type: string
                  example: "123-456-7890"
      401:
        description: Missing or invalid JWT token
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        # Obtener el ID del usuario desde el token JWT
        current_user_id = get_jwt_identity()
        logger.info(f"Fetching profile for user ID: {current_user_id}")
        
        # Convertir a entero si es necesario
        try:
            current_user_id = int(current_user_id)
        except ValueError:
            pass
        
        # Obtener datos del usuario
        user = user_model.get_user_by_id(current_user_id)
        
        if not user:
            logger.warning(f"User not found with ID: {current_user_id}")
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Asegurar que no enviamos la contraseña
        if 'password' in user:
            del user['password']
        
        logger.info(f"Profile retrieved successfully for user ID: {current_user_id}")
        return jsonify({
            "user": user
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in get_user_profile: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """
    Update User Profile
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            first_name:
              type: string
              description: User first name
              example: John
            last_name:
              type: string
              description: User last name
              example: Doe
            language:
              type: string
              description: User preferred language
              example: "en"
    responses:
      200:
        description: User profile updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Profile updated successfully
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                email:
                  type: string
                  example: user@example.com
                first_name:
                  type: string
                  example: John
                last_name:
                  type: string
                  example: Doe
                role:
                  type: string
                  example: user
                language:
                  type: string
                  example: "en"
      400:
        description: Error in provided data
      401:
        description: Missing or invalid JWT token
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        # Obtener el ID del usuario desde el token JWT
        current_user_id = get_jwt_identity()
        logger.info(f"Updating profile for user ID: {current_user_id}")
        
        # Convertir a entero si es necesario
        try:
            current_user_id = int(current_user_id)
        except ValueError:
            pass
        
        # Obtener datos a actualizar
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400
        
        # Verificar si el usuario existe
        user = user_model.get_user_by_id(current_user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Actualizar usuario
        updated_user = user_model.update_user(current_user_id, data)
        
        if "error" in updated_user:
            return jsonify({"error": updated_user["error"]}), 400
        
        logger.info(f"Profile updated successfully for user ID: {current_user_id}")
        return jsonify({
            "message": "Perfil actualizado correctamente",
            "user": updated_user
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in update_user_profile: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_language():
    """
    Update User Language Setting
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - language
          properties:
            language:
              type: string
              description: User preferred language
              example: "en"
    responses:
      200:
        description: Language setting updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Language updated successfully
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                language:
                  type: string
                  example: "en"
      400:
        description: Error in provided data
      401:
        description: Missing or invalid JWT token
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        # Obtener el ID del usuario desde el token JWT
        current_user_id = get_jwt_identity()
        logger.info(f"Updating language for user ID: {current_user_id}")
        
        # Convertir a entero si es necesario
        try:
            current_user_id = int(current_user_id)
        except ValueError:
            pass
        
        # Obtener datos a actualizar
        data = request.get_json()
        if not data or 'language' not in data:
            return jsonify({"error": "No se proporcionó el idioma para actualizar"}), 400
        
        # Verificar si el usuario existe
        user = user_model.get_user_by_id(current_user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Actualizar idioma
        updated_user = user_model.update_language(current_user_id, data['language'])
        
        if "error" in updated_user:
            return jsonify({"error": updated_user["error"]}), 400
        
        logger.info(f"Language updated successfully for user ID: {current_user_id}")
        return jsonify({
            "message": "Idioma actualizado correctamente",
            "user": updated_user
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in update_language: {str(e)}")
        return jsonify({"error": str(e)}), 500

