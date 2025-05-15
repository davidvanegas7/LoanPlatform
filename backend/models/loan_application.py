from config.db import Database
import logging
import json
from datetime import datetime

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
            loan_details JSON,
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
            SELECT id, user_id, status, business_name, tax_id, created_at, updated_at, submitted_at
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
            SELECT id, user_id, status, business_name, business_info, 
                  financial_info, loan_details, created_at, updated_at, submitted_at
            FROM loan_applications 
            WHERE id = %s
            """
            application = self.db.fetch_one(query, (application_id,))
            
            if application:
                # Parse JSON fields
                for json_field in ['business_info', 'financial_info', 'loan_details']:
                    if application.get(json_field):
                        if isinstance(application[json_field], str):
                            try:
                                application[json_field] = json.loads(application[json_field])
                            except json.JSONDecodeError:
                                application[json_field] = {}
            
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
            # Format as JSON for storage
            loan_details_json = json.dumps(data)
            
            # Update loan details
            query = """
            UPDATE loan_applications 
            SET loan_details = %s
            WHERE id = %s
            """
            
            self.db.execute_query(query, (loan_details_json, application_id))
            
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
                
            if not application.get('loan_details'):
                return {"error": "Loan details are required"}
            
            # Validate required fields in business_info
            business_info = application.get('business_info', {})
            if not business_info.get('business_name'):
                return {"error": "Business name is required"}
                
            # Validate required fields in financial_info
            financial_info = application.get('financial_info', {})
            if 'annual_revenue' not in financial_info:
                return {"error": "Annual revenue is required"}
                
            # Validate required fields in loan_details
            loan_details = application.get('loan_details', {})
            if 'loan_amount' not in loan_details:
                return {"error": "Loan amount is required"}
                
            if 'loan_purpose' not in loan_details:
                return {"error": "Loan purpose is required"}
            
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

            if application.get('loan_details')['loan_amount'] < 50000:
                status = 'approved'
            elif application.get('loan_details')['loan_amount'] == 50000:
                status = 'undecided'
            else:
                status = 'declined'

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