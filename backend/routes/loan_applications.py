from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
import logging
from models.loan_application import LoanApplication

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

loan_app_bp = Blueprint('loan_applications', __name__)
loan_app_model = LoanApplication()

@loan_app_bp.route('', methods=['POST'])
@jwt_required()
def create_loan_application():
    """
    Create a new loan application
    ---
    tags:
      - Loan Applications
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            business_name:
              type: string
              description: Name of the business
              example: ABC Company
            tax_id:
              type: string
              description: Tax ID of the business
              example: 12-3456789
            loan_purpose:
              type: string
              description: Purpose of the loan
              example: Working capital
    responses:
      201:
        description: Loan application created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Loan application created successfully
            application:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                user_id:
                  type: integer
                  example: 42
                tax_id:
                  type: string
                  example: 12-3456789
                status:
                  type: string
                  example: draft
                created_at:
                  type: string
                  format: date-time
                  example: 2023-06-01T10:00:00Z
      400:
        description: Error in provided data
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid loan application data
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid access token
            message:
              type: string
              example: Authentication failed
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
        # Get the user ID from the token and convert it to integer
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        # Add the user_id to the data
        data['user_id'] = user_id
        
        # Create the loan application
        application = loan_app_model.create_application(data)
        
        if "error" in application:
            logger.error(f"Error creating loan application: {application['error']}")
            return jsonify({"error": application["error"]}), 400
        
        logger.info(f"Loan application created successfully with ID: {application['id']}")
        
        return jsonify({
            "message": "Loan application created successfully",
            "application": application
        }), 201
        
    except Exception as e:
        logger.error(f"Exception in create_loan_application: {str(e)}")
        return jsonify({"error": str(e)}), 500


@loan_app_bp.route('', methods=['GET'])
@jwt_required()
def get_user_loan_applications():
    """
    Get all loan applications for the authenticated user
    ---
    tags:
      - Loan Applications
    security:
      - Bearer: []
    responses:
      200:
        description: List of loan applications
        schema:
          type: object
          properties:
            applications:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  status:
                    type: string
                    example: draft
                  business_name:
                    type: string
                    example: ABC Company
                  created_at:
                    type: string
                    format: date-time
                    example: 2023-06-01T10:00:00Z
                  updated_at:
                    type: string
                    format: date-time
                    example: 2023-06-01T10:00:00Z
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid access token
            message:
              type: string
              example: Authentication failed
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
        # Get the user ID from the token and convert it to integer
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        # Get all applications for the user
        applications = loan_app_model.get_applications_by_user(user_id)
        
        return jsonify({
            "applications": applications
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in get_user_loan_applications: {str(e)}")
        return jsonify({"error": str(e)}), 500


@loan_app_bp.route('/<int:application_id>', methods=['GET'])
@jwt_required()
def get_loan_application_details(application_id):
    """
    Get details of a specific loan application
    ---
    tags:
      - Loan Applications
    security:
      - Bearer: []
    parameters:
      - name: application_id
        in: path
        required: true
        type: integer
        description: ID of the loan application
    responses:
      200:
        description: Loan application details
        schema:
          type: object
          properties:
            application:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                user_id:
                  type: integer
                  example: 42
                status:
                  type: string
                  example: draft
                business_name:
                  type: string
                  example: ABC Company
                business_info:
                  type: object
                financial_info:
                  type: object
                loan_details:
                  type: object
                created_at:
                  type: string
                  format: date-time
                  example: 2023-06-01T10:00:00Z
                updated_at:
                  type: string
                  format: date-time
                  example: 2023-06-01T10:00:00Z
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid access token
            message:
              type: string
              example: Authentication failed
      403:
        description: Unauthorized access
        schema:
          type: object
          properties:
            error:
              type: string
              example: You don't have permission to access this loan application
      404:
        description: Loan application not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: Loan application not found
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
        # Get the user ID from the token and convert it to integer
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        # Get the application details
        application = loan_app_model.get_application_by_id(application_id)
        
        if not application:
            return jsonify({"error": "Loan application not found"}), 404
            
        # Check if the application belongs to the user
        if application.get('user_id') != user_id:
            return jsonify({"error": "You don't have permission to access this loan application"}), 403
        
        return jsonify({
            "application": application
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in get_loan_application_details: {str(e)}")
        return jsonify({"error": str(e)}), 500


@loan_app_bp.route('/<int:application_id>/steps/business-info', methods=['POST'])
@jwt_required()
def save_business_info(application_id):
    """
    Save business information for a loan application
    ---
    tags:
      - Loan Application Steps
    security:
      - Bearer: []
    parameters:
      - name: application_id
        in: path
        required: true
        type: integer
        description: ID of the loan application
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            business_name:
              type: string
              example: ABC Company
            business_type:
              type: string
              example: LLC
            industry:
              type: string
              example: Technology
            years_in_business:
              type: integer
              example: 5
            address:
              type: object
              properties:
                street:
                  type: string
                  example: 123 Main St
                city:
                  type: string
                  example: New York
                state:
                  type: string
                  example: NY
                zip_code:
                  type: string
                  example: 10001
    responses:
      200:
        description: Business information saved successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Business information saved successfully
            application:
              type: object
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid access token
            message:
              type: string
              example: Authentication failed
      403:
        description: Unauthorized access
        schema:
          type: object
          properties:
            error:
              type: string
              example: You don't have permission to update this loan application
      404:
        description: Loan application not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: Loan application not found
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
        # Get the user ID from the token and convert it to integer
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        # Verify application exists and belongs to user
        application = loan_app_model.get_application_by_id(application_id)
        
        if not application:
            return jsonify({"error": "Loan application not found"}), 404
            
        if application.get('user_id') != user_id:
            return jsonify({"error": "You don't have permission to update this loan application"}), 403
        
        # Update the business info
        updated_application = loan_app_model.update_business_info(application_id, data)
        
        return jsonify({
            "message": "Business information saved successfully",
            "application": updated_application
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in save_business_info: {str(e)}")
        return jsonify({"error": str(e)}), 500


@loan_app_bp.route('/<int:application_id>/steps/financial-info', methods=['POST'])
@jwt_required()
def save_financial_info(application_id):
    """
    Save financial information for a loan application
    ---
    tags:
      - Loan Application Steps
    security:
      - Bearer: []
    parameters:
      - name: application_id
        in: path
        required: true
        type: integer
        description: ID of the loan application
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            annual_revenue:
              type: number
              format: float
              example: 500000
            monthly_profit:
              type: number
              format: float
              example: 25000
            business_bank_account:
              type: object
              properties:
                bank_name:
                  type: string
                  example: Bank of America
                account_number:
                  type: string
                  example: "******1234"
            financial_documents:
              type: array
              items:
                type: object
                properties:
                  document_type:
                    type: string
                    example: tax_return
                  document_url:
                    type: string
                    example: https://example.com/document1.pdf
    responses:
      200:
        description: Financial information saved successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Financial information saved successfully
            application:
              type: object
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid access token
            message:
              type: string
              example: Authentication failed
      403:
        description: Unauthorized access
        schema:
          type: object
          properties:
            error:
              type: string
              example: You don't have permission to update this loan application
      404:
        description: Loan application not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: Loan application not found
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
        # Get the user ID from the token and convert it to integer
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        # Verify application exists and belongs to user
        application = loan_app_model.get_application_by_id(application_id)
        
        if not application:
            return jsonify({"error": "Loan application not found"}), 404
            
        if application.get('user_id') != user_id:
            return jsonify({"error": "You don't have permission to update this loan application"}), 403
        
        # Update the financial info
        updated_application = loan_app_model.update_financial_info(application_id, data)
        
        return jsonify({
            "message": "Financial information saved successfully",
            "application": updated_application
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in save_financial_info: {str(e)}")
        return jsonify({"error": str(e)}), 500


@loan_app_bp.route('/<int:application_id>/steps/loan-details', methods=['POST'])
@jwt_required()
def save_loan_details(application_id):
    """
    Save loan details for a loan application
    ---
    tags:
      - Loan Application Steps
    security:
      - Bearer: []
    parameters:
      - name: application_id
        in: path
        required: true
        type: integer
        description: ID of the loan application
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            loan_amount:
              type: number
              format: float
              example: 100000
            loan_purpose:
              type: string
              example: Working capital
            loan_term:
              type: integer
              example: 36
            collateral:
              type: object
              properties:
                has_collateral:
                  type: boolean
                  example: true
                collateral_type:
                  type: string
                  example: Real estate
                estimated_value:
                  type: number
                  format: float
                  example: 250000
    responses:
      200:
        description: Loan details saved successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Loan details saved successfully
            application:
              type: object
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid access token
            message:
              type: string
              example: Authentication failed
      403:
        description: Unauthorized access
        schema:
          type: object
          properties:
            error:
              type: string
              example: You don't have permission to update this loan application
      404:
        description: Loan application not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: Loan application not found
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
        # Get the user ID from the token and convert it to integer
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        # Verify application exists and belongs to user
        application = loan_app_model.get_application_by_id(application_id)
        
        if not application:
            return jsonify({"error": "Loan application not found"}), 404
            
        if application.get('user_id') != user_id:
            return jsonify({"error": "You don't have permission to update this loan application"}), 403
        
        # Update the loan details
        updated_application = loan_app_model.update_loan_details(application_id, data)
        
        return jsonify({
            "message": "Loan details saved successfully",
            "application": updated_application
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in save_loan_details: {str(e)}")
        return jsonify({"error": str(e)}), 500


@loan_app_bp.route('/<int:application_id>/submit', methods=['POST'])
@jwt_required()
def submit_loan_application(application_id):
    """
    Submit a loan application for evaluation
    ---
    tags:
      - Loan Applications
    security:
      - Bearer: []
    parameters:
      - name: application_id
        in: path
        required: true
        type: integer
        description: ID of the loan application
    responses:
      200:
        description: Loan application submitted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Loan application submitted successfully
            application:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                status:
                  type: string
                  example: submitted
                submitted_at:
                  type: string
                  format: date-time
                  example: 2023-06-01T10:00:00Z
      400:
        description: Invalid application state
        schema:
          type: object
          properties:
            error:
              type: string
              example: Application is missing required information
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid access token
            message:
              type: string
              example: Authentication failed
      403:
        description: Unauthorized access
        schema:
          type: object
          properties:
            error:
              type: string
              example: You don't have permission to submit this loan application
      404:
        description: Loan application not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: Loan application not found
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
        # Get the user ID from the token and convert it to integer
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        
        # Verify application exists and belongs to user
        application = loan_app_model.get_application_by_id(application_id)
        
        if not application:
            return jsonify({"error": "Loan application not found"}), 404
            
        if application.get('user_id') != user_id:
            return jsonify({"error": "You don't have permission to submit this loan application"}), 403
        
        # Check if the application has all required steps completed
        validation_result = loan_app_model.validate_application_completeness(application_id)
        
        if "error" in validation_result:
            return jsonify({"error": validation_result["error"]}), 400
        
        # Submit the application
        submitted_application = loan_app_model.submit_application(application_id)
        
        return jsonify({
            "message": "Loan application submitted successfully",
            "application": submitted_application
        }), 200
        
    except Exception as e:
        logger.error(f"Exception in submit_loan_application: {str(e)}")
        return jsonify({"error": str(e)}), 500 