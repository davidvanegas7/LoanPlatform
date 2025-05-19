from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.loan import Loan
import logging
from datetime import datetime, date
import json
from tasks.ach_processor import generate_daily_ach_file, process_ach_return_file

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
payment_bp = Blueprint('payments', __name__)

# Initialize models
loan_model = Loan()


@payment_bp.route('/', methods=['GET'])
@jwt_required()
def get_payments():
    """
    Get all pending payments
    ---
    parameters:
      - name: status
        in: query
        required: false
        type: string
        description: Status of the payments to filter by (optional)
        enum: [scheduled, processing, completed, failed, all]
      - name: limit
        in: query
        required: false
        type: integer
        description: Number of payments to return (optional)
        default: 10
      - name: sort
        in: query
        required: false
        type: string
        description: Sort order (optional)
        default: created_at:asc
        
    tags:
      - Payments
    security:
      - Bearer: []
    responses:
      200:
        description: List of payments for the loan
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
        # Get loan to verify ownership
        loans = loan_model.get_loan_by_user_id(user_id)
        loan_ids = [loan['id'] for loan in loans]

        payments = loan_model.get_payments_by_loan_ids(loan_ids)        
        
        return jsonify({
            "payments": payments,
            "status": "success"
        }), 200
    except Exception as e:
        logger.error(f"Error getting payments {str(e)}")
        return jsonify({
            "error": "Failed to retrieve payments",
            "message": str(e)
        }), 500

@payment_bp.route('/loan/<int:loan_id>', methods=['GET'])
@jwt_required()
def get_loan_payments(loan_id):
    """
    Get all payments for a specific loan
    ---
    tags:
      - Payments
    parameters:
      - name: loan_id
        in: path
        required: true
        type: integer
        description: ID of the loan to retrieve payments for
    security:
      - Bearer: []
    responses:
      200:
        description: List of payments for the loan
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
        
        # Get loan to verify ownership
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
                "message": "You do not have permission to access payments for this loan"
            }), 401
        
        # Get payments for this loan
        payments = loan_model.get_loan_payments(loan_id)
        
        return jsonify({
            "payments": payments,
            "status": "success"
        }), 200
    except Exception as e:
        logger.error(f"Error getting payments for loan {loan_id}: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve payments",
            "message": str(e)
        }), 500

@payment_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """
    Get a specific payment by ID
    ---
    tags:
      - Payments
    parameters:
      - name: payment_id
        in: path
        required: true
        type: integer
        description: ID of the payment to retrieve
    security:
      - Bearer: []
    responses:
      200:
        description: Payment details
      401:
        description: Unauthorized
      404:
        description: Payment not found
      500:
        description: Server error
    """
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get payment
        payment = loan_model.get_payment_by_id(payment_id)
        
        if not payment:
            return jsonify({
                "error": "Payment not found",
                "message": f"No payment found with ID {payment_id}"
            }), 404
        
        # Get loan to verify ownership
        loan = loan_model.get_loan_by_id(payment['loan_id'])
        
        # Verify user owns the loan this payment belongs to
        if str(loan['user_id']) != str(user_id):
            return jsonify({
                "error": "Unauthorized",
                "message": "You do not have permission to access this payment"
            }), 401
        
        return jsonify({
            "payment": payment,
            "status": "success"
        }), 200
    except Exception as e:
        logger.error(f"Error getting payment {payment_id}: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve payment details",
            "message": str(e)
        }), 500

