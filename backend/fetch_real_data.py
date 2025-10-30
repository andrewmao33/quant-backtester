#!/usr/bin/env python3
"""
Fetch real stock data from Alpha Vantage and store in database
"""

from src.data.alpha_vantage_fetcher import AlphaVantageFetcher
from src.database.models import create_tables
from src.database.connection import get_db_connection

def insert_stock_data(data):
    """Insert stock data into the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert data (ignore duplicates due to UNIQUE constraint)
    cursor.executemany('''
        INSERT OR IGNORE INTO stock_data 
        (symbol, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [
        (row['symbol'], row['date'], row['open'], row['high'], 
         row['low'], row['close'], row['volume'])
        for row in data
    ])
    
    conn.commit()
    conn.close()
    print(f"Inserted {len(data)} records into database")

def fetch_and_store_data():
    """Fetch real data for symbols and store in database"""
    
    # Your API key
    API_KEY = 'TMD1NUWLD8WDMQOV'
    
    # Symbols to fetch (using your original symbols)
    symbols = ['AAPL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX', 'AMD']
    
    # Create tables if they don't exist
    create_tables()
    
    # Initialize fetcher
    fetcher = AlphaVantageFetcher(API_KEY)
    
    print(f"Fetching real data for {len(symbols)} symbols...")
    print("Note: Alpha Vantage free tier allows 5 requests per minute")
    print("This will take about 2 minutes to complete...")
    
    # Fetch data for all symbols
    all_data = fetcher.fetch_multiple_symbols(symbols, delay=12.0)  # 12 seconds between requests
    
    # Store data in database
    total_records = 0
    for symbol, data in all_data.items():
        if data:
            print(f"\nStoring {len(data)} records for {symbol}...")
            insert_stock_data(data)
            total_records += len(data)
        else:
            print(f"No data to store for {symbol}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Successfully fetched data for {len(all_data)} symbols")
    print(f"Total records stored: {total_records}")
    
    # Show date ranges for each symbol
    from src.database.models import get_date_range, get_available_symbols
    
    print(f"\n=== DATE RANGES ===")
    symbols_in_db = get_available_symbols()
    for symbol in symbols_in_db:
        start, end = get_date_range(symbol)
        print(f"{symbol}: {start} to {end}")

if __name__ == "__main__":
    fetch_and_store_data()
