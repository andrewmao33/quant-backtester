#!/usr/bin/env python3
"""
Quick script to check what's in the database
"""

from src.database.models import get_available_symbols, get_date_range, get_stock_data

def check_database():
    print("=== DATABASE OVERVIEW ===")
    
    # Get all symbols
    symbols = get_available_symbols()
    print(f"Available symbols: {symbols}")
    print(f"Total symbols: {len(symbols)}")
    
    print("\n=== SYMBOL DETAILS ===")
    for symbol in symbols:
        start_date, end_date = get_date_range(symbol)
        data = get_stock_data(symbol)
        
        print(f"\n{symbol}:")
        print(f"  Date range: {start_date} to {end_date}")
        print(f"  Total records: {len(data)}")
        
        if data:
            print(f"  First record: {data[0]}")
            print(f"  Last record: {data[-1]}")
            
            # Show price range
            prices = [row['close'] for row in data]
            print(f"  Price range: ${min(prices):.2f} - ${max(prices):.2f}")
    
    print("\n=== SAMPLE DATA ===")
    if symbols:
        symbol = symbols[0]
        sample_data = get_stock_data(symbol)[:5]  # First 5 records
        print(f"\nFirst 5 records for {symbol}:")
        for record in sample_data:
            print(f"  {record['date']}: O={record['open']:.2f} H={record['high']:.2f} L={record['low']:.2f} C={record['close']:.2f} V={record['volume']:,}")

if __name__ == "__main__":
    check_database()
