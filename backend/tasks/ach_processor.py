import logging
import os
from datetime import datetime, date
from ach.builder import AchFile
from models.loan import Loan
from config.celery_config import celery_app
from dotenv import load_dotenv

# Configuración de registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Inicializar modelo
loan_model = Loan()

# Configuración de NACHA
NACHA_IMMEDIATE_DESTINATION = os.getenv('NACHA_IMMEDIATE_DESTINATION', '999999999') # Número de routing del banco receptor
NACHA_IMMEDIATE_ORIGIN = os.getenv('NACHA_IMMEDIATE_ORIGIN', '1234567890') # ID de la compañía originadora
NACHA_COMPANY_NAME = os.getenv('NACHA_COMPANY_NAME', 'LOAN PLATFORM')
NACHA_COMPANY_ID = os.getenv('NACHA_COMPANY_ID', '1234567890')
NACHA_ODFI_ID = os.getenv('NACHA_ODFI_ID', '99999999') # ID del banco originador
NACHA_OUTPUT_DIR = os.getenv('NACHA_OUTPUT_DIR', 'ach_files')

@celery_app.task
def generate_daily_ach_file():
    """
    Tarea que genera un archivo ACH diario con todos los pagos programados para hoy
    y lo guarda en formato NACHA para enviarlo a la red ACH.
    """
    try:
        # Crear el directorio de salida si no existe
        if not os.path.exists(NACHA_OUTPUT_DIR):
            os.makedirs(NACHA_OUTPUT_DIR)
        
        # Obtener la fecha actual
        current_date = datetime.now().date()
        logger.info(f"Generando archivo ACH para la fecha: {current_date}")
        
        # Crear batch ACH en la base de datos
        ach_batch = loan_model.create_ach_batch(current_date)
        if 'error' in ach_batch:
            logger.error(f"Error al crear el batch ACH: {ach_batch['error']}")
            return {'error': ach_batch['error']}
            
        batch_id = ach_batch['id']
        logger.info(f"Batch ACH creado con ID: {batch_id}")
        
        # Si no hay transacciones para procesar, terminar
        if ach_batch['total_transactions'] == 0:
            logger.info("No hay pagos programados para hoy")
            return {'message': 'No hay pagos programados para hoy'}
        
        # Generar el archivo NACHA
        nacha_file = create_nacha_file(batch_id, current_date)
        
        # Guardar el archivo
        file_name = f"ACH_{current_date.strftime('%Y%m%d')}_{batch_id}.txt"
        file_path = os.path.join(NACHA_OUTPUT_DIR, file_name)
        
        with open(file_path, 'w') as f:
            f.write(nacha_file.render())
        
        # Actualizar el nombre del archivo en la base de datos
        update_batch_file_name(batch_id, file_name)
        
        logger.info(f"Archivo ACH generado exitosamente: {file_path}")
        return {
            'message': f'Archivo ACH generado exitosamente', 
            'file_path': file_path, 
            'batch_id': batch_id
        }
        
    except Exception as e:
        logger.error(f"Error al generar archivo ACH: {str(e)}")
        return {'error': f'Error al generar archivo ACH: {str(e)}'}

def create_nacha_file(batch_id, effective_date):
    """
    Crea un archivo NACHA para el batch ACH especificado
    """
    # Obtener información del batch
    ach_batch = loan_model.get_ach_batch(batch_id)
    
    # Obtener todas las transacciones ACH para este batch
    ach_transactions = get_ach_transactions(batch_id)
    
    # Crear archivo ACH
    ach_file = AchFile(
        company_name=NACHA_COMPANY_NAME,
        company_id=NACHA_COMPANY_ID,
        company_entry_description='PAYMENT',
        originating_dfi_id=NACHA_ODFI_ID,
        immediate_destination=NACHA_IMMEDIATE_DESTINATION,
        immediate_origin=NACHA_IMMEDIATE_ORIGIN,
        effective_date=effective_date.strftime('%y%m%d')
    )
    
    # Agregar entradas (transacciones individuales)
    entry_count = 0
    total_amount = 0
    
    for transaction in ach_transactions:
        # Obtener datos del pago y la información bancaria de la aplicación de préstamo
        payment = get_payment_details(transaction['payment_id'])
        loan_application_data = get_loan_application_data(payment['loan_id'])
        
        if not loan_application_data:
            logger.warning(f"No se encontró información bancaria para el préstamo {payment['loan_id']}")
            continue
        
        # Extraer datos bancarios del JSON de la aplicación de préstamo
        bank_info = extract_bank_info(loan_application_data)
        
        if not bank_info:
            logger.warning(f"No se encontró información bancaria válida para el préstamo {payment['loan_id']}")
            continue
        
        # Agregar entrada al archivo
        ach_file.add_entry(
            transaction_code='27',  # Débito a cuenta corriente
            routing_number=bank_info['routing_number'],
            account_number=bank_info['account_number'],
            amount=int(float(transaction['amount']) * 100),  # Convertir a centavos
            individual_name=bank_info['account_holder_name'],
            trace_number=f"{NACHA_ODFI_ID}{str(transaction['id']).zfill(7)}"
        )
        
        # Actualizar contadores
        entry_count += 1
        total_amount += int(float(transaction['amount']) * 100)
    
    return ach_file

