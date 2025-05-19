from config.db import Database
import logging
import json
from datetime import datetime
import random
from decimal import Decimal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoanApplication:
    def __init__(self):
        self.db = Database()
        self.create_tables()
        
    def create_tables(self):
        # Create loan_applications table if it doesn't exist
        query = """
        CREATE TABLE IF NOT EXISTS loan_applications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            status ENUM('draft', 'submitted', 'reviewing', 'approved', 'declined', 'undecided') DEFAULT 'draft',
            business_name VARCHAR(255),
            tax_id VARCHAR(50),
            business_info JSON,
            financial_info JSON,
            loan_amount DECIMAL(10, 2) NULL,
            loan_purpose VARCHAR(255) NULL,
            loan_term INT NULL,
            loan_interest_rate DECIMAL(5, 4) NULL,
            loan_total_amount DECIMAL(12, 2) NULL,
            loan_monthly_payment DECIMAL(12, 2) NULL,
            submitted_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        self.db.execute_query(query)
    
    def create_application(self, data):
        try:
            # Extract basic data
            user_id = data.get('user_id')
            business_name = data.get('business_name', '')
            tax_id = data.get('tax_id', '')
            
            # Insert new application
            query = """
            INSERT INTO loan_applications (user_id, business_name, tax_id) 
            VALUES (%s, %s, %s)
            """
            application_id = self.db.insert(query, (user_id, business_name, tax_id))
            
            if application_id:
                logger.info(f"Loan application created with ID: {application_id}")
                return self.get_application_by_id(application_id)
            return {"error": "Error creating loan application"}
        except Exception as e:
            logger.error(f"Error in create_application: {str(e)}")
            return {"error": f"Error creating loan application: {str(e)}"}
    
    def get_applications_by_user(self, user_id):
        try:
            query = """
            SELECT id, user_id, status, business_name, tax_id, loan_amount, loan_purpose, loan_term, loan_total_amount, loan_monthly_payment, loan_interest_rate, created_at, updated_at, submitted_at
            FROM loan_applications 
            WHERE user_id = %s
            ORDER BY created_at DESC
            """
            applications = self.db.fetch_all(query, (user_id,))
            return applications
        except Exception as e:
            logger.error(f"Error getting applications for user {user_id}: {str(e)}")
            return []
    
    def get_application_by_id(self, application_id):
        try:
            query = """
            SELECT id, user_id, status, business_name, tax_id, business_info, 
                  financial_info, loan_amount, loan_purpose, loan_term, loan_total_amount, loan_monthly_payment, loan_interest_rate, created_at, updated_at, submitted_at
            FROM loan_applications 
            WHERE id = %s
            """
            application = self.db.fetch_one(query, (application_id,))
            
            if application:
                # Parse JSON fields
                for json_field in ['business_info', 'financial_info']:
                    if application.get(json_field):
                        field_value = application[json_field]
                        
                        # First, ensure it's a string by decoding if it's bytes
                        if isinstance(field_value, bytes):
                            try:
                                field_value = field_value.decode('utf-8')
                            except UnicodeDecodeError:
                                logger.error(f"Error decoding bytes field {json_field} for application {application_id}. Value: {field_value[:50]}...") # Log a snippet of the value
                                application[json_field] = {"error": "unicode_decode_error"} # Or some other placeholder
                                continue # Skip to next field or handle as an error

                        # Now, if it's a string (either originally or after decoding), parse it as JSON
                        if isinstance(field_value, str):
                            try:
                                application[json_field] = json.loads(field_value)
                            except json.JSONDecodeError:
                                logger.warning(f"Could not decode JSON string for field {json_field} in application {application_id}. Value: {field_value[:100]}... Setting to empty dict.")
                                application[json_field] = {}
                        # If it's already a dict (e.g., if the DB driver handles JSON parsing), do nothing.
                        # If it's neither bytes, str, nor dict, it might be an issue or already parsed.
                        # For now, we only explicitly handle bytes and str.
            
                # Convert Decimal fields to string for JSON serialization
                decimal_fields = ['loan_amount', 'loan_total_amount', 'loan_monthly_payment', 'loan_interest_rate']
                for field in decimal_fields:
                    if field in application and application[field] is not None:
                        if isinstance(application[field], Decimal):
                            application[field] = str(application[field])
            
            return application
        except Exception as e:
            logger.error(f"Error getting application {application_id}: {str(e)}")
            return None
    
    def update_business_info(self, application_id, data):
        try:
            # Format as JSON for storage
            business_info_json = json.dumps(data)
            
            # Update business info
            query = """
            UPDATE loan_applications 
            SET business_info = %s, business_name = %s
            WHERE id = %s
            """
            
            business_name = data.get('business_name', '')
            self.db.execute_query(query, (business_info_json, business_name, application_id))
            
            # Return updated application
            return self.get_application_by_id(application_id)
        except Exception as e:
            logger.error(f"Error updating business info for application {application_id}: {str(e)}")
            return {"error": f"Error updating business information: {str(e)}"}
    
    def update_financial_info(self, application_id, data):
        try:
            # Format as JSON for storage
            financial_info_json = json.dumps(data)
            
            # Update financial info
            query = """
            UPDATE loan_applications 
            SET financial_info = %s
            WHERE id = %s
            """
            
            self.db.execute_query(query, (financial_info_json, application_id))
            
            # Return updated application
            return self.get_application_by_id(application_id)
        except Exception as e:
            logger.error(f"Error updating financial info for application {application_id}: {str(e)}")
            return {"error": f"Error updating financial information: {str(e)}"}
    
    def update_loan_details(self, application_id, data):
        try:
            # Update loan details columns
            query = """
            UPDATE loan_applications 
            SET loan_amount = %s, loan_purpose = %s, loan_term = %s
            WHERE id = %s
            """
            
            self.db.execute_query(query, (data['loan_amount'], data['loan_purpose'], data['loan_term'], application_id))
            
            # Return updated application
            return self.get_application_by_id(application_id)
        except Exception as e:
            logger.error(f"Error updating loan details for application {application_id}: {str(e)}")
            return {"error": f"Error updating loan details: {str(e)}"}
    
    def validate_application_completeness(self, application_id):
        try:
            application = self.get_application_by_id(application_id)
            
            if not application:
                return {"error": "Application not found"}
                
            # Check if required sections are completed
            if not application.get('business_info'):
                return {"error": "Business information is required"}
                
            if not application.get('financial_info'):
                return {"error": "Financial information is required"}
                
            if not application.get('loan_amount'):
                return {"error": "Loan amount is required"}
                
            if not application.get('loan_purpose'):
                return {"error": "Loan purpose is required"}
            
            # Validate required fields in business_info
            business_info = application.get('business_info', {})
            if not business_info.get('business_name'):
                return {"error": "Business name is required"}
                
            # Validate required fields in financial_info
            financial_info = application.get('financial_info', {})
            if 'annual_revenue' not in financial_info:
                return {"error": "Annual revenue is required"}
            
            return {"valid": True}
        except Exception as e:
            logger.error(f"Error validating application {application_id}: {str(e)}")
            return {"error": f"Error validating application: {str(e)}"}
    
    def submit_application(self, application_id):
        try:
            # Update status to submitted and set submitted_at timestamp
            status = 'submitted'
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            application = self.get_application_by_id(application_id)

            if int(application.get('loan_amount')) < 50000:
                status = 'approved'
                loan_interest_rate = random.randint(5, 20) / 100 # 5% to 20%
                # Calculando pago total con interés compuesto mensual
                annual_rate = float(loan_interest_rate)
                monthly_rate = annual_rate / 12  # Convertir tasa anual a mensual
                principal = float(application.get('loan_amount'))
                term_months = float(application.get('loan_term'))
                
                # Calculamos el pago mensual usando la fórmula de amortización
                if monthly_rate > 0:
                    loan_monthly_payment = principal * monthly_rate * (1 + monthly_rate)**term_months / ((1 + monthly_rate)**term_months - 1)
                else:
                    loan_monthly_payment = principal / term_months
                    
                loan_total_amount = loan_monthly_payment * term_months

                query = """
                UPDATE loan_applications 
                SET status = %s, submitted_at = %s, loan_total_amount = %s, loan_interest_rate = %s, loan_monthly_payment = %s
                WHERE id = %s
                """
                
                self.db.execute_query(query, (status, current_time, loan_total_amount, loan_interest_rate, loan_monthly_payment, application_id))

            elif int(application.get('loan_amount')) == 50000:
                status = 'undecided'
            else:
                status = 'declined'

            if (status == 'declined' or status == 'undecided'):
                query = """
                UPDATE loan_applications 
                SET status = %s, submitted_at = %s
                WHERE id = %s
                """
                
                self.db.execute_query(query, (status, current_time, application_id))
            
            # Return updated application
            return self.get_application_by_id(application_id)
        except Exception as e:
            logger.error(f"Error submitting application {application_id}: {str(e)}")
            return {"error": f"Error submitting application: {str(e)}"} 
        
    def update_status(self, application_id, status):
        try:
            query = """
            UPDATE loan_applications 
            SET status = %s
            WHERE id = %s
            """

            self.db.execute_query(query, (status, application_id))
        except Exception as e:
            logger.error(f"Error updating status for application {application_id}: {str(e)}")
            return {"error": f"Error updating status: {str(e)}"}
