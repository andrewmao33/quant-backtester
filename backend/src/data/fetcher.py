import yfinance as yf
import os
import pandas as pd

def fetch_stock_data(symbol: str, period: str = "1y"):
    try:
        # Try cache first
        cached_data = fetch_from_cache(symbol, period)
        if cached_data is not None:
            print(f"Using cached data for {symbol}")
            # Convert dates to strings for JSON serialization
            cached_data['Date'] = cached_data.index.strftime('%Y-%m-%d')
            return cached_data.to_dict(orient="records")
        
        # Fetch from yfinance
        print(f"Fetching fresh data for {symbol} from yfinance...")
        data = fetch_from_yfinance(symbol, period)
        
        # Save to cache if we got data
        if not data.empty:
            cache_file = f"cache/{symbol}_{period}.parquet"
            data.to_parquet(cache_file)
            print(f"Saved data to cache: {cache_file}")
            
            # Convert dates to strings for JSON serialization
            data['Date'] = data.index.strftime('%Y-%m-%d')
            return data.to_dict(orient="records")
        
        return data.to_dict(orient="records")
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def fetch_from_cache(symbol: str, period: str):
    # Create cache directory if it doesn't exist
    os.makedirs("cache", exist_ok=True)
    
    cache_file = f"cache/{symbol}_{period}.parquet"
    if os.path.exists(cache_file):
        return pd.read_parquet(cache_file)
    else:
        return None

def fetch_from_yfinance(symbol: str, period: str):
    ticket = yf.Ticker(symbol)
    data = ticket.history(period=period)
    return data