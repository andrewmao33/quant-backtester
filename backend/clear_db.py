#!/usr/bin/env python3
"""
Clear all data from the database
"""

from src.database.connection import get_db_connection

def clear_database():
    """Clear all data from the stock_data table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count records before clearing
    cursor.execute("SELECT COUNT(*) FROM stock_data")
    count_before = cursor.fetchone()[0]
    
    # Clear all data
    cursor.execute("DELETE FROM stock_data")
    
    # Reset auto-increment counter
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='stock_data'")
    
    conn.commit()
    
    # Count records after clearing
    cursor.execute("SELECT COUNT(*) FROM stock_data")
    count_after = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Database cleared!")
    print(f"Records before: {count_before}")
    print(f"Records after: {count_after}")

if __name__ == "__main__":
    clear_database()
