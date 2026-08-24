import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_sql(database_name: str, schema: dict, question: str) -> str:

    schema_text = ""

    for table_name, columns in schema.items():
        schema_text += f"\nTable: {table_name}\n"

        for column in columns:
            schema_text += (
                f" - {column['column']}: {column['type']}\n"
            )

    contents = f"""
You are an SQL query generator.

The user has selected the PostgreSQL database:

{database_name}

Here is the schema of that database:

{schema_text}

The user's question is:

{question}

Generate a PostgreSQL SQL query that answers the user's question.

Rules:

1. Generate ONLY SQL.
2. Generate ONLY SELECT queries.
3. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER,
   CREATE, TRUNCATE, GRANT, REVOKE, or any other
   data-modifying query.
4. Use ONLY the tables and columns provided in the schema.
5. Do not invent tables or columns.
6. Return only the SQL query without Markdown formatting.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents
    )

    sql = response.text.strip()

    # Remove Markdown code fences if Gemini returns them
    if sql.startswith("```sql"):
        sql = sql[6:]
    elif sql.startswith("```"):
        sql = sql[3:]

    if sql.endswith("```"):
        sql = sql[:-3]

    return sql.strip()