@payment_bp.route('/<int:payment_id>/status', methods=['PUT'])
@jwt_required()
def update_payment_status(payment_id):
    """
    Update payment status
    ---
    tags:
      - Payments
    parameters:
      - name: payment_id
        in: path
        required: true
        type: integer
        description: ID of the payment to update
      - name: body
        in: body
        required: true
        schema:
          properties:
            status:
              type: string
              description: New status for the payment
              enum: [scheduled, processing, completed, failed]
              example: completed
            failure_reason:
              type: string
              description: Reason for failure (if status is failed)
              example: Insufficient funds
    security:
      - Bearer: []
    responses:
      200:
        description: Payment status updated successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
      404:
        description: Payment not found
      500:
        description: Server error
    """
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get payment
        payment = loan_model.get_payment_by_id(payment_id)
        
        if not payment:
            return jsonify({
                "error": "Payment not found",
                "message": f"No payment found with ID {payment_id}"
            }), 404
        
        # Get loan to verify ownership
        loan = loan_model.get_loan_by_id(payment['loan_id'])
        
        # Verify user owns the loan this payment belongs to
        if str(loan['user_id']) != str(user_id):
            return jsonify({
                "error": "Unauthorized",
                "message": "You do not have permission to update this payment"
            }), 401
        
        # Get request data
        data = request.get_json()
        status = data.get('status')
        failure_reason = data.get('failure_reason')
        
        if not status or status not in ['scheduled', 'processing', 'completed', 'failed']:
            return jsonify({
                "error": "Invalid status",
                "message": "Status must be one of: scheduled, processing, completed, failed"
            }), 400
        
        # If status is failed, failure_reason is required
        if status == 'failed' and not failure_reason:
            return jsonify({
                "error": "Missing failure reason",
                "message": "Failure reason is required when status is 'failed'"
            }), 400
        
        # Update payment status
        updated_payment = loan_model.update_payment_status(payment_id, status, failure_reason)
        
        return jsonify({
            "message": "Payment status updated successfully",
            "payment": updated_payment,
            "status": "success"
        }), 200
    except Exception as e:
        logger.error(f"Error updating payment status for payment {payment_id}: {str(e)}")
        return jsonify({
            "error": "Failed to update payment status",
            "message": str(e)
        }), 500

@payment_bp.route('/create-ach-batch', methods=['POST'])
def create_ach_batch():
    """
    Create a new ACH payment batch for today's scheduled payments
    ---
    tags:
      - Payments
    parameters:
      - name: body
        in: body
        schema:
          properties:
            batch_date:
              type: string
              format: date
              description: Date for which to create the batch (defaults to today)
              example: "2023-06-01"
    security:
      - Bearer: []
    responses:
      201:
        description: ACH batch created successfully
      400:
        description: Invalid request data
      500:
        description: Server error
    """
    try:
        # Get request data
        data = request.get_json() or {}
        batch_date_str = data.get('batch_date')
        
        # Parse batch date if provided
        batch_date = None
        if batch_date_str:
            try:
                batch_date = datetime.strptime(batch_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    "error": "Invalid date format",
                    "message": "Date must be in format YYYY-MM-DD"
                }), 400
        
        # Create ACH batch
        batch = loan_model.create_ach_batch(batch_date)
        
        if 'error' in batch:
            return jsonify({
                "error": "Failed to create ACH batch",
                "message": batch['error']
            }), 500
        
        return jsonify({
            "message": "ACH batch created successfully",
            "batch": batch,
            "status": "success"
        }), 201
    except Exception as e:
        logger.error(f"Error creating ACH batch: {str(e)}")
        return jsonify({
            "error": "Failed to create ACH batch",
            "message": str(e)
        }), 500

@payment_bp.route('/process-failed-payments', methods=['POST'])
def process_failed_payments():
    """
    Process a list of failed payments from ACH return file
    ---
    tags:
      - Payments
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            failed_transactions:
              type: array
              description: List of failed transactions
              items:
                type: object
                properties:
                  payment_id:
                    type: integer
                    description: ID of the payment that failed
                  failure_reason:
                    type: string
                    description: Reason for payment failure
    security:
      - Bearer: []
    responses:
      200:
        description: Failed payments processed successfully
      400:
        description: Invalid request data
      500:
        description: Server error
    """
    try:
        # Get request data
        data = request.get_json()
        failed_transactions = data.get('failed_transactions', [])
        
        if not failed_transactions or not isinstance(failed_transactions, list):
            return jsonify({
                "error": "Invalid data",
                "message": "failed_transactions must be a non-empty array"
            }), 400
        
        # Process failed payments
        result = loan_model.process_failed_payments(failed_transactions)
        
        if 'error' in result:
            return jsonify({
                "error": "Failed to process failed payments",
                "message": result['error']
            }), 500
        
        return jsonify({
            "message": f"Processed {len(failed_transactions)} failed payments successfully",
            "status": "success"
        }), 200
    except Exception as e:
        logger.error(f"Error processing failed payments: {str(e)}")
        return jsonify({
            "error": "Failed to process failed payments",
            "message": str(e)
        }), 500

