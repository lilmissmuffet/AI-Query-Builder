# AI Query Builder — Natural Language to SQL API

An AI-powered backend that converts **natural-language questions into SQL queries** using **Google Gemini**, retrieves database schemas dynamically from **PostgreSQL**, validates generated SQL, and executes approved queries through a **FastAPI REST API**.

The application also includes **JWT-based authentication**, secure password hashing, protected API endpoints, and support for discovering and querying PostgreSQL databases.

---

## Overview

AI Query Builder allows users to interact with relational databases using natural language instead of manually writing SQL.

For example:

> "Show me all employees in the Engineering department."

The application retrieves the relevant database schema, provides it to Gemini, generates an SQL query, validates the generated SQL, and executes the approved query against PostgreSQL.

The backend is protected using JWT authentication, ensuring that database and query operations are only available to authenticated users.

---

## Key Features

### AI & SQL

* Natural Language → SQL generation using Google Gemini
* Dynamic PostgreSQL schema retrieval
* Schema-aware SQL generation
* Database discovery
* SQL validation before execution
* Controlled SQL execution
* Support for querying multiple PostgreSQL databases

### Backend

* FastAPI REST API
* Pydantic request/response validation
* Modular backend architecture
* PostgreSQL integration using `psycopg2`
* Interactive Swagger API documentation

### Authentication & Security

* User registration
* Secure password hashing
* Login authentication
* JWT access-token generation
* JWT token verification
* OAuth2 Bearer authentication
* Protected API endpoints
* Environment-based configuration for secrets



## Request Flow

```text
1. User registers an account
          ↓
2. User logs in
          ↓
3. API returns JWT access token
          ↓
4. User sends Bearer token with protected requests
          ↓
5. API verifies JWT
          ↓
6. Available PostgreSQL databases are discovered
          ↓
7. Database schema is retrieved dynamically
          ↓
8. User submits a natural-language question
          ↓
9. Gemini generates SQL using the schema
          ↓
10. Generated SQL is validated
          ↓
11. Valid SQL is executed against PostgreSQL
          ↓
12. Query results are returned through the API
```

---

## API Endpoints

| Method | Endpoint     | Description                         | Authentication |
| ------ | ------------ | ----------------------------------- | -------------- |
| `POST` | `/register`  | Register a new user                 | No             |
| `POST` | `/login`     | Authenticate user and receive JWT   | No             |
| `GET`  | `/me`        | Retrieve current authenticated user | Required       |
| `GET`  | `/databases` | Discover available databases        | Required       |
| `GET`  | `/schema`    | Retrieve database schema            | Required       |
| `POST` | `/query`     | Generate, validate and execute SQL  | Required       |

---

## Authentication

The API uses **JWT Bearer authentication**.

### Authentication Flow

```text
Register
   ↓
Login
   ↓
JWT Access Token
   ↓
Authorization: Bearer <access_token>
   ↓
Protected API Endpoint
```

After logging in, the returned access token must be included in the `Authorization` header when accessing protected endpoints.

Example:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## Example Natural Language Query

User input:

```text
Show all employees who work in the Engineering department.
```

Gemini generates an SQL query based on the dynamically retrieved schema:

```sql
SELECT *
FROM employees
WHERE department = 'Engineering';
```

The generated SQL is then passed through the SQL validation layer before execution.

---

## SQL Validation

Generated SQL is not executed blindly.

The application validates the generated query before sending it to PostgreSQL.

The validation layer is designed to:

* Inspect generated SQL
* Reject unsupported or unsafe query types
* Prevent unauthorized database operations
* Allow only permitted query operations
* Ensure that only validated SQL reaches the execution layer

This provides an additional safety layer between the LLM and the database.

---

## Project Structure

```text
AI-Query-Builder/
│
├── main.py
├── auth.py
├── database.py
├── sql_validator.py
├── ai.py
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

> The exact filenames should match the files currently present in the repository.

### File Responsibilities

**`main.py`**

Contains the FastAPI application and API endpoints.

**`auth.py`**

Handles:

* Password hashing
* Password verification
* JWT creation
* JWT decoding and verification
* Authentication dependencies

**`database.py`**

Handles:

* PostgreSQL connections
* Database discovery
* Schema retrieval
* Query execution

**`sql_validator.py`**

Handles validation and safety checks for generated SQL queries.

**`ai.py`**

Handles Gemini integration and natural-language-to-SQL generation.

**`.env`**

Stores sensitive configuration such as API keys and database credentials.

---

## Technologies Used

### Programming Language

* Python
* SQL

### Backend

* FastAPI
* Uvicorn
* Pydantic

### AI / LLM

* Google Gemini API
* Google GenAI SDK
* Prompt Engineering
* LLM-based SQL Generation

### Database

* PostgreSQL
* psycopg2

### Authentication

* JWT
* OAuth2 Bearer Authentication
* Password Hashing

### Development Tools

* Git
* GitHub
* VS Code
* PowerShell
* Python Virtual Environment
* python-dotenv

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/lilmissmuffet/AI-Query-Builder.git
```

