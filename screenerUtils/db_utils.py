import sqlite3
from pathlib import Path

def backup_database(db_path: str):
    """
    Backup an SQLite database if it exists
    
    Args:
        db_path: Path to the SQLite database file
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    db_file = Path(db_path)
    
    if db_file.exists():
        # In the parent directory create a new name backup.db
        backup_path = db_file.parent / "backup.db"
        # rename the file to backup.db
        db_file.rename(backup_path)
    
def create_connection(db_path: str) -> sqlite3.Connection:
    """Create a connection to the SQLite database. If the database file does not exist, it will be created.
    
    Args:
        db_path: Path to the SQLite database file
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(db_path)
    return conn

def close_connection(conn: sqlite3.Connection) -> None:
    """
    Close the database connection.
    
    Args:
        conn: Database connection object
    """
    if conn:
        conn.close()

def execute_query(conn: sqlite3.Connection, query: str, params: tuple = ()) -> list:
    """
    Execute a SELECT query and return results.
    
    Args:
        conn: Database connection object
        query: SQL query string
        params: Query parameters
    
    Returns:
        list: Query results
    """
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor.fetchall()

def execute_update(conn: sqlite3.Connection, query: str, params: tuple = ()) -> None:
    """
    Execute an INSERT, UPDATE, or DELETE query.
    
    Args:
        conn: Database connection object
        query: SQL query string
        params: Query parameters
    """
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

def create_table(conn: sqlite3.Connection, table_name: str) -> None:
    """
    Create the  table if it doesn't exist.
    
    Args:
        conn: Database connection object
        table_name: Name of the table
    """
    query = f"DROP TABLE IF EXISTS {table_name}"
    execute_update(conn, query)

    query = """
    CREATE TABLE IF NOT EXISTS Company (
        CIK TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        ticker TEXT NOT NULL UNIQUE
    )
    """
    execute_update(conn, query)

def drop_table_if_exists(conn: sqlite3.Connection, table_name: str) -> None:
    """
    Drop a table if it exists in the database.
    
    Args:
        conn: Database connection object
        table_name: Name of the table to drop
    """
    query = f"DROP TABLE IF EXISTS {table_name}"
    execute_update(conn, query)

def create_table_if_not_exists(conn: sqlite3.Connection, table_name: str, schema: str) -> None:
    """
    Create a table if it doesn't exist, otherwise drop and recreate it.
    
    Args:
        conn: Database connection object
        table_name: Name of the table
        schema: SQL schema definition for the table
    """
    drop_table_if_exists(conn, table_name)
    execute_update(conn, schema)


