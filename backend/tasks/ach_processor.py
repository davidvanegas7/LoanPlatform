import logging
import os
from datetime import datetime, date, timedelta
import math # Añadido para math.ceil
import json
import paramiko # Añadido para SFTP
import tempfile # Añadido para archivos temporales

# Ya no se necesitan importaciones de la librería ach-file para la generación
# from ach.files import ACHFileBuilder
# from ach.constants import (
# AutoDateInput,
# BatchStandardEntryClassCode,
# TransactionCode,
# ServiceClassCode
# )

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

# Configuración de NACHA (revisar si todos son necesarios o si los nombres coinciden con los parámetros de las nuevas funciones)
NACHA_IMMEDIATE_DESTINATION = os.getenv('NACHA_IMMEDIATE_DESTINATION', '200000002') # RDFI del banco receptor (9 dígitos)
NACHA_IMMEDIATE_ORIGIN = os.getenv('NACHA_IMMEDIATE_ORIGIN', '1000000001')       # ODFI de tu banco (10 dígitos, normalmente tu EIN precedido por '1')
NACHA_DESTINATION_BANK_NAME = os.getenv('NACHA_DESTINATION_BANK_NAME', 'BANK OF AMERICA')
NACHA_COMPANY_NAME = os.getenv('NACHA_COMPANY_NAME', 'LENDINGFRONT') # Tu nombre de compañía
NACHA_COMPANY_ID = os.getenv('NACHA_COMPANY_ID', '3000000003')          # Tu ID de compañía (usualmente EIN/Tax ID, 10 dígitos)
NACHA_ODFI_ID_SHORT = os.getenv('NACHA_ODFI_ID_SHORT', NACHA_IMMEDIATE_ORIGIN[1:9] if NACHA_IMMEDIATE_ORIGIN and len(NACHA_IMMEDIATE_ORIGIN) >=9 else '00000000') # Primeros 8 dígitos del routing de tu banco ODFI (para trace numbers)
NACHA_OUTPUT_DIR = os.getenv('NACHA_OUTPUT_DIR', 'ach_files')

# Configuración SFTP desde variables de entorno
SFTP_HOSTNAME = os.getenv('SFTP_HOSTNAME')
SFTP_USERNAME = os.getenv('SFTP_USERNAME')
SFTP_PASSWORD = os.getenv('SFTP_PASSWORD')
SFTP_REMOTE_PATH = os.getenv('SFTP_REMOTE_PATH', '/uploads') # Default si no está en .env
SFTP_FAILED_PATH = os.getenv('SFTP_FAILED_PATH', '/failed') # Para descargas de retornos
SFTP_PORT = int(os.getenv('SFTP_PORT', '22')) # Default puerto SFTP

# Constantes para códigos ACH (reemplazando los enums de la librería)
SERVICE_CLASS_CODE_DEBITS_ONLY = "225" # Para lotes de solo débitos
STANDARD_ENTRY_CLASS_CODE_PPD = "PPD"  # Prearranged Payment and Deposit
TRANSACTION_CODE_CHECKING_DEBIT = "27" # Débito a cuenta de cheques

# --- Funciones de generación de archivos ACH (adaptadas de ach_generator.py) ---

def generate_ach_record_line(fields):
    """Genera una línea de registro ACH de 94 caracteres."""
    line = "".join(fields)
    if len(line) != 94:
        logger.error(f"Error crítico: La línea ACH generada no tiene 94 caracteres. Longitud: {len(line)}. Contenido: {line}")
        line = (line + " " * 94)[:94] # Truncar o rellenar para asegurar 94 caracteres.
    return line + "\n"

def ach_manual_generate_ach_file(file_header, batch_header, entries, batch_control, file_control):
    """Genera una cadena de archivo ACH a partir de los datos de registro proporcionados."""
    ach_string = ""
    ach_string += file_header
    ach_string += batch_header
    for entry in entries:
        ach_string += entry
    ach_string += batch_control
    ach_string += file_control.rstrip("\n") 
    return ach_string

def ach_manual_create_file_header(destination_routing_9digit, origin_routing_10digit, destination_name, origin_name, file_id_modifier="A", reference_code=""):
    """Crea un registro de Encabezado de Archivo (1)."""
    record_type = "1"
    priority_code = "01"
    file_creation_date = datetime.now().strftime("%y%m%d")
    file_creation_time = datetime.now().strftime("%H%M")
    record_size = "094"
    blocking_factor = "10"
    format_code = "1"
    
    immediate_destination_padded = (destination_routing_9digit.strip() + " ").ljust(10) # El espacio es por si el routing es de 9 y el campo 10
    immediate_origin_padded = origin_routing_10digit.strip().ljust(10)
    
    destination_name_padded = destination_name.strip()[:23].ljust(23)
    origin_name_padded = origin_name.strip()[:23].ljust(23)
    reference_code_padded = reference_code.strip()[:8].ljust(8)
    
    fields = [
        record_type,
        priority_code,
        immediate_destination_padded,
        immediate_origin_padded,
        file_creation_date,
        file_creation_time,
        file_id_modifier.upper(),
        record_size,
        blocking_factor,
        format_code,
        destination_name_padded,
        origin_name_padded,
        reference_code_padded
    ]
    return generate_ach_record_line(fields)

