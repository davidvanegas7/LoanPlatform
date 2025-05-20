from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.loan import Loan
from models.loan_application import LoanApplication
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
loan_bp = Blueprint('loans', __name__)

# Initialize models
loan_model = Loan()
loan_application_model = LoanApplication()

@loan_bp.route('/', methods=['GET'])
@jwt_required()
def get_loans():
    """
    Get all loans for the authenticated user
    ---
    tags:
      - Loans
    security:
      - Bearer: []
    responses:
      200:
        description: List of loans
      401:
        description: Unauthorized
      500:
        description: Server error
    """
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get loans for user
        loans = loan_model.get_loans_by_user(user_id)
        
        return jsonify({
            "loans": loans,
            "status": "success"
        }), 200
    except Exception as e:
        logger.error(f"Error getting loans: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve loans",
            "message": str(e)
        }), 500

@loan_bp.route('/<int:loan_id>', methods=['GET'])
@jwt_required()
def get_loan(loan_id):
    """
    Get a specific loan by ID
    ---
    tags:
      - Loans
    parameters:
      - name: loan_id
        in: path
        required: true
        type: integer
        description: ID of the loan to retrieve
    security:
      - Bearer: []
    responses:
      200:
        description: Loan details
      401:
        description: Unauthorized
      404:
        description: Loan not found
      500:
        description: Server error
    """
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get loan
        loan = loan_model.get_loan_by_id(loan_id)
        
        if not loan:
            return jsonify({
                "error": "Loan not found",
                "message": f"No loan found with ID {loan_id}"
            }), 404
            
        # Verify user owns this loan
        if str(loan['user_id']) != str(user_id):
            return jsonify({
                "error": "Unauthorized",
                "message": "You do not have permission to access this loan"
            }), 401
        
        # Get payments for this loan
        payments = loan_model.get_loan_payments(loan_id)
        
        # Group payments by status
        payment_summary = {
            "completed": [],
            "scheduled": [],
            "processing": [],
            "failed": []
        }
        
        for payment in payments:
            status = payment['status']
            if status in payment_summary:
                payment_summary[status].append(payment)
        
        return jsonify({
            "loan": loan,
            "payments": {
                "summary": {
                    "total": len(payments),
                    "completed": len(payment_summary['completed']),
                    "scheduled": len(payment_summary['scheduled']),
                    "processing": len(payment_summary['processing']),
                    "failed": len(payment_summary['failed'])
                },
                "completed": payment_summary['completed'],
                "scheduled": payment_summary['scheduled'],
                "processing": payment_summary['processing'],
                "failed": payment_summary['failed']
            },
            "status": "success"
        }), 200
    except Exception as e:
        logger.error(f"Error getting loan {loan_id}: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve loan details",
            "message": str(e)
        }), 500

@loan_bp.route('/application/<int:application_id>/fund', methods=['POST'])
@jwt_required()
def fund_loan(application_id):
    """
    Fund a loan for an approved application
    ---
    tags:
      - Loans
    parameters:
      - name: application_id
        in: path
        required: true
        type: integer
        description: ID of the loan application to fund
      - name: body
        in: body
        required: true
        schema:
          properties:
            term_days:
              type: integer
              description: Number of days for the loan term
              example: 90
            interest_rate:
              type: number
              format: float
              description: Interest rate for the loan
              example: 5.5
    security:
      - Bearer: []
    responses:
      201:
        description: Loan funded successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
      404:
        description: Application not found
      500:
        description: Server error
    """
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get application
        application = loan_application_model.get_application_by_id(application_id)
        
        if not application:
            return jsonify({
                "error": "Application not found",
                "message": f"No application found with ID {application_id}"
            }), 404
            
        # Verify user owns this application
        if str(application['user_id']) != str(user_id):
            return jsonify({
                "error": "Unauthorized",
                "message": "You do not have permission to fund this application"
            }), 401
            
        # Verify application is approved
        if application['status'] != 'approved':
            return jsonify({
                "error": "Invalid application status",
                "message": f"Application must be approved to fund a loan. Current status: {application['status']}"
            }), 400
        
        # Get loan details from application instead of request
        if not application.get('loan_amount') or not application.get('loan_term'):
            return jsonify({
                "error": "Invalid application",
                "message": "Application does not have valid loan details"
            }), 400
        
        # Para este ejemplo, asumimos que term_days y term_months son lo mismo (multiplicado por 30)
        term_days = application.get('loan_term') * 30  # Convertimos meses a días aproximados
        interest_rate = application.get('loan_interest_rate')  # Valor por defecto o se podría agregar como columna si es necesario
        loan_amount = application.get('loan_amount')
        loan_total_amount = application.get('loan_total_amount')
        # Create loan object
        loan_data = {
            'application_id': application_id,
            'user_id': user_id,
            'business_name': application.get('business_name'),
            'tax_id': application.get('tax_id'),
            'amount': loan_amount,
            'term_days': term_days,
            'interest_rate': interest_rate,
            'remaining_balance': loan_total_amount,
        }
        
        # Create loan
        loan = loan_model.create_loan(loan_data)
        
        if 'error' in loan:
            return jsonify({
                "error": "Failed to fund loan",
                "message": loan['error']
            }), 500
                
        return jsonify({
            "message": "Loan funded successfully",
            "loan": loan,
            "status": "success"
        }), 201
    except Exception as e:
        logger.error(f"Error funding loan for application {application_id}: {str(e)}")
        return jsonify({
            "error": "Failed to fund loan",
            "message": str(e)
        }), 500

@loan_bp.route('/<int:loan_id>/status', methods=['PUT'])
@jwt_required()
def update_loan_status(loan_id):
    """
    Update loan status
    ---
    tags:
      - Loans
    parameters:
      - name: loan_id
        in: path
        required: true
        type: integer
        description: ID of the loan to update
      - name: body
        in: body
        required: true
        schema:
          properties:
            status:
              type: string
              description: New status for the loan
              enum: [active, closed, defaulted]
              example: closed
    security:
      - Bearer: []
    responses:
      200:
        description: Loan status updated successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
      404:
        description: Loan not found
      500:
        description: Server error
    """
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get loan
        loan = loan_model.get_loan_by_id(loan_id)
        
        if not loan:
            return jsonify({
                "error": "Loan not found",
                "message": f"No loan found with ID {loan_id}"
            }), 404
            
        # Verify user owns this loan
        if str(loan['user_id']) != str(user_id):
            return jsonify({
                "error": "Unauthorized",
                "message": "You do not have permission to update this loan"
            }), 401
        
        # Get request data
        data = request.get_json()
        status = data.get('status')
        
        if not status or status not in ['active', 'closed', 'defaulted']:
            return jsonify({
                "error": "Invalid status",
                "message": "Status must be one of: active, closed, defaulted"
            }), 400
        
        # Update loan status
        updated_loan = loan_model.update_loan_status(loan_id, status)
        
        return jsonify({
            "message": "Loan status updated successfully",
            "loan": updated_loan,
            "status": "success"
        }), 200
    except Exception as e:
        logger.error(f"Error updating loan status for loan {loan_id}: {str(e)}")
        return jsonify({
            "error": "Failed to update loan status",
            "message": str(e)
        }), 500 