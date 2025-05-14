import bcrypt
from config.db import Database
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User:
    def __init__(self):
        self.db = Database()
        
    def create_tables(self):
        # Create users table if it doesn't exist
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            role ENUM('admin', 'user') DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(query)
        
        # Create business_owners table if it doesn't exist
        query = """
        CREATE TABLE IF NOT EXISTS business_owners (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            business_name VARCHAR(255) NOT NULL,
            business_address VARCHAR(255),
            phone_number VARCHAR(20),
            tax_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        self.db.execute_query(query)
        
    def create_user(self, email, password, first_name=None, last_name=None, role='user'):
        try:
            # Normalize email
            normalized_email = email.strip().lower()
            
            # Check if user already exists
            query = "SELECT id FROM users WHERE LOWER(email) = LOWER(%s)"
            existing_user = self.db.fetch_one(query, (normalized_email,))
            
            if existing_user:
                return {"error": "Email is already registered"}
            
            # Hash password
            logger.info(f"Creating user with email: {normalized_email}")
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            logger.info(f"Password hashed successfully. Length: {len(hashed_password)}")
        
            # Insert new user
            query = """
            INSERT INTO users (email, password, first_name, last_name, role) 
            VALUES (%s, %s, %s, %s, %s)
            """
            user_id = self.db.insert(query, (normalized_email, hashed_password, first_name, last_name, role))
            
            if user_id:
                logger.info(f"User created with ID: {user_id}")
                return {
                    "id": user_id,
                    "email": normalized_email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": role
                }
            return {"error": "Error creating user"}
        except Exception as e:
            logger.error(f"Error in create_user: {str(e)}")
            return {"error": f"Error creating user: {str(e)}"}
    
    def create_business_owner(self, user_id, business_name, business_address=None, phone_number=None, tax_id=None):
        try:
            query = """
            INSERT INTO business_owners (user_id, business_name, business_address, phone_number, tax_id)
            VALUES (%s, %s, %s, %s, %s)
            """
            business_id = self.db.insert(query, (user_id, business_name, business_address, phone_number, tax_id))
            
            if business_id:
                return {
                    "id": business_id,
                    "user_id": user_id,
                    "business_name": business_name,
                    "business_address": business_address,
                    "phone_number": phone_number,
                    "tax_id": tax_id
                }
            return {"error": "Error creating business information"}
        except Exception as e:
            logger.error(f"Error in create_business_owner: {str(e)}")
            return {"error": f"Error creating business: {str(e)}"}
     
    def get_all_users(self):
        """
        Get all users for diagnostics
        """
        try:
            query = "SELECT id, email, first_name, last_name, role FROM users"
            users = self.db.fetch_all(query)
            logger.info(f"Found {len(users)} users in the database")
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []
        
    def verify_user(self, email, password):
        try:
            # Normalize email
            normalized_email = email.strip().lower() if email else ""
            logger.info(f"Trying to verify user with email: '{normalized_email}'")
            
            # Find user by normalized email
            query = "SELECT id, email, password, first_name, last_name, role FROM users WHERE LOWER(email) = LOWER(%s)"
            user = self.db.fetch_one(query, (normalized_email,))
            
            if not user:
                logger.warning(f"No user found with email: '{normalized_email}'")
                return None
            
            logger.info(f"Found user with ID: {user['id']}, email: {user['email']}")
            
            # Verify password
            if not password:
                logger.warning("Empty password provided")
                return None
                
            stored_hash = user['password']
            logger.info(f"Stored hash length: {len(stored_hash)}")
            
            try:
                password_bytes = password.encode('utf-8')
                stored_hash_bytes = stored_hash.encode('utf-8')
                
                # Password verification
                is_valid = bcrypt.checkpw(password_bytes, stored_hash_bytes)
                logger.info(f"Password verification result: {is_valid}")
                
                if is_valid:
                    # Don't send password to client
                    user_copy = user.copy()
                    del user_copy['password']
                    return user_copy
                
                logger.warning("Password verification failed")
                return None
            except Exception as e:
                logger.error(f"Error verifying password: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Error in verify_user: {str(e)}")
            return None 