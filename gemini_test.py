import os

import psycopg2
from dotenv import load_dotenv
from google import genai


# ============================================================
# 1. Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# 2. Initialize Gemini
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================================
# 3. Database connection settings
# ============================================================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ============================================================
# 4. Fetch existing databases from PostgreSQL
# ============================================================

server_conn = None
server_cursor = None

try:

    server_conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database="postgres",
        user=DB_USER,
        password=DB_PASSWORD
    )

    server_cursor = server_conn.cursor()

    server_cursor.execute("""
        SELECT datname
        FROM pg_database
        WHERE datistemplate = false
        AND datname <> 'postgres'
        ORDER BY datname;
    """)

    databases = [row[0] for row in server_cursor.fetchall()]


except Exception as e:

    print(f"\nCould not fetch databases: {e}")
    exit()


finally:

    if server_cursor:
        server_cursor.close()

    if server_conn:
        server_conn.close()


# ============================================================
# 5. Check whether databases were found
# ============================================================

if not databases:

    print("\nNo databases found.")
    exit()


# ============================================================
# 6. Display databases and ask user to choose
# ============================================================

print("\nAvailable databases:")

for index, database in enumerate(databases, start=1):
    print(f"{index}. {database}")


choice = input("\nChoose a database: ").strip()


# ============================================================
# 7. Validate user's selection
# ============================================================

if not choice.isdigit():

    print("\nInvalid selection.")
    exit()


choice = int(choice)


if choice < 1 or choice > len(databases):

    print("\nInvalid database selection.")
    exit()


selected_database = databases[choice - 1]

print(f"\nSelected database: {selected_database}")


# ============================================================
# 8. Connect to the selected database
# ============================================================

conn = None
cursor = None

try:

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=selected_database,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = conn.cursor()

    print("Database connection successful!")


    # ========================================================
    # 9. Fetch schema from selected database
    # ========================================================

    cursor.execute("""
        SELECT
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """)

    schema_rows = cursor.fetchall()


    if not schema_rows:

        print("\nNo tables found in this database.")
        exit()


    # ========================================================
    # 10. Convert schema into text for Gemini
    # ========================================================

    schema = ""

    current_table = None

    for table_name, column_name, data_type in schema_rows:

        if table_name != current_table:

            schema += f"\nTable: {table_name}\n"

            current_table = table_name

        schema += f"  - {column_name}: {data_type}\n"


    print("\nDatabase schema loaded.")


    # ========================================================
    # 11. Ask the user for a question
    # ========================================================

    question = input(
        "\nAsk your database question: "
    ).strip()


    # ========================================================
    # 12. Send schema + question to Gemini
    # ========================================================

    contents = f"""
You are an SQL query generator.

The user has selected the PostgreSQL database:

{selected_database}

Here is the schema of that database:

{schema}

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


    # ========================================================
    # 13. Extract SQL generated by Gemini
    # ========================================================

    sql = response.text.strip()


    # Remove Markdown code fences if Gemini returns them

    if sql.startswith("```sql"):

        sql = sql[6:]


    elif sql.startswith("```"):

        sql = sql[3:]


    if sql.endswith("```"):

        sql = sql[:-3]


    sql = sql.strip()


    print("\nGenerated SQL:")
    print(sql)


    # ========================================================
    # 14. Safety check
    # ========================================================

    if not sql.lower().startswith("select"):

        print("\nError: Only SELECT queries are allowed.")
        exit()


    # ========================================================
    # 15. Execute SQL on the selected database
    # ========================================================

    cursor.execute(sql)

    results = cursor.fetchall()


    # ========================================================
    # 16. Display results
    # ========================================================

    print("\nResult:")

    if results:

        for row in results:
            print(row)

    else:

        print("No results found.")


except Exception as e:

    print(f"\nError: {e}")


finally:

    if cursor:
        cursor.close()

    if conn:
        conn.close()

    print("\nDatabase connection closed.")