Navigate into the project:

```bash
cd AI-Query-Builder
```

---

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

Add the required API and database configuration used by the application.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Add your PostgreSQL configuration according to the variables used by your current `database.py`.

**Do not commit `.env` to GitHub.**

Make sure `.env` is included in `.gitignore`.

---

## Running the Application

Start the FastAPI development server with:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## Interactive API Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI can be used to:

* Register users
* Log in
* Obtain JWT tokens
* Authorize requests
* Discover databases
* Retrieve schemas
* Submit natural-language queries
* View generated SQL and query results

---

## Using the API

### Step 1 — Register

Create a user account using:

```text
POST /register
```

---

### Step 2 — Login

Authenticate using:

```text
POST /login
```

The API returns an access token.

---

### Step 3 — Authorize

Use the returned token with the Bearer authentication scheme:

```text
Bearer YOUR_ACCESS_TOKEN
```

---

### Step 4 — Discover Databases

Call:

```text
GET /databases
```

This endpoint returns the databases available to the authenticated user/application.

---

### Step 5 — Retrieve Schema

Call:

```text
GET /schema
```

The backend retrieves the relevant PostgreSQL schema so that Gemini can generate schema-aware SQL.

---

### Step 6 — Submit a Natural Language Query

Call:

```text
POST /query
```

Example:

```json
{
  "question": "Show all employees in the Engineering department."
}
```

The backend:

```text
Natural Language
       ↓
Schema Retrieval
       ↓
Gemini
       ↓
SQL Generation
       ↓
SQL Validation
       ↓
PostgreSQL
       ↓
Results
```

---

## Security Considerations

The project incorporates several security controls:

* Passwords are securely hashed rather than stored as plain text.
* JWT access tokens are used for authenticated API access.
* Protected endpoints require Bearer authentication.
* JWT tokens are verified before protected operations are performed.
* Generated SQL is validated before execution.
* Database credentials and API keys are stored using environment variables.
* Sensitive configuration is excluded from version control through `.gitignore`.

---

## Development Phases

### Phase 1 — Core Backend — Complete

* [x] FastAPI setup
* [x] PostgreSQL connection
* [x] Database discovery
* [x] Dynamic schema retrieval
* [x] Gemini SQL generation
* [x] SQL validation
* [x] SQL execution

### Phase 2 — Authentication — Complete

* [x] User registration
* [x] Secure password hashing
* [x] Login
* [x] JWT access tokens
* [x] JWT verification
* [x] `/me`
* [x] Protected `/databases`
* [x] Protected `/schema`
* [x] Protected `/query`

### Phase 3 — Planned

* [ ] Automated unit and integration testing
* [ ] Query history
* [ ] Improved error handling
* [ ] Structured logging
* [ ] Rate limiting
* [ ] Dockerization
* [ ] Deployment
* [ ] Frontend interface
* [ ] Improved query safety and permissions

---

## Project Goals

The project was developed to explore how **Large Language Models can be integrated with backend systems and relational databases** while maintaining control over database access and query execution.

The main goals are:

1. Convert natural language into SQL using an LLM.
2. Provide the LLM with real database schema information.
3. Validate generated SQL before execution.
4. Expose the functionality through a REST API.
5. Protect database operations using authentication.
6. Build the system using modular backend components.

---

## Future Improvements

Potential future improvements include:

* Query history and saved queries
* User-specific database permissions
* More advanced SQL validation
* Query result pagination
* API rate limiting
* Automated testing
* Logging and monitoring
* Docker-based deployment
* Cloud deployment
* Frontend dashboard
* Improved prompt and SQL-generation strategies
* Support for additional database systems

---

## Learning Outcomes

Through this project, I gained hands-on experience with:

* Building REST APIs using FastAPI
* Integrating LLMs into backend applications
* Natural-language-to-SQL generation
* PostgreSQL database interaction
* Dynamic database schema inspection
* SQL validation and controlled execution
* JWT authentication
* Password hashing
* OAuth2 Bearer authentication
* API dependency management
* Environment-based secret management
* Modular Python backend architecture

---

## Project Status

**Current Status: Phase 2 Complete**

The project currently provides an authenticated FastAPI backend capable of connecting to PostgreSQL, discovering databases and schemas, generating SQL using Google Gemini, validating generated SQL, and executing approved queries.

Development will continue with testing, improved security controls, deployment, and additional application features.

---

## Author

**Swastika Shome**

GitHub:
https://github.com/lilmissmuffet


 The project is being developed as a practical AI Engineering portfolio project, with the goal of demonstrating how an LLM can be integrated with a real relational database to build a useful and controlled AI application.
