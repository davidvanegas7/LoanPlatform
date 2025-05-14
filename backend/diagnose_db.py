import os
import sys
import logging
from config.db import Database
from models.user import User
import bcrypt

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def diagnose_database():
    """Database connection diagnostics"""
    logger.info("=== DATABASE DIAGNOSTICS ===")
    
    # Check environment variables
    logger.info("Checking environment variables...")
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_pass = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'loan_tracker')
    
    logger.info(f"DB_HOST: {db_host}")
    logger.info(f"DB_USER: {db_user}")
    logger.info(f"DB_NAME: {db_name}")
    logger.info(f"DB_PASSWORD: {'***' if db_pass else 'no password set'}")
    
    # Test connection
    logger.info("Testing database connection...")
    try:
        db = Database()
        connection = db.connect()
        
        if connection:
            logger.info("✅ Successfully connected to database")
            
            # Check if tables exist
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            tables_list = []
            for table in tables:
                tables_list.append(list(table.values())[0])
            
            logger.info(f"Tables found: {tables_list}")
            
            if 'users' in tables_list:
                logger.info("✅ 'users' table found")
                
                # Check table structure
                cursor.execute("DESCRIBE users")
                columns = cursor.fetchall()
                logger.info(f"Columns in 'users' table: {[col['Field'] for col in columns]}")
                
                # Count users
                cursor.execute("SELECT COUNT(*) as count FROM users")
                user_count = cursor.fetchone()['count']
                logger.info(f"Number of users in database: {user_count}")
                
                if user_count > 0:
                    # Show all users
                    cursor.execute("SELECT id, email, first_name, last_name, role FROM users")
                    users = cursor.fetchall()
                    for user in users:
                        logger.info(f"User: {user}")
                else:
                    logger.warning("⚠️ No users in the database")
            else:
                logger.error("❌ 'users' table not found")
                
            cursor.close()
        else:
            logger.error("❌ Could not connect to database")
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {e}")

def test_user_creation():
    """Test user creation and verification"""
    logger.info("=== USER CREATION AND VERIFICATION TEST ===")
    
    # Create test user
    email = f"test_{int(__import__('time').time())}@example.com"
    password = "testpassword123"
    
    logger.info(f"Creating test user with email: {email}")
    
    user_model = User()
    result = user_model.create_user(
        email=email,
        password=password,
        first_name="Test",
        last_name="User"
    )
    
    if "error" in result:
        logger.error(f"❌ Error creating user: {result['error']}")
        return
    
    logger.info(f"✅ User created successfully with ID: {result['id']}")
    
    # Verify the newly created user
    logger.info("Verifying the newly created user...")
    
    verify_result = user_model.verify_user(email, password)
    
    if verify_result:
        logger.info(f"✅ User verified successfully: {verify_result}")
    else:
        logger.error("❌ Could not verify user")
        
        # Try to find user directly
        db = Database()
        cursor = db.execute_query("SELECT * FROM users WHERE email = %s", (email,))
        if cursor:
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                logger.info(f"User found in database: {user}")
                
                # Try to verify password manually
                stored_hash = user['password']
                is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
                logger.info(f"Manual password verification: {'✅ Successful' if is_valid else '❌ Failed'}")
            else:
                logger.error(f"❌ User with email '{email}' not found in database")

if __name__ == "__main__":
    logger.info("Starting diagnostics...")
    
    diagnose_database()
    
    # If 'test' argument is provided, create a test user
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_user_creation()
    
    logger.info("Diagnostics completed.") 