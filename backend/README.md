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
