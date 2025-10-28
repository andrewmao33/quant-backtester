import sqlite3
import os
from pathlib import Path

def get_db_path():
    """
    Get the path to the SQLite database file.
    Creates the data directory if it doesn't exist.
    """
    # Get the backend directory (parent of src)
    backend_dir = Path(__file__).parent.parent.parent
    data_dir = backend_dir / "data"
    
    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)
    
    # Return path to database file
    return data_dir / "backtester.db"

def get_db_connection():
    """
    Create and return a connection to the SQLite database.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def close_db_connection(conn):
    """
    Close the database connection.
    """
    if conn:
        conn.close()

# Example usage:
if __name__ == "__main__":
    # Test the connection
    conn = get_db_connection()
    print(f"Database created at: {get_db_path()}")
    print("Connection successful!")
    close_db_connection(conn)
