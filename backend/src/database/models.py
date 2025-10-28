from .connection import get_db_connection

def create_tables():
    """
    Create the stock_data table if it doesn't exist.
    This is the main table that stores all stock price data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create the stock_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date DATE NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            UNIQUE(symbol, date)
        )
    ''')
    
    # Create indexes for better query performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_symbol_date 
        ON stock_data(symbol, date)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_date 
        ON stock_data(date)
    ''')
    
    conn.commit()
    conn.close()
    print("Database tables created successfully!")

def get_available_symbols():
    """
    Get all unique symbols in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT symbol FROM stock_data ORDER BY symbol')
    symbols = [row['symbol'] for row in cursor.fetchall()]
    
    conn.close()
    return symbols

def get_date_range(symbol):
    """
    Get the available date range for a specific symbol.
    Returns (start_date, end_date) or (None, None) if no data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT MIN(date) as start_date, MAX(date) as end_date 
        FROM stock_data 
        WHERE symbol = ?
    ''', (symbol,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result['start_date']:
        return result['start_date'], result['end_date']
    else:
        return None, None

def get_stock_data(symbol, start_date=None, end_date=None):
    """
    Get stock data for a symbol within a date range.
    If no dates provided, returns all data for the symbol.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if start_date and end_date:
        cursor.execute('''
            SELECT * FROM stock_data 
            WHERE symbol = ? AND date BETWEEN ? AND ?
            ORDER BY date
        ''', (symbol, start_date, end_date))
    else:
        cursor.execute('''
            SELECT * FROM stock_data 
            WHERE symbol = ?
            ORDER BY date
        ''', (symbol,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries for easier use
    return [dict(row) for row in rows]

# Example usage:
if __name__ == "__main__":
    # Create tables
    create_tables()
    
    # Test functions
    symbols = get_available_symbols()
    print(f"Available symbols: {symbols}")
    
    if symbols:
        symbol = symbols[0]
        start, end = get_date_range(symbol)
        print(f"Date range for {symbol}: {start} to {end}")
