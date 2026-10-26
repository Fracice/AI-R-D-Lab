
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "sales.db"

# SQLite actions that a generated query must never perform.
DENIED_ACTIONS = {
    sqlite3.SQLITE_INSERT,
    sqlite3.SQLITE_UPDATE,
    sqlite3.SQLITE_DELETE,
    sqlite3.SQLITE_ALTER_TABLE,
    sqlite3.SQLITE_DROP_TABLE,
    sqlite3.SQLITE_DROP_INDEX,
    sqlite3.SQLITE_DROP_VIEW,
    sqlite3.SQLITE_DROP_TRIGGER,
    sqlite3.SQLITE_CREATE_TABLE,
    sqlite3.SQLITE_CREATE_INDEX,
    sqlite3.SQLITE_CREATE_VIEW,
    sqlite3.SQLITE_CREATE_TRIGGER,
    sqlite3.SQLITE_ATTACH,
    sqlite3.SQLITE_DETACH,
    sqlite3.SQLITE_PRAGMA,
}


def get_connection():
    """Open a connection to the local SQLite database."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Run setup_db.py first."
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_schema():
    """Return the database schema for the LLM."""
    with get_connection() as conn:
        tables = conn.execute("""
            SELECT name, sql
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()

    return "\n\n".join(
        f"Table: {row['name']}\n{row['sql']}" for row in tables
    )


def _read_only_authorizer(action, arg1, arg2, database, trigger):
    """Allow reads and SELECT operations; deny changes to database state."""
    if action in DENIED_ACTIONS:
        return sqlite3.SQLITE_DENY

    # Block write-oriented PRAGMA and unknown actions by default.
    if action == sqlite3.SQLITE_FUNCTION:
        function_name = (arg2 or arg1 or "").lower()
        if function_name in {"writefile", "readfile"}:
            return sqlite3.SQLITE_DENY

    return sqlite3.SQLITE_OK


def execute_query(sql):
    """Execute one read-only query, with SQLite-level authorization."""
    statement = sql.strip()

    if not statement:
        raise ValueError("SQL query cannot be empty.")

    # Only allow a SELECT or a CTE that begins with WITH.
    first_word = statement.split(None, 1)[0].upper()
    if first_word not in {"SELECT", "WITH"}:
        raise ValueError("Only SELECT queries are allowed.")

    # Reject multiple SQL statements.
    if ";" in statement.rstrip(";"):
        raise ValueError("Only one SQL statement is allowed.")

    uri = DB_PATH.resolve().as_uri() + "?mode=ro"

    with sqlite3.connect(uri, uri=True) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")
        conn.set_authorizer(_read_only_authorizer)

        cursor = conn.execute(statement)
        return [dict(row) for row in cursor.fetchall()]
