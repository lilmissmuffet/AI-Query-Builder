from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import psycopg2

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

from database import (
    get_db_connection,
    get_databases,
    get_schema,
    execute_query,
)

from ai_service import generate_sql
from sql_validator import validate_sql



# FastAPI Application


app = FastAPI(
    title="AI Query Builder API",
    description="Natural language to SQL API powered by Gemini and PostgreSQL",
    version="1.0.0"
)



# Authentication


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)):

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, username, email
            FROM users
            WHERE id = %s;
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return {
            "id": user[0],
            "username": user[1],
            "email": user[2]
        }

    finally:
        cursor.close()
        conn.close()



# Request Models


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class QueryRequest(BaseModel):
    database: str
    question: str



# Basic Routes


@app.get("/")
def root():
    return {
        "message": "AI Query Builder API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }



# Authentication Routes


@app.post("/register", status_code=201)
def register_user(user: RegisterRequest):

    password_hash = hash_password(user.password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, username, email, created_at;
            """,
            (
                user.username,
                user.email,
                password_hash
            )
        )

        new_user = cursor.fetchone()

        conn.commit()

        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user[0],
                "username": new_user[1],
                "email": new_user[2],
                "created_at": new_user[3]
            }
        }

    except psycopg2.IntegrityError:
        conn.rollback()

        raise HTTPException(
            status_code=409,
            detail="Username or email already exists."
        )

    except psycopg2.Error:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to register user."
        )

    finally:
        cursor.close()
        conn.close()


@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, username, email, password_hash
            FROM users
            WHERE username = %s;
            """,
            (form_data.username,)
        )

        db_user = cursor.fetchone()

        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        user_id, username, email, password_hash = db_user

        if not verify_password(
            form_data.password,
            password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        access_token = create_access_token(
            data={
                "sub": str(user_id),
                "username": username
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    finally:
        cursor.close()
        conn.close()


@app.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user)
):
    return current_user



# Database Routes


@app.get("/databases")
def list_databases(
    current_user: dict = Depends(get_current_user)
):

    try:
        databases = get_databases()

        return {
            "databases": databases
        }

    except psycopg2.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to PostgreSQL."
        )


@app.get("/databases/{database_name}/schema")
def database_schema(
    database_name: str,
    current_user: dict = Depends(get_current_user)
):

    try:
        databases = get_databases()

        if database_name not in databases:
            raise HTTPException(
                status_code=404,
                detail=f"Database '{database_name}' not found."
            )

        schema = get_schema(database_name)

        return {
            "database": database_name,
            "schema": schema
        }

    except psycopg2.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to PostgreSQL."
        )



# AI Query Route


@app.post("/query")
def run_query(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):

    # 1. Check whether the database exists
    try:
        databases = get_databases()

        if request.database not in databases:
            raise HTTPException(
                status_code=404,
                detail=f"Database '{request.database}' not found."
            )

    except psycopg2.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to PostgreSQL."
        )

    # 2. Retrieve database schema
    try:
        schema = get_schema(request.database)

    except psycopg2.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve database schema."
        )

    # 3. Generate SQL using Gemini
    try:
        sql = generate_sql(
            request.database,
            schema,
            request.question
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Failed to generate SQL using Gemini."
        )

    # 4. Validate generated SQL
    if not validate_sql(sql):
        raise HTTPException(
            status_code=400,
            detail="Generated SQL failed security validation."
        )

    # 5. Execute SQL
    try:
        result = execute_query(
            request.database,
            sql
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=400,
            detail="The generated SQL could not be executed."
        )

    # 6. Return results
    return {
        "database": request.database,
        "question": request.question,
        "sql": sql,
        "columns": result["columns"],
        "rows": result["rows"]
    }