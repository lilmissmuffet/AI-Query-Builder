import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


POSTGRES_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432"),
}


def get_db_connection(database_name="ai_query_builder"):
    return psycopg2.connect(
        **POSTGRES_CONFIG,
        database=database_name
    )


def get_databases():
    conn = get_db_connection("postgres")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT datname
        FROM pg_database
        WHERE datistemplate = false;
    """)

    databases = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return databases


def get_schema(database_name):
    conn = get_db_connection(database_name)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    schema = {}

    for table_name, column_name, data_type in rows:
        if table_name not in schema:
            schema[table_name] = []

        schema[table_name].append({
            "column": column_name,
            "type": data_type
        })

    return schema


def execute_query(database_name, sql):
    conn = get_db_connection(database_name)
    cursor = conn.cursor()

    cursor.execute(sql)

    results = cursor.fetchall()

    column_names = [
        description[0]
        for description in cursor.description
    ]

    cursor.close()
    conn.close()

    return {
        "columns": column_names,
        "rows": results
    }