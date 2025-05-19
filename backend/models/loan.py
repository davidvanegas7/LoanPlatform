from config.db import Database
import logging
from datetime import datetime, timedelta
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Loan:
    def __init__(self):
        self.db = Database()
        self.create_tables()
        
    def create_tables(self):
        # Create loans table if it doesn't exist
        loans_query = """
        CREATE TABLE IF NOT EXISTS loans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            application_id INT NOT NULL,
            user_id INT NOT NULL,
            business_name VARCHAR(255) NOT NULL,
            tax_id VARCHAR(50) NOT NULL,
            status ENUM('active', 'closed', 'defaulted') DEFAULT 'active',
            amount DECIMAL(10, 2) NOT NULL,
            term_days INT NOT NULL,
            interest_rate DECIMAL(5, 2) NOT NULL,
            remaining_balance DECIMAL(10, 2) NOT NULL,
            daily_payment DECIMAL(10, 2) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            funded_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES loan_applications(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        self.db.execute_query(loans_query)
        
        # Create payments table if it doesn't exist
        payments_query = """
        CREATE TABLE IF NOT EXISTS payments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            loan_id INT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            status ENUM('scheduled', 'processing', 'completed', 'failed') DEFAULT 'scheduled',
            due_date DATE NOT NULL,
            processed_at TIMESTAMP NULL,
            ach_batch_id INT NULL,
            ach_transaction_id VARCHAR(50) NULL,
            failure_reason VARCHAR(255) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (loan_id) REFERENCES loans(id)
        )
        """
        self.db.execute_query(payments_query)
        
        # Create ach_batches table if it doesn't exist
        ach_batches_query = """
        CREATE TABLE IF NOT EXISTS ach_batches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            status ENUM('pending', 'processed', 'completed') DEFAULT 'pending',
            batch_date DATE NOT NULL,
            file_name VARCHAR(255) NULL,
            total_transactions INT NOT NULL DEFAULT 0,
            total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(ach_batches_query)
        
        # Create ach_transactions table if it doesn't exist
        ach_transactions_query = """
        CREATE TABLE IF NOT EXISTS ach_transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            batch_id INT NOT NULL,
            payment_id INT NOT NULL,
            status ENUM('pending', 'processed', 'failed', 'returned') DEFAULT 'pending',
            transaction_id VARCHAR(50) NULL,
            amount DECIMAL(10, 2) NOT NULL,
            failure_reason VARCHAR(255) NULL,
            processed_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES ach_batches(id),
            FOREIGN KEY (payment_id) REFERENCES payments(id)
        )
        """
        self.db.execute_query(ach_transactions_query)
    
    def create_loan(self, data):
        try:
            # Extract loan data
            application_id = data.get('application_id')
            user_id = data.get('user_id')
            business_name = data.get('business_name')
            tax_id = data.get('tax_id')
            amount = data.get('amount')
            term_days = data.get('term_days')
            interest_rate = data.get('interest_rate')
            remaining_balance = data.get('remaining_balance')
            # Calculate loan details
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=term_days)
            
            # Calculate daily payment
            daily_payment = remaining_balance / term_days
            
            # Insert new loan
            query = """
            INSERT INTO loans (
                application_id, user_id, business_name, tax_id,
                amount, term_days, interest_rate, remaining_balance, daily_payment, 
                start_date, end_date, funded_at
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            loan_id = self.db.insert(query, (
                application_id, user_id, business_name, tax_id,
                amount, term_days, interest_rate, remaining_balance, daily_payment,
                start_date, end_date
            ))
            
            if loan_id:
                # Create payment schedule
                self.create_payment_schedule(loan_id, start_date, term_days, daily_payment)
                logger.info(f"Loan created with ID: {loan_id}")
                return self.get_loan_by_id(loan_id)
            
            return {"error": "Error creating loan"}
        except Exception as e:
            logger.error(f"Error in create_loan: {str(e)}")
            return {"error": f"Error creating loan: {str(e)}"}
    
    def create_payment_schedule(self, loan_id, start_date, term_days, daily_payment):
        try:
            # Create a payment entry for each day in the term
            due_date = start_date
            for _ in range(term_days):
                due_date = due_date + timedelta(days=1)
                query = """
                INSERT INTO payments (loan_id, amount, due_date, status)
                VALUES (%s, %s, %s, 'scheduled')
                """
                self.db.insert(query, (loan_id, daily_payment, due_date))
            
            logger.info(f"Created payment schedule for loan {loan_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating payment schedule for loan {loan_id}: {str(e)}")
            return False
    
    def get_loan_by_id(self, loan_id):
        try:
            query = """
            SELECT * FROM loans WHERE id = %s
            """
            loan = self.db.fetch_one(query, (loan_id,))
            return loan
        except Exception as e:
            logger.error(f"Error getting loan {loan_id}: {str(e)}")
            return None
    
    def get_loan_by_user_id(self, user_id):
        try:
            query = """
            SELECT * FROM loans WHERE user_id = %s
            """
            loans = self.db.fetch_all(query, (user_id,))
            return loans
        except Exception as e:
            logger.error(f"Error getting loan {user_id}: {str(e)}")
            return None
    
    def get_loans_by_user(self, user_id):
        try:
            query = """
            SELECT * FROM loans WHERE user_id = %s
            """
            loans = self.db.fetch_all(query, (user_id,))
            return loans
        except Exception as e:
            logger.error(f"Error getting loans for user {user_id}: {str(e)}")
            return []
    
    def get_loan_payments(self, loan_id):
        try:
            query = """
            SELECT * FROM payments 
            WHERE loan_id = %s
            ORDER BY due_date ASC
            """
            payments = self.db.fetch_all(query, (loan_id,))
            return payments
        except Exception as e:
            logger.error(f"Error getting payments for loan {loan_id}: {str(e)}")
            return []
    
    def update_loan_status(self, loan_id, status):
        try:
            query = """
            UPDATE loans 
            SET status = %s
            WHERE id = %s
            """
            self.db.execute_query(query, (status, loan_id))
            return self.get_loan_by_id(loan_id)
        except Exception as e:
            logger.error(f"Error updating status for loan {loan_id}: {str(e)}")
            return {"error": f"Error updating loan status: {str(e)}"}
    
    def update_payment_status(self, payment_id, status, failure_reason=None):
        try:
            query = """
            UPDATE payments 
            SET status = %s, failure_reason = %s, processed_at = %s
            WHERE id = %s
            """
            processed_at = datetime.now() if status in ['completed', 'failed'] else None
            self.db.execute_query(query, (status, failure_reason, processed_at, payment_id))
            
            # If payment completed, update loan remaining balance
            if status == 'completed':
                self.update_loan_balance_after_payment(payment_id)
            
            return self.get_payment_by_id(payment_id)
        except Exception as e:
            logger.error(f"Error updating status for payment {payment_id}: {str(e)}")
            return {"error": f"Error updating payment status: {str(e)}"}
    
    def get_payment_by_id(self, payment_id):
        try:
            query = """
            SELECT * FROM payments WHERE id = %s
            """
            payment = self.db.fetch_one(query, (payment_id,))
            return payment
        except Exception as e:
            logger.error(f"Error getting payment {payment_id}: {str(e)}")
            return None
    
    def update_loan_balance_after_payment(self, payment_id):
        try:
            # Get payment amount and loan_id
            query = "SELECT loan_id, amount FROM payments WHERE id = %s"
            payment = self.db.fetch_one(query, (payment_id,))
            
            if not payment:
                return False
                
            loan_id = payment['loan_id']
            payment_amount = payment['amount']
            
            # Update loan remaining balance
            query = """
            UPDATE loans 
            SET remaining_balance = remaining_balance - %s
            WHERE id = %s
            """
            self.db.execute_query(query, (payment_amount, loan_id))
            
            # Check if loan is paid off
            loan = self.get_loan_by_id(loan_id)
            if loan and loan['remaining_balance'] <= 0:
                self.update_loan_status(loan_id, 'closed')
                
            return True
        except Exception as e:
            logger.error(f"Error updating loan balance after payment {payment_id}: {str(e)}")
            return False
    
    def create_ach_batch(self, batch_date=None):
        try:
            if not batch_date:
                batch_date = datetime.now().date()
                
            # Create new ACH batch
            query = """
            INSERT INTO ach_batches (batch_date, status)
            VALUES (%s, 'pending')
            """
            batch_id = self.db.insert(query, (batch_date,))
            
            # Get all scheduled payments due on batch_date
            payments_query = """
            SELECT id, loan_id, amount 
            FROM payments 
            WHERE due_date = %s AND status = 'scheduled'
            """
            payments = self.db.fetch_all(payments_query, (batch_date,))
            
            total_amount = 0
            total_transactions = 0
            
            # Create ACH transactions for each payment
            for payment in payments:
                # Update payment status to processing
                self.update_payment_status(payment['id'], 'processing')
                
                # Create ACH transaction
                transaction_query = """
                INSERT INTO ach_transactions (batch_id, payment_id, amount, status)
                VALUES (%s, %s, %s, 'pending')
                """
                self.db.insert(transaction_query, (
                    batch_id, payment['id'], payment['amount']
                ))
                
                total_amount += float(payment['amount'])
                total_transactions += 1
            
            # Update batch with totals
            update_query = """
            UPDATE ach_batches 
            SET total_transactions = %s, total_amount = %s
            WHERE id = %s
            """
            self.db.execute_query(update_query, (
                total_transactions, total_amount, batch_id
            ))
            
            return self.get_ach_batch(batch_id)
        except Exception as e:
            logger.error(f"Error creating ACH batch: {str(e)}")
            return {"error": f"Error creating ACH batch: {str(e)}"}
    
    def get_ach_batch(self, batch_id):
        try:
            query = """
            SELECT * FROM ach_batches WHERE id = %s
            """
            batch = self.db.fetch_one(query, (batch_id,))
            return batch
        except Exception as e:
            logger.error(f"Error getting ACH batch {batch_id}: {str(e)}")
            return None
    
    def process_failed_payments(self, failed_transactions):
        try:
            for transaction in failed_transactions:
                payment_id = transaction.get('payment_id')
                failure_reason = transaction.get('failure_reason', 'Unknown failure')
                
                # Update payment status to failed
                self.update_payment_status(payment_id, 'failed', failure_reason)
                
                # Update ACH transaction status
                query = """
                UPDATE ach_transactions 
                SET status = 'failed', failure_reason = %s, processed_at = NOW()
                WHERE payment_id = %s
                """
                self.db.execute_query(query, (failure_reason, payment_id))
            
            return {"message": f"Processed {len(failed_transactions)} failed transactions", "status": "success"}
        except Exception as e:
            logger.error(f"Error processing failed payments: {str(e)}")
            return {"error": f"Error processing failed payments: {str(e)}"} 
        
    def get_payments_by_loan_ids(self, loan_ids, status):
        try:
            # Convertir la lista de IDs a una cadena de texto con los IDs separados por comas
            if isinstance(loan_ids, list):
                loan_ids_str = ','.join(map(str, loan_ids))
                query = f"""
                SELECT * FROM payments WHERE status = %s AND loan_id IN ({loan_ids_str}) ORDER BY due_date ASC

                """
                payments = self.db.fetch_all(query, (status,))
            else:
                # Si solo es un ID, usar la consulta original
                query = """
                SELECT * FROM payments WHERE status = %s AND loan_id = %s ORDER BY due_date ASC
                """
                payments = self.db.fetch_all(query, (status, loan_ids))
            return payments
        except Exception as e:
            logger.error(f"Error getting payments by loan IDs: {str(e)}")
            return []
