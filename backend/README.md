# Loan Tracker Backend API

This API provides authentication endpoints (registration and login) using Flask and MySQL.

## Requirements

- Python 3.8+
- MySQL

## Setup

1. Install dependencies:

```bash
pip3 install -r requirements.txt
```

2. Create a `.env` file in the `backend` folder with the following content:

```
# Database configuration
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=loan_tracker

# JWT configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ACCESS_TOKEN_EXPIRES=3600
```

3. Initialize the database:

```bash
python3 init_db.py
```

## Execution

To start the development server:

```bash
python3 app.py
```

The API will be available at `http://localhost:5000`.

## API Documentation

The API is documented with Swagger UI, accessible at:

```
http://localhost:5000/docs/
```

This interface provides interactive documentation of all available endpoints, including:

- Endpoint descriptions
- Required parameters
- Request and response formats
- Possible response codes
- Interactive endpoint testing

## Endpoints

### User Registration

**URL:** `/api/v1/auth/register`  
**Method:** `POST`  
**Request body:**

```json
{
  "email": "example@example.com",
  "password": "password123",
  "first_name": "First",
  "last_name": "Last",
  "business_name": "My Business",
  "business_address": "Business Address",
  "phone_number": "123456789",
  "tax_id": "TAX12345"
}
```

The fields `business_name`, `business_address`, `phone_number`, and `tax_id` are optional for initial registration.

### Login

**URL:** `/api/v1/auth/login`  
**Method:** `POST`  
**Request body:**

```json
{
  "email": "example@example.com",
  "password": "password123"
}
```

### User Profile

**URL:** `/api/v1/auth/profile`  
**Method:** `GET`  
**Headers:** `Authorization: Bearer {token}`

## Responses

All responses follow this format:

```json
{
  "message": "Descriptive message",
  "user": {
    "id": 1,
    "email": "example@example.com",
    "first_name": "First",
    "last_name": "Last",
    "role": "user"
  },
  "access_token": "jwt_token"
}
```

In case of error:

```json
{
  "error": "Error description"
}
```

## How to Document New Endpoints

To document new endpoints, use Python docstrings with Swagger format. Example:

```python
@blueprint.route('/endpoint', methods=['POST'])
def my_endpoint():
    """
    Endpoint description
    ---
    tags:
      - Category
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            property:
              type: string
              description: Description
              example: Example value
    responses:
      200:
        description: Success description
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success message
    """
    # Implementation
```

## Procesamiento Automático de Pagos ACH

El sistema ahora incluye un procesador automático de pagos ACH que genera archivos en formato NACHA para ser enviados a la red ACH. Este proceso se ejecuta diariamente a las 11:00 AM.

### Configuración

Para configurar el procesamiento automático de pagos ACH, sigue estos pasos:

1. Instala las dependencias adicionales:

```
pip install celery==5.2.7 redis==4.5.1 nacha==1.1.1
```

2. Configura las siguientes variables de entorno:

```
# Configuración de Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Configuración de NACHA
NACHA_IMMEDIATE_DESTINATION=999999999  # Número de routing del banco receptor
NACHA_IMMEDIATE_ORIGIN=1234567890      # ID de la compañía originadora
NACHA_COMPANY_NAME=LOAN PLATFORM       # Nombre de la compañía
NACHA_COMPANY_ID=1234567890           # ID de la compañía
NACHA_ODFI_ID=99999999                # ID del banco originador
NACHA_OUTPUT_DIR=ach_files            # Directorio para guardar los archivos generados
```

3. Asegúrate de que Redis esté instalado y ejecutándose:

```
# En macOS con Homebrew
brew install redis
brew services start redis

# En Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

### Ejecución

Para iniciar el worker de Celery:

```
cd backend
celery -A celery_worker worker --loglevel=info
```

Para iniciar el scheduler de Celery (beat):

```
cd backend
celery -A celery_worker beat --loglevel=info
```

### Proceso de Pagos

1. Cada día a las 11:00 AM, el sistema automáticamente:

   - Identifica todos los pagos programados para el día
   - Crea un batch ACH en la base de datos
   - Genera un archivo en formato NACHA con todas las transacciones
   - Guarda el archivo en el directorio configurado

2. El archivo generado debe ser enviado manualmente a la red ACH para su procesamiento.

3. Para procesar los archivos de retorno con transacciones fallidas:
   - Coloca el archivo de retorno en un directorio accesible
   - Utiliza el endpoint API: `POST /api/v1/payments/process-failed-payments` con el parámetro `file_path`

### Estructura de los Archivos NACHA

Los archivos generados siguen el formato NACHA estándar con:

- Un encabezado de archivo (File Header Record)
- Un lote de transacciones (Batch Header Record)
- Registros de entrada para cada transacción (Entry Detail Records)
- Un control de lote (Batch Control Record)
- Un control de archivo (File Control Record)

### Notas Importantes

- La información bancaria se extrae automáticamente de los datos de aplicación de préstamo.
- Se busca la información bancaria en diferentes campos del JSON de la aplicación.
- El sistema identifica automáticamente la información necesaria como números de cuenta y routing.
