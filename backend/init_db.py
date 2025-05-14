import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_database():
    # Obtener configuración de la base de datos
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', 'password')
    db_name = os.getenv('DB_NAME', 'loan_tracker')
    
    # Conectar a MySQL (sin seleccionar una base de datos)
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )
    
    cursor = connection.cursor()
    
    try:
        # Crear base de datos si no existe
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Base de datos '{db_name}' creada o ya existente.")
        
        # Usar la base de datos
        cursor.execute(f"USE {db_name}")
        
        # Aquí puedes inicializar tablas si lo deseas,
        # pero en nuestra implementación actual esto se hace desde el modelo User
        
        print("Inicialización de la base de datos completada.")
        
    except mysql.connector.Error as e:
        print(f"Error al crear la base de datos: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    create_database() 