def ach_manual_create_batch_header(service_class_code, company_name, company_identification_10digit, standard_entry_class_code, company_entry_description, effective_entry_date_yymmdd, originating_dfi_id_8digit, batch_number_str_7digit="0000001"):
    """Crea un registro de Encabezado de Lote (5)."""
    record_type = "5"
    company_name_padded = company_name.strip()[:16].ljust(16)
    company_discretionary_data = "".ljust(20) 
    company_id_padded = company_identification_10digit.strip().ljust(10)
    company_entry_description_padded = company_entry_description.strip()[:10].ljust(10)
    settlement_date_julian = "   " 
    originator_status_code = "1" 
    originating_dfi_id_padded = originating_dfi_id_8digit.strip()[:8].ljust(8)
    
    fields = [
        record_type,                    
        service_class_code,             
        company_name_padded,            
        company_discretionary_data,     
        company_id_padded,              
        standard_entry_class_code,      
        company_entry_description_padded, 
        effective_entry_date_yymmdd,    
        settlement_date_julian,         
        originator_status_code,         
        originating_dfi_id_padded,      
        "".ljust(6), # Espacio reservado 82-87
        batch_number_str_7digit.zfill(7) # Pos 88-94
    ]
    return generate_ach_record_line(fields)

def ach_manual_create_entry_detail(transaction_code_2digit, receiving_dfi_routing_9digit, dda_account_number, amount_cents_int, individual_id_number, individual_name, trace_number_field_15char: str, discretionary_data="", addenda_record_indicator="0"):
    """Crea un registro de Detalle de Entrada (6).
    trace_number_field_15char debe ser el trace number completo de 15 caracteres.
    """
    record_type = "6"
    receiving_dfi_routing_padded = receiving_dfi_routing_9digit.strip()[:9].ljust(9)
    dda_account_number_padded = dda_account_number.strip()[:17].ljust(17)
    amount_padded = str(amount_cents_int).zfill(10)
    individual_id_number_padded = individual_id_number.strip()[:15].ljust(15)
    individual_name_padded = individual_name.strip()[:22].ljust(22)
    discretionary_data_padded = discretionary_data.strip()[:2].ljust(2)

    if len(trace_number_field_15char) != 15:
        logger.warning(f"El trace_number_field_15char proporcionado '{trace_number_field_15char}' no tiene 15 caracteres. Se ajustará o podría causar errores en el procesamiento ACH.")
        # Ajustar a 15 caracteres, rellenando con espacios a la derecha o truncando.
        # Es crucial que este valor sea correcto según las especificaciones NACHA y cómo se almacena/busca.
        trace_number_field_15char = trace_number_field_15char.ljust(15)[:15]

    fields = [
        record_type,
        transaction_code_2digit,
        receiving_dfi_routing_padded,
        dda_account_number_padded,
        amount_padded,
        individual_id_number_padded,
        individual_name_padded,
        discretionary_data_padded,
        addenda_record_indicator,
        trace_number_field_15char # Usar directamente el trace number proporcionado
    ]
    return generate_ach_record_line(fields)

def ach_manual_create_batch_control(service_class_code_3digit, entry_addenda_count_6digit_int, entry_hash_total_10digit_int, total_debit_amount_cents_12digit_int, total_credit_amount_cents_12digit_int, company_identification_10digit, originating_dfi_id_8digit, batch_number_str_7digit="0000001"):
    """Crea un registro de Control de Lote (8)."""
    record_type = "8"
    message_authentication_code = "".ljust(19) 
    reserved_space = "".ljust(6) 
    originating_dfi_id_padded = originating_dfi_id_8digit.strip()[:8].ljust(8)

    fields = [
        record_type,
        service_class_code_3digit,
        str(entry_addenda_count_6digit_int).zfill(6),
        str(entry_hash_total_10digit_int).zfill(10),
        str(total_debit_amount_cents_12digit_int).zfill(12),
        str(total_credit_amount_cents_12digit_int).zfill(12),
        company_identification_10digit.strip().ljust(10),
        message_authentication_code,
        reserved_space,
        originating_dfi_id_padded,
        batch_number_str_7digit.zfill(7)
    ]
    return generate_ach_record_line(fields)