@payment_bp.route('/generate-ach-file', methods=['POST'])
def generate_ach_file():
    """
    Generate NACHA formatted ACH file for today's scheduled payments
    ---
    tags:
      - Payments
    parameters:
      - name: body
        in: body
        schema:
          properties:
            batch_date:
              type: string
              format: date
              description: Date for which to create the ACH file (defaults to today)
              example: "2023-06-01"
            async_mode:
              type: boolean
              description: Whether to process the file asynchronously
              default: false
    security:
      - Bearer: []
    responses:
      200:
        description: ACH file generation started or completed
      400:
        description: Invalid request data
      500:
        description: Server error
    """
    try:
        # Get request data
        data = request.get_json() or {}
        batch_date_str = data.get('batch_date')
        async_mode = data.get('async_mode', False)
        
        # Parse batch date if provided
        batch_date = None
        if batch_date_str:
            try:
                batch_date = datetime.strptime(batch_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    "error": "Formato de fecha inválido",
                    "message": "La fecha debe estar en formato YYYY-MM-DD"
                }), 400
        
        if async_mode:
            # Ejecutar la tarea de manera asíncrona
            task = generate_daily_ach_file.delay()
            return jsonify({
                "message": "Generación de archivo ACH iniciada",
                "task_id": task.id,
                "status": "success"
            }), 202
        else:
            # Ejecutar la tarea de manera síncrona
            result = generate_daily_ach_file()
            
            if 'error' in result:
                return jsonify({
                    "error": "Error al generar archivo ACH",
                    "message": result['error']
                }), 500
                
            return jsonify({
                "message": "Archivo ACH generado exitosamente",
                "result": result,
                "status": "success"
            }), 200
    except Exception as e:
        logger.error(f"Error al generar archivo ACH: {str(e)}")
        return jsonify({
            "error": "Error al generar archivo ACH",
            "message": str(e)
        }), 500

@payment_bp.route('/process-return-file', methods=['POST'])
def process_return_file():
    """
    Process an ACH return file containing failed transactions
    ---
    tags:
      - Payments
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            async_mode:
              type: boolean
              description: Whether to process the file asynchronously
              default: false
    security:
      - Bearer: []
    responses:
      200:
        description: ACH return file processing started or completed
      400:
        description: Invalid request data
      500:
        description: Server error
    """
    try:
        # Get request data
        data = request.get_json()
        async_mode = data.get('async_mode', False)
        
        if async_mode:
            # Ejecutar la tarea de manera asíncrona
            task = process_ach_return_file.delay()
            return jsonify({
                "message": "Procesamiento de archivo de retorno ACH iniciado",
                "task_id": task.id,
                "status": "success"
            }), 202
        else:
            # Ejecutar la tarea de manera síncrona
            result = process_ach_return_file()
            
            if 'error' in result:
                return jsonify({
                    "error": "Error al procesar archivo de retorno ACH",
                    "message": result['error']
                }), 500
                
            return jsonify({
                "message": "Archivo de retorno ACH procesado exitosamente",
                "result": result,
                "status": "success"
            }), 200
    except Exception as e:
        logger.error(f"Error al procesar archivo de retorno ACH: {str(e)}")
        return jsonify({
            "error": "Error al procesar archivo de retorno ACH",
            "message": str(e)
        }), 500 