def get_ach_transactions(batch_id):
    """
    Obtiene todas las transacciones ACH para un batch específico
    """
    try:
        query = """
        SELECT at.*, p.loan_id
        FROM ach_transactions at
        JOIN payments p ON at.payment_id = p.id
        WHERE at.batch_id = %s AND at.status = 'pending'
        """
        transactions = loan_model.db.fetch_all(query, (batch_id,))
        logger.info(f"Se encontraron {len(transactions)} transacciones para el batch {batch_id}")
        return transactions
    except Exception as e:
        logger.error(f"Error al obtener transacciones ACH: {str(e)}")
        return []

def get_payment_details(payment_id):
    """
    Obtiene los detalles de un pago específico
    """
    return loan_model.get_payment_by_id(payment_id)

def get_loan_application_data(loan_id):
    """
    Obtiene los datos de la aplicación de préstamo asociada a un préstamo
    """
    try:
        query = """
        SELECT la.*
        FROM loan_applications la
        JOIN loans l ON la.id = l.application_id
        WHERE l.id = %s
        LIMIT 1
        """
        loan_application = loan_model.db.fetch_one(query, (loan_id,))
        return loan_application
    except Exception as e:
        logger.error(f"Error al obtener aplicación de préstamo para préstamo {loan_id}: {str(e)}")
        return None

def extract_bank_info(loan_application):
    """
    Extrae la información bancaria del JSON de la aplicación de préstamo
    """
    try:
        # Intentar obtener datos de bank_info del JSON en application_data
        if loan_application and 'application_data' in loan_application:
            app_data = loan_application['application_data']
            
            # Si application_data es una cadena JSON, convertirla a diccionario
            if isinstance(app_data, str):
                import json
                app_data = json.loads(app_data)
            
            # Buscar los datos bancarios en diferentes posibles ubicaciones
            bank_info = None
            
            # Buscar en la ubicación principal
            if 'bank_info' in app_data:
                bank_info = app_data['bank_info']
            # Buscar en financial_info si existe
            elif 'financial_info' in app_data and 'bank_info' in app_data['financial_info']:
                bank_info = app_data['financial_info']['bank_info']
            # Buscar en business_info si existe
            elif 'business_info' in app_data and 'banking' in app_data['business_info']:
                bank_info = app_data['business_info']['banking']
            
            if bank_info:
                # Asegurarse de que tiene todos los campos necesarios
                required_fields = {
                    'routing_number': ['routing_number', 'routing', 'routingNumber'],
                    'account_number': ['account_number', 'account', 'accountNumber'],
                    'account_holder_name': ['account_holder_name', 'account_holder', 'accountHolder', 'name']
                }
                
                result = {}
                
                # Buscar cada campo requerido en las posibles claves
                for field, possible_keys in required_fields.items():
                    for key in possible_keys:
                        if key in bank_info:
                            result[field] = bank_info[key]
                            break
                    
                    # Si no se encontró el campo, usar valores por defecto
                    if field not in result:
                        if field == 'account_holder_name':
                            # Intentar obtener el nombre del dueño del negocio
                            if 'business_owner' in app_data and 'name' in app_data['business_owner']:
                                result[field] = app_data['business_owner']['name']
                            elif 'business_info' in app_data and 'owner_name' in app_data['business_info']:
                                result[field] = app_data['business_info']['owner_name']
                            else:
                                result[field] = 'BUSINESS OWNER'
                        else:
                            # Para routing_number y account_number, no podemos usar valores por defecto
                            logger.warning(f"No se encontró el campo {field} en los datos bancarios")
                            return None
                
                return result
            
        logger.warning("No se encontró información bancaria en los datos de la aplicación")
        return None
    except Exception as e:
        logger.error(f"Error al extraer información bancaria: {str(e)}")
        return None

def update_batch_file_name(batch_id, file_name):
    """
    Actualiza el nombre del archivo en el batch ACH
    """
    try:
        query = """
        UPDATE ach_batches 
        SET file_name = %s, status = 'processed'
        WHERE id = %s
        """
        loan_model.db.execute_query(query, (file_name, batch_id))
        logger.info(f"Actualizado nombre de archivo para batch {batch_id}: {file_name}")
        return True
    except Exception as e:
        logger.error(f"Error al actualizar nombre de archivo para batch {batch_id}: {str(e)}")
        return False

@celery_app.task
def process_ach_return_file(file_path):
    """
    Procesa un archivo de retorno ACH y actualiza el estado de las transacciones
    """
    try:
        logger.info(f"Procesando archivo de retorno ACH: {file_path}")
        
        # Aquí iría el código para parsear el archivo de retorno ACH
        # y extraer las transacciones fallidas
        
        # Por ahora, simulamos algunas transacciones fallidas
        failed_transactions = []
        
        # Procesar las transacciones fallidas
        if failed_transactions:
            result = loan_model.process_failed_payments(failed_transactions)
            logger.info(f"Resultado del procesamiento: {result}")
            return result
        else:
            logger.info("No se encontraron transacciones fallidas")
            return {'message': 'No se encontraron transacciones fallidas'}
            
    except Exception as e:
        logger.error(f"Error al procesar archivo de retorno ACH: {str(e)}")
        return {'error': f'Error al procesar archivo de retorno ACH: {str(e)}'} 