def ach_manual_create_file_control(batch_count_int, block_count_int, entry_addenda_count_int, entry_hash_total_int, total_debit_amount_cents_int, total_credit_amount_cents_int):
    """Crea un registro de Control de Archivo (9)."""
    record_type = "9"
    reserved_space = "".ljust(39) 
    
    fields = [
        record_type,
        str(batch_count_int).zfill(6),
        str(block_count_int).zfill(6),
        str(entry_addenda_count_int).zfill(8),
        str(entry_hash_total_int).zfill(10), 
        str(total_debit_amount_cents_int).zfill(12),
        str(total_credit_amount_cents_int).zfill(12),
        reserved_space
    ]
    return generate_ach_record_line(fields)

# --- Fin de funciones de generación de archivos ACH ---

# --- Función de subida SFTP ---
def upload_file_to_sftp(local_file_path, remote_file_name):
    """Sube un archivo local a un servidor SFTP."""
    try:
        if not all([SFTP_HOSTNAME, SFTP_USERNAME, SFTP_PASSWORD, SFTP_REMOTE_PATH]):
            logger.error("SFTP: Configuración incompleta (hostname, username, password, o remote_path faltante). No se subirá el archivo.")
            return {'error': "SFTP configuration incomplete."}

        # Asegurar que el remote_path sea estilo Unix y termine con / si es un directorio
        # y luego añadir el nombre del archivo.
        # remote_dir = SFTP_REMOTE_PATH.rstrip('/') + '/'
        # full_remote_path = remote_dir + remote_file_name.lstrip('/')

        # Construcción más segura de la ruta remota
        # Eliminar barras iniciales/finales de remote_file_name si las tuviera para evitar // o rutas absolutas inesperadas
        clean_remote_file_name = remote_file_name.strip('/')
        if not SFTP_REMOTE_PATH.endswith('/'):
            full_remote_path = SFTP_REMOTE_PATH + '/' + clean_remote_file_name
        else:
            full_remote_path = SFTP_REMOTE_PATH + clean_remote_file_name

        logger.info(f"SFTP: Intentando conectar a {SFTP_HOSTNAME}:{SFTP_PORT} como {SFTP_USERNAME}")
        transport = paramiko.Transport((SFTP_HOSTNAME, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        logger.info(f"SFTP: Conectado. Subiendo {local_file_path} a {full_remote_path}")
        sftp.put(local_file_path, full_remote_path)
        logger.info(f"SFTP: Archivo {local_file_path} subido exitosamente a {full_remote_path}")

        sftp.close()
        transport.close()
        return {'message': 'Archivo subido a SFTP exitosamente', 'sftp_path': full_remote_path}
    except paramiko.ssh_exception.AuthenticationException:
        logger.error(f"SFTP: Falló la autenticación para {SFTP_USERNAME}@{SFTP_HOSTNAME}.")
        return {'error': 'SFTP Authentication failed.'}
    except paramiko.ssh_exception.SSHException as ssh_ex:
        logger.error(f"SFTP: Error de SSH al conectar o transferir: {str(ssh_ex)}")
        return {'error': f'SFTP SSH error: {str(ssh_ex)}'}
    except FileNotFoundError:
        logger.error(f"SFTP: Archivo local no encontrado: {local_file_path}")
        return {'error': f'SFTP: Local file not found {local_file_path}'}
    except Exception as e:
        logger.error(f"SFTP: Error inesperado durante la subida: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {'error': f'SFTP: Unexpected error during upload: {str(e)}'}

@celery_app.task
def generate_daily_ach_file():
    """
    Tarea que genera un archivo ACH diario usando la implementación manual y lo sube a SFTP.
    """
    sftp_upload_result = None # Inicializar para asegurar que esté definida
    try:
        if not os.path.exists(NACHA_OUTPUT_DIR):
            os.makedirs(NACHA_OUTPUT_DIR)
        
        current_date = datetime.now().date()
        logger.info(f"Generando archivo ACH para la fecha: {current_date} usando implementación manual")
        
        ach_batch_db = loan_model.create_ach_batch(current_date)
        if 'error' in ach_batch_db:
            logger.error(f"Error al crear el batch ACH en DB: {ach_batch_db['error']}")
            return {'error': ach_batch_db['error']}
            
        batch_id_db = ach_batch_db['id']
        # Generar un número de lote NACHA de 7 dígitos. Puede ser derivado del ID de la BD o secuencial.
        nacha_batch_number_str = str(batch_id_db % 10000000).zfill(7) # Ejemplo: tomar últimos 7 dígitos del ID de batch de BD

        logger.info(f"Batch ACH en DB creado con ID: {batch_id_db}. Usando número de lote NACHA: {nacha_batch_number_str}")
        
        if ach_batch_db['total_transactions'] == 0:
            logger.info("No hay pagos programados para hoy (manual)")
            return {'message': 'No hay pagos programados para hoy'}
        
        nacha_file_content_str = create_nacha_file_manually(batch_id_db, current_date, nacha_batch_number_str)
        
        # Chequeo robustecido: si es un dict, es un mensaje/error, no contenido de archivo.
        if isinstance(nacha_file_content_str, dict):
            if 'error' in nacha_file_content_str:
                logger.error(f"Error desde create_nacha_file_manually: {nacha_file_content_str['error']}")
            elif 'message' in nacha_file_content_str:
                logger.info(f"Mensaje desde create_nacha_file_manually: {nacha_file_content_str['message']}")
            else:
                logger.warning(f"Respuesta inesperada (dict) desde create_nacha_file_manually: {nacha_file_content_str}")
            return nacha_file_content_str # Retornar el dict directamente

        file_name = f"ACH_manual_{current_date.strftime('%Y%m%d')}_{batch_id_db}.txt"
        file_path = os.path.join(NACHA_OUTPUT_DIR, file_name)
        
        with open(file_path, 'w', newline='\r\n') as f: # Usar CRLF para newlines
            f.write(nacha_file_content_str)
        
        update_batch_file_name(batch_id_db, file_name) 
        
        logger.info(f"Archivo ACH (manual) generado localmente: {file_path}")

        # Subir a SFTP
        if os.path.exists(file_path):
            # El segundo argumento para upload_file_to_sftp es solo el nombre del archivo remoto.
            # La ruta base del directorio remoto se toma de SFTP_REMOTE_PATH dentro de la función.
            sftp_upload_result = upload_file_to_sftp(file_path, file_name) 
            if sftp_upload_result and 'error' in sftp_upload_result:
                logger.error(f"SFTP: Falló la subida del archivo {file_name}: {sftp_upload_result['error']}")
            elif sftp_upload_result and 'message' in sftp_upload_result:
                 logger.info(f"SFTP: {sftp_upload_result['message']} ({sftp_upload_result.get('sftp_path')})")
        else:
            logger.error(f"SFTP: El archivo local {file_path} no existe, no se puede subir.")
            sftp_upload_result = {'error': f'Local file {file_path} not found for SFTP upload'}
        
        return {
            'message': 'Archivo ACH (manual) generado exitosamente', 
            'file_path': file_path, 
            'batch_id': batch_id_db,
            'sftp_status': sftp_upload_result
        }
        
    except Exception as e:
        logger.error(f"Error al generar archivo ACH (manual) y/o subir a SFTP: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'error': f'Error en la tarea generate_daily_ach_file: {str(e)}',
            'sftp_status': sftp_upload_result if sftp_upload_result else "SFTP no intentado debido a error previo"
        }

def create_nacha_file_manually(db_batch_id, processing_date_obj, nacha_batch_number_str):
    """
    Crea un archivo NACHA usando la implementación manual.
    processing_date_obj es un objeto date.
    nacha_batch_number_str es el número de lote de 7 dígitos para el archivo.
    """
    try:
        ach_transactions_db = get_ach_transactions(db_batch_id)
        if not ach_transactions_db:
            logger.info(f"Manual: No se encontraron transacciones ACH para el batch de DB {db_batch_id}")
            # Devuelve un error o un mensaje indicando que no se generará un archivo porque no hay transacciones.
            # Un archivo ACH no puede estar vacío, pero un archivo con 0 transacciones sí se puede generar (solo headers/controls).
            # Sin embargo, el flujo actual espera transacciones.
            return {'message': f"No hay transacciones para el batch {db_batch_id}, no se generará archivo."}


        # --- File Header ---
        file_header_rec = ach_manual_create_file_header(
            destination_routing_9digit=NACHA_IMMEDIATE_DESTINATION,
            origin_routing_10digit=NACHA_IMMEDIATE_ORIGIN,
            destination_name=NACHA_DESTINATION_BANK_NAME,
            origin_name=NACHA_COMPANY_NAME, 
            reference_code="LOANPAY" 
        )

        # --- Batch Header ---
        effective_entry_date_str = processing_date_obj.strftime("%y%m%d")
        
        batch_header_rec = ach_manual_create_batch_header(
            service_class_code=SERVICE_CLASS_CODE_DEBITS_ONLY, 
            company_name=NACHA_COMPANY_NAME, 
            company_identification_10digit=NACHA_COMPANY_ID,
            standard_entry_class_code=STANDARD_ENTRY_CLASS_CODE_PPD,
            company_entry_description="PAYMENT", 
            effective_entry_date_yymmdd=effective_entry_date_str,
            originating_dfi_id_8digit=NACHA_ODFI_ID_SHORT, 
            batch_number_str_7digit=nacha_batch_number_str 
        )

        # --- Entry Detail Records ---
        entry_detail_recs = []
        total_debit_amount_cents_batch = 0
        total_credit_amount_cents_batch = 0 
        entry_hash_accumulator_batch = 0
        entry_addenda_count_batch = 0 # Solo registros '6' y '7'. Para PPD sin addendas, solo '6'.
        
        entry_sequence_counter = 0 # Secuencial para los últimos 7 dígitos del Trace Number

        for transaction in ach_transactions_db:
            entry_sequence_counter += 1 # Incrementa para cada entrada
            payment = get_payment_details(transaction['payment_id'])
            if not payment:
                logger.warning(f"Manual: No se encontraron detalles de pago para payment_id {transaction['payment_id']}. Saltando transacción.")
                continue
                
            loan_application_data = get_loan_application_data(payment['loan_id'])
            if not loan_application_data:
                logger.warning(f"Manual: No info de app para préstamo {payment['loan_id']} (transacción DB ID {transaction['id']}). Saltando.")
                continue
            
            bank_info = extract_bank_info(loan_application_data)
            if not bank_info or not bank_info.get('routing_number') or not bank_info.get('account_number') or not bank_info.get('account_holder_name'):
                logger.warning(f"Manual: Info bancaria incompleta para préstamo {payment['loan_id']} (transacción DB ID {transaction['id']}). Saltando.")
                continue

            routing_number_full_9digit = bank_info['routing_number'].strip()
            if len(routing_number_full_9digit) != 9 or not routing_number_full_9digit.isdigit():
                logger.warning(f"Manual: Número de ruta inválido '{routing_number_full_9digit}' para préstamo {payment['loan_id']}. Saltando.")
                continue
            
            ach_transaction_code = TRANSACTION_CODE_CHECKING_DEBIT 

            try:
                amount_in_cents = int(float(transaction['amount']) * 100)
            except ValueError:
                logger.warning(f"Manual: Monto inválido '{transaction['amount']}' para préstamo {payment['loan_id']}. Saltando.")
                continue

            total_debit_amount_cents_batch += amount_in_cents
            
            try: # Sumar los primeros 8 dígitos del número de ruta del RDFI
                entry_hash_accumulator_batch += int(routing_number_full_9digit[:8])
            except ValueError:
                 logger.error(f"Manual: Número de ruta {routing_number_full_9digit} no es numérico para cálculo de hash. Saltando transacción.")
                 continue # O manejar de otra forma, e.g., asignar 0 a este sumando.

            # Se asume que transaction['trace_number'] contiene el trace number de 15 caracteres
            # que fue previamente generado (ej. a partir del transaction id) y almacenado en la BD.
            trace_number_from_db = transaction.get('trace_number')

            if not trace_number_from_db or len(trace_number_from_db) != 15:
                logger.error(f"Manual: Trace number inválido o ausente ('{trace_number_from_db}') para transacción ID {transaction.get('id')}. Saltando. Asegúrese de que ach_transactions.trace_number esté poblado con un valor de 15 caracteres.")
                continue

            entry_rec = ach_manual_create_entry_detail(
                transaction_code_2digit=ach_transaction_code,
                receiving_dfi_routing_9digit=routing_number_full_9digit,
                dda_account_number=bank_info['account_number'],
                amount_cents_int=amount_in_cents,
                individual_id_number=str(payment.get('loan_id', transaction['id'])),
                individual_name=bank_info['account_holder_name'],
                trace_number_field_15char=trace_number_from_db, # Usar el trace_number de la BD
                addenda_record_indicator="0" # 0 si no hay addenda
            )
            entry_detail_recs.append(entry_rec)
            entry_addenda_count_batch += 1 # Cada registro de entrada tipo '6' cuenta como 1

        if not entry_detail_recs: # Si después de iterar no hay entradas válidas
            logger.info("Manual: No hay entradas válidas para añadir al batch después de procesar transacciones.")
            # Podríamos decidir generar un archivo "vacío" (solo con controles y headers), o retornar error.
            # Por ahora, para ser consistentes con el chequeo inicial de ach_transactions_db:
            return {'message': "No hay entradas válidas para procesar con implementación manual."}

        # --- Batch Control ---
        batch_entry_hash_10_digits = int(str(entry_hash_accumulator_batch)[-10:]) # Tomar últimos 10 dígitos

        batch_control_rec = ach_manual_create_batch_control(
            service_class_code_3digit=SERVICE_CLASS_CODE_DEBITS_ONLY,
            entry_addenda_count_6digit_int=entry_addenda_count_batch,
            entry_hash_total_10digit_int=batch_entry_hash_10_digits,
            total_debit_amount_cents_12digit_int=total_debit_amount_cents_batch,
            total_credit_amount_cents_12digit_int=total_credit_amount_cents_batch, 
            company_identification_10digit=NACHA_COMPANY_ID,
            originating_dfi_id_8digit=NACHA_ODFI_ID_SHORT,
            batch_number_str_7digit=nacha_batch_number_str 
        )

        # --- File Control ---
        total_batches_in_file = 1 # Asumiendo un solo lote por archivo
        total_entry_addenda_in_file = entry_addenda_count_batch # Total de registros 6 y 7 en todos los lotes
        total_debit_amount_file = total_debit_amount_cents_batch
        total_credit_amount_file = total_credit_amount_cents_batch
        file_entry_hash_total_10_digits = batch_entry_hash_10_digits # Suma de todos los hash de lote (aquí solo 1)

        # Block count: Total de registros (FH, BH, N Entradas, BC, FC) / 10, redondeado hacia arriba.
        # Cada registro generado por las funciones ach_manual_create_* ya incluye un \n.
        # El total de líneas físicas es 1(FH)+1(BH)+N(Entries)+1(BC)+1(FC)
        total_physical_records_in_file = 1 + 1 + len(entry_detail_recs) + 1 + 1
        block_count_file = math.ceil(total_physical_records_in_file / 10.0)

        file_control_rec = ach_manual_create_file_control(
            batch_count_int=total_batches_in_file,
            block_count_int=int(block_count_file), # Debe ser entero
            entry_addenda_count_int=total_entry_addenda_in_file,
            entry_hash_total_int=file_entry_hash_total_10_digits,
            total_debit_amount_cents_int=total_debit_amount_file,
            total_credit_amount_cents_int=total_credit_amount_file
        )

        # --- Generar el contenido del archivo ---
        return ach_manual_generate_ach_file(
            file_header_rec, 
            batch_header_rec, 
            entry_detail_recs, 
            batch_control_rec, 
            file_control_rec
        )

    except Exception as e:
        logger.error(f"Error detallado en create_nacha_file_manually: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {'error': f"Error detallado creando archivo con implementación manual: {str(e)}"}

# --- Funciones de obtención de datos (sin cambios significativos en su lógica interna) ---
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
        logger.warning(f"Manual: Revisando loan_application: {loan_application}")
        if loan_application:
            app_data = loan_application
            if isinstance(app_data, str):
                app_data = json.loads(app_data)
            
            bank_info_data = None
            possible_bank_info_paths = [
                ['financial_info', 'business_bank_account'], 
                ['bank_info'],
                ['financial_info', 'bank_info'], 
                ['business_info', 'banking']
            ]
            for path in possible_bank_info_paths:
                current_data_node = app_data
                valid_path = True
                try:
                    for key_part in path:
                        # Si el nodo actual es una cadena, intentar decodificarla como JSON
                        if isinstance(current_data_node, str):
                            try:
                                current_data_node = json.loads(current_data_node)
                            except json.JSONDecodeError:
                                valid_path = False # No se pudo decodificar, esta sub-ruta no es válida
                                break
                        
                        # Después de un posible parseo, el nodo debe ser un diccionario para continuar
                        if not isinstance(current_data_node, dict) or key_part not in current_data_node:
                            valid_path = False # No es un diccionario o la clave no existe
                            break
                            
                        current_data_node = current_data_node[key_part] # Avanzar al siguiente nivel
                    
                    if valid_path:
                        # Si el nodo final es una cadena JSON, parsearla también
                        if isinstance(current_data_node, str):
                            try:
                                current_data_node = json.loads(current_data_node)
                            except json.JSONDecodeError:
                                current_data_node = None # Falló el parseo del nodo final
                        
                        if current_data_node and isinstance(current_data_node, dict):
                            bank_info_data = current_data_node
                            break # Ruta válida encontrada y bank_info_data es un diccionario

                except (KeyError, TypeError):
                    # Estos errores pueden ocurrir si una clave no existe o si se intenta indexar incorrectamente.
                    # Continuar con la siguiente ruta es el comportamiento deseado.
                    continue
            
            if bank_info_data:
                result = {}
                key_map = {
                    'routing_number': ['routing_number', 'routing', 'routingNumber'],
                    'account_number': ['account_number', 'account', 'accountNumber'],
                    'account_holder_name': ['account_holder_name', 'account_holder', 'accountHolder', 'nameOnAccount', 'name']
                }
                for field, possible_keys in key_map.items():
                    for key in possible_keys:
                        if key in bank_info_data and bank_info_data[key]:
                            result[field] = str(bank_info_data[key]).strip()
                            break
                
                # Añadir routing number de prueba si no se encontró ninguno
                if not result.get('routing_number'):
                    logger.info(f"Manual: No se encontró 'routing_number' en los datos bancarios para app_id {loan_application.get('id') if loan_application else 'desconocida'}. Usando valor de prueba '123123123'.")
                    result['routing_number'] = "123123123" # Número de ruta de prueba

                if not result.get('account_holder_name'):
                    owner_name_paths = [
                        ['business_owner', 'name'],
                        ['business_info', 'owner_name']
                    ]
                    for path in owner_name_paths:
                        temp_data = app_data
                        try:
                            for key_part in path:
                                temp_data = temp_data[key_part]
                            if temp_data:
                                result['account_holder_name'] = str(temp_data).strip()
                                break
                        except (KeyError, TypeError):
                            continue
                    if not result.get('account_holder_name'):
                        result['account_holder_name'] = loan_application.get('business_name', NACHA_COMPANY_NAME)
                        logger.warning(f"Manual: No se pudo determinar account_holder_name para la app_id {loan_application.get('id') if loan_application else 'desconocida'}, usando fallback.")

                if all(k in result and result[k] for k in ['routing_number', 'account_number', 'account_holder_name']):
                    if not (result['routing_number'].isdigit() and len(result['routing_number']) == 9):
                        logger.warning(f"Manual: Routing number inválido '{result['routing_number']}' para app_id {loan_application.get('id') if loan_application else 'desconocida'}")
                        return None
                    if not result['account_number'].isalnum(): # Puede ser alfanumérico, no solo isdigit
                         logger.warning(f"Manual: Account number inválido '{result['account_number']}' para app_id {loan_application.get('id') if loan_application else 'desconocida'}")
                         return None
                    return result
                else:
                    missing_fields = [k for k in ['routing_number', 'account_number', 'account_holder_name'] if not result.get(k)]
                    logger.warning(f"Manual: Faltan campos bancarios requeridos ({missing_fields}) en la app_id {loan_application.get('id') if loan_application else 'desconocida'}. Datos bancarios: {bank_info_data}")
                    return None
        
        logger.warning(f"Manual: No se encontró 'application_data' o info bancaria relevante en la app_id {loan_application.get('id') if loan_application else 'desconocida'}")
        return None
    except Exception as e:
        logger.error(f"Error al extraer información bancaria (Manual) de la app_id {loan_application.get('id') if loan_application else 'desconocida'}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def update_batch_file_name(batch_id, file_name):
    """
    Actualiza el nombre del archivo en el batch ACH de la base de datos
    """
    try:
        query = """
        UPDATE ach_batches 
        SET file_name = %s, status = 'processed'
        WHERE id = %s
        """
        loan_model.db.execute_query(query, (file_name, batch_id))
        logger.info(f"Actualizado nombre de archivo para batch DB {batch_id}: {file_name}")
        return True
    except Exception as e:
        logger.error(f"Error al actualizar nombre de archivo para batch DB {batch_id}: {str(e)}")
        return False

@celery_app.task
def process_ach_return_file():
    """
    Descarga un archivo de retorno ACH de SFTP del día anterior, lo parsea,
    y actualiza el estado de las transacciones fallidas.
    """
    try:
        yesterday = date.today() - timedelta(days=1)
        logger.info(f"Procesando archivo de retorno ACH para la fecha: {yesterday}")

        local_return_file_path = download_return_file_from_sftp(yesterday)

        if not local_return_file_path:
            message = f"No se encontró o no se pudo descargar el archivo de retorno ACH para {yesterday} desde SFTP."
            logger.info(message)
            return {'message': message, 'status': 'no_file_found'}

        logger.info(f"Archivo de retorno descargado a: {local_return_file_path}")
        
        failed_transactions_details = []
        try:
            with open(local_return_file_path, 'r') as f:
                file_content = f.read()
            
            if not file_content.strip(): 
                 logger.warning(f"El archivo de retorno {local_return_file_path} está vacío.")
                 return {'message': f"El archivo de retorno para {yesterday} está vacío.", 'status': 'file_empty'}

            failed_transactions_details = parse_nacha_return_file_content(file_content)
        
        except Exception as parse_ex:
            logger.error(f"Error parseando el archivo de retorno {local_return_file_path}: {str(parse_ex)}")
            import traceback
            logger.error(traceback.format_exc())
            return {'error': f"Error parseando archivo de retorno: {str(parse_ex)}", 'status': 'parsing_error'}
        finally:
            if os.path.exists(local_return_file_path):
                try:
                    os.remove(local_return_file_path)
                    logger.info(f"Archivo temporal {local_return_file_path} eliminado.")
                except Exception as rm_err:
                    logger.error(f"Error eliminando archivo temporal {local_return_file_path}: {rm_err}")

        if failed_transactions_details:
            logger.info(f"Procesando {len(failed_transactions_details)} transacciones fallidas del archivo de retorno.")
            processing_result = loan_model.process_failed_payments(failed_transactions_details)
            logger.info(f"Resultado del procesamiento de pagos fallidos: {processing_result}")
            return {
                'message': f"{len(failed_transactions_details)} transacciones fallidas procesadas.", 
                'details': processing_result,
                'status': 'completed'
            }
        else:
            logger.info("No se encontraron transacciones fallidas procesables en el archivo de retorno.")
            return {'message': 'No se encontraron transacciones fallidas procesables.', 'status': 'no_failed_transactions'}
            
    except Exception as e:
        logger.error(f"Error general en process_ach_return_file: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {'error': f'Error general en process_ach_return_file: {str(e)}', 'status': 'task_error'}

# --- Funciones para Procesamiento de Archivos de Retorno ACH ---
def download_return_file_from_sftp(target_date: date):
    """
    Descarga un archivo de retorno ACH de SFTP para una fecha específica.
    Busca un archivo en SFTP_FAILED_PATH que contenga target_date en formato YYYYMMDD.
    """
    if not all([SFTP_HOSTNAME, SFTP_USERNAME, SFTP_PASSWORD, SFTP_FAILED_PATH]):
        logger.error("SFTP Return: Configuración SFTP incompleta para descargar archivo de retorno.")
        return None

    target_date_str = target_date.strftime("%Y%m%d")
    downloaded_file_path = None
    transport = None
    sftp = None

    try:
        logger.info(f"SFTP Return: Conectando a {SFTP_HOSTNAME}:{SFTP_PORT} como {SFTP_USERNAME} para buscar en {SFTP_FAILED_PATH}")
        transport = paramiko.Transport((SFTP_HOSTNAME, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        logger.info(f"SFTP Return: Listando archivos en {SFTP_FAILED_PATH}")
        files_in_failed_path = sftp.listdir(SFTP_FAILED_PATH)
        
        found_file_name = None
        for filename in files_in_failed_path:
            if target_date_str in filename: 
                found_file_name = filename
                logger.info(f"SFTP Return: Archivo encontrado para {target_date_str}: {filename}")
                break
        
        if found_file_name:
            remote_full_path = f"{SFTP_FAILED_PATH.rstrip('/')}/{found_file_name}"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", prefix=f"ach_return_{target_date_str}_")
            local_temp_path = temp_file.name
            temp_file.close() 

            logger.info(f"SFTP Return: Descargando {remote_full_path} a {local_temp_path}")
            sftp.get(remote_full_path, local_temp_path)
            logger.info(f"SFTP Return: Archivo descargado exitosamente: {local_temp_path}")
            downloaded_file_path = local_temp_path
        else:
            logger.info(f"SFTP Return: No se encontró ningún archivo de retorno para la fecha {target_date_str} en {SFTP_FAILED_PATH}")

    except Exception as e:
        logger.error(f"SFTP Return: Error durante la descarga del archivo de retorno: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        if downloaded_file_path and os.path.exists(downloaded_file_path):
             os.remove(downloaded_file_path)
        return None
    finally:
        if sftp:
            sftp.close()
        if transport:
            transport.close()
            
    return downloaded_file_path

def parse_nacha_return_file_content(file_content_string: str):
    """
    Parsea el contenido de un archivo de retorno NACHA e identifica transacciones fallidas.
    Devuelve una lista de diccionarios para process_failed_payments.
    """
    failed_transactions_for_processing = []
    lines = file_content_string.splitlines()
    current_entry_detail_trace_number = None
    logger.info(f"Parse Return: Analizando {len(lines)} líneas del archivo de retorno.")

    for line in lines:
        if not line or len(line) < 1:
            continue
        record_type = line[0]

        if record_type == '6': 
            current_entry_detail_trace_number = line[79:94].strip() 
            logger.debug(f"Parse Return: Encontrado Entry Detail con Trace Number: {current_entry_detail_trace_number}")
        elif record_type == '7' and current_entry_detail_trace_number: 
            addenda_type_code = line[1:3]
            if addenda_type_code == "99": 
                return_reason_code = line[3:6].strip()
                logger.info(f"Parse Return: Encontrado Addenda de Retorno (99) para Trace {current_entry_detail_trace_number}. Código: {return_reason_code}")
                query = "SELECT payment_id FROM ach_transactions WHERE trace_number = %s LIMIT 1"
                db_result = loan_model.db.fetch_one(query, (current_entry_detail_trace_number,))
                if db_result and db_result.get('payment_id'):
                    payment_id = db_result['payment_id']
                    failed_transactions_for_processing.append({
                        'payment_id': payment_id,
                        'failure_reason': return_reason_code 
                    })
                    logger.info(f"Parse Return: Transacción para payment_id {payment_id} marcada como fallida con código {return_reason_code}.")
                else:
                    logger.warning(f"Parse Return: No se encontró payment_id para el trace_number {current_entry_detail_trace_number} en la base de datos.")
                current_entry_detail_trace_number = None 
        elif record_type in ['1', '5', '8', '9']:
            current_entry_detail_trace_number = None 
        
    logger.info(f"Parse Return: Total de transacciones fallidas identificadas para procesamiento: {len(failed_transactions_for_processing)}")
    return failed_transactions_for_processing

# La función create_nacha_file_with_achfile_lib ya no es necesaria
# y puede ser eliminada si se confirma que todo funciona con la manual.
# Si existía, debería ser eliminada o comentada completamente. 