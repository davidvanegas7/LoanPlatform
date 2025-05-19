from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Crear la aplicación Celery
celery_app = Celery(
    'loan_platform',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['tasks.ach_processor']
)

# Configurar la zona horaria
celery_app.conf.timezone = 'America/New_York'

# Configurar tareas periódicas
celery_app.conf.beat_schedule = {
    'generate-ach-file-daily': {
        'task': 'tasks.ach_processor.generate_daily_ach_file',
        'schedule': crontab(hour=11, minute=0),  # Todos los días a las 11:00 AM
    },
}

# Otras configuraciones
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
) 