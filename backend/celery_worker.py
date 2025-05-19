from config.celery_config import celery_app
import logging
import os
from dotenv import load_dotenv

# Configuración de registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Importar tareas para asegurarnos de que se registren
import tasks.ach_processor

if __name__ == '__main__':
    logger.info("Iniciando worker de Celery para procesamiento ACH...")
    celery_app.start() 