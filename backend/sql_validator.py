import re


FORBIDDEN_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "grant",
    "revoke",
    "comment",
    "merge",
}


def validate_sql(sql: str) -> bool:

    # Reject empty SQL
    if not sql or not sql.strip():
        return False

    # Remove leading/trailing whitespace
    sql = sql.strip()

    # Remove one trailing semicolon
    if sql.endswith(";"):
        sql = sql[:-1].strip()

    # Only one SQL statement is allowed
    if ";" in sql:
        return False

    # Query must begin with SELECT or WITH
    if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE):
        return False

    # Extract SQL words
    words = re.findall(
        r"\b[a-zA-Z]+\b",
        sql.lower()
    )

    # Check for forbidden operations
    for word in words:
        if word in FORBIDDEN_KEYWORDS:
            return False

    return True