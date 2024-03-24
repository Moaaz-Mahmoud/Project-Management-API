# Project Management API

---

## Overview

This project is a REST API designed to handle task management 
within an organization. It provides endpoints for user registration, authentication 
(login/logout), and various operations related to task management. 

**Key Features:**
- User management: Registration, login, logout, retrieval (all and single), 
updating, and deletion.
- Task management: Creation, retrieval, update, and deletion.
- Assignment management: Assigning and unassigning users to tasks.
- Admin privileges: Listing all users' data.

**Technologies Used:**
- Flask
- Flask-Smorest
- Flask-JWT-Extended
- Flask-SQLAlchemy
- PostgreSQL
- Marshmallow

---

## Getting Started

### Prerequisites

Make sure you have the following software installed on your machine:

- Python (version 3.10.12)
- pip

### Installation

1. Clone the repository to your local machine:

```bash
git clone https://github.com/Moaaz-Mahmoud/Project-Management-API
```

2. Navigate to the project directory:

```bash
cd Project-Management-API
```

3. Install the required Python dependencies using pip:

```bash
pip install -r requirements.txt
```

### Database Setup

1. Ensure you have a PostgreSQL database server running. You can install PostgreSQL from [here](https://www.postgresql.org/download/) if you haven't already.

2. Create a new PostgreSQL database and keep the database URL.

3. To set up your environment variables, create a .env file in the project directory based on the [.env.example](.env.example) file included in the repository.

```plaintext
DATABASE_URL=<your_database_url>
JWT_SECRET_KEY=<your_jwt_secret_key>
```

### Database Initialization

Create and seed the database:

```bash
flask db_create
flask db_seed
```

### Running the Application

Once the database is set up and initialized, you can start the Flask application:

```bash
flask run
```

The application should now be running locally at `http://127.0.0.1:5000/`.

## API Documentation

You can access the Swagger UI documentation for the API at http://127.0.0.1:5000/swagger-ui/. This documentation provides information about the available endpoints and how to interact with them.

### Testing

To run the automated tests for the application, use the following command:

```bash
python3 -m unittest discover  # Linux
```
```bash
python -m unittest discover  # Windows
```

---

## Play with the API

A few requests to experiment with the API. Watch out for the placeholders!

1. **Register a User**:

```bash
curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d '{
    "name": "Meowing Cat",
    "username": "meowing_cat",
    "email": "cat@meows.com",
    "password": "123",
    "status": "ACTIVE"
}'
```

2. **Log In to Obtain Access Token**:

```bash
curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{
    "username_or_email": "meowing_cat",
    "password": "123"
}'
```

3. **Create a Task**:

```bash
curl -X POST http://localhost:5000/users/<user_id>/tasks -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" -d '{
    "name": "Destroy the earphones",
    "description": "Destroy the earphones for no reason.",
    "due_date": "2024-01-31 07:00:00",
    "status": "active"
}'
```

4. **Assign the Task to the New User**:

```bash
curl -X POST "http://localhost:5000/assign?user_id=<user_id>&task_id=<task_id>" -H "Authorization: Bearer <access_token>"
```

5. **Retrieve a List of Your Tasks**:

```bash
curl -X GET http://localhost:5000/users/<user_id>/tasks -H "Authorization: Bearer <access_token>"
```

6. **Unassign the Task**:

```bash
curl -X DELETE "http://localhost:5000/assign?user_id=<user_id>&task_id=<task_id>" -H "Authorization: Bearer <access_token>"
```

7. **Retrieve a List of Your Tasks Again**:

```bash
curl -X GET http://localhost:5000/users/<user_id>/tasks -H "Authorization: Bearer <access_token>"
```

8. **Delete the Task**:

```bash
curl -X DELETE http://localhost:5000/tasks/<task_id> -H "Authorization: Bearer <access_token>"
```

9. **Log Out**:

```bash
curl -X POST http://localhost:5000/logout -H "Authorization: Bearer <access_token>"
```

10. **Attempt to Retrieve a List of Your Tasks Again**:

```bash
curl -X GET http://localhost:5000/users/<user_id>/tasks -H "Authorization: Bearer <access_token>"
```
