import mysql.connector
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', ''),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'loan_tracker'),
            'autocommit': True,  # Enable autocommit
            'consume_results': True  # Automatically consume all results
        }
        logger.info(f"Database config: host={self.config['host']}, user={self.config['user']}, database={self.config['database']}")
        self.connection = None
        
    def connect(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                logger.info("Connecting to MySQL database...")
                self.connection = mysql.connector.connect(**self.config)
                logger.info("Connected to MySQL database successfully")
            return self.connection
        except mysql.connector.Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            self.connection = None
            return None
            
    def close(self):
        if self.connection and self.connection.is_connected():
            logger.info("Closing database connection")
            self.connection.close()
            self.connection = None
    
    def reconnect(self):
        """Force reconnection to database"""
        self.close()
        return self.connect()
            
    def execute_query(self, query, params=None):
        connection = None
        cursor = None
        try:
            connection = self.connect()
            if not connection:
                logger.error("Failed to connect to database")
                return None
                
            cursor = connection.cursor(dictionary=True)
            
            # Log query for debugging (strip to avoid logging huge queries)
            log_query = query
            if len(log_query) > 200:
                log_query = log_query[:200] + "..."
            
            if params:
                logger.info(f"Executing query: {log_query} with params: {params}")
                cursor.execute(query, params)
            else:
                logger.info(f"Executing query: {log_query}")
                cursor.execute(query)
            
            # We don't need commit because autocommit is enabled
            return cursor
        except mysql.connector.errors.InternalError as e:
            # Specifically handle the "Unread result found" error
            if "Unread result found" in str(e):
                logger.warning("Unread result found. Reconnecting and retrying...")
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass
                
                # Force reconnection
                connection = self.reconnect()
                if not connection:
                    logger.error("Failed to reconnect to database")
                    return None
                
                # Retry the query
                try:
                    cursor = connection.cursor(dictionary=True)
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    return cursor
                except Exception as retry_e:
                    logger.error(f"Error retrying query: {retry_e}")
                    return None
            else:
                logger.error(f"Error executing query: {e}")
                return None
        except mysql.connector.Error as e:
            logger.error(f"Error executing query: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            return None
            
    def fetch_all(self, query, params=None):
        cursor = None
        try:
            cursor = self.execute_query(query, params)
            if cursor:
                result = cursor.fetchall()
                count = len(result)
                logger.info(f"fetch_all returned {count} rows")
                return result
            logger.warning("fetch_all: cursor is None, returning empty list")
            return []
        except Exception as e:
            logger.error(f"Error in fetch_all: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
        
    def fetch_one(self, query, params=None):
        cursor = None
        try:
            cursor = self.execute_query(query, params)
            if cursor:
                result = cursor.fetchone()
                if result:
                    logger.info(f"fetch_one returned a row with keys: {list(result.keys())}")
                else:
                    logger.info("fetch_one returned None (no matching row)")
                return result
            logger.warning("fetch_one: cursor is None, returning None")
            return None
        except Exception as e:
            logger.error(f"Error in fetch_one: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
        
    def insert(self, query, params=None):
        cursor = None
        try:
            cursor = self.execute_query(query, params)
            if cursor:
                last_id = cursor.lastrowid
                logger.info(f"insert returned last_id: {last_id}")
                return last_id
            logger.warning("insert: cursor is None, returning None")
            return None
        except Exception as e:
            logger.error(f"Error in insert: {e}")
            return None
        finally:
            if cursor:
                cursor.close() 