import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Optional

class AlphaVantageFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
    def fetch_stock_data(self, symbol: str) -> Optional[List[Dict]]:
        """
        Fetch daily stock data for a symbol from Alpha Vantage.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
            
        Returns:
            List of dictionaries with OHLCV data, or None if error
        """
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'full',  # Get maximum historical data
            'apikey': self.api_key
        }
        
        try:
            print(f"Fetching data for {symbol}...")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                print(f"Error for {symbol}: {data['Error Message']}")
                return None
                
            if 'Note' in data:
                print(f"API limit reached: {data['Note']}")
                return None
                
            if 'Information' in data:
                print(f"API info: {data['Information']}")
                return None
            
            # Extract time series data
            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                print(f"No time series data found for {symbol}")
                return None
            
            # Convert to our format
            stock_data = []
            for date_str, values in time_series.items():
                try:
                    # Parse date
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    stock_data.append({
                        'symbol': symbol,
                        'date': date_str,
                        'open': float(values['1. open']),
                        'high': float(values['2. high']),
                        'low': float(values['3. low']),
                        'close': float(values['4. close']),
                        'volume': int(values['5. volume'])
                    })
                except (ValueError, KeyError) as e:
                    print(f"Error parsing data for {symbol} on {date_str}: {e}")
                    continue
            
            # Sort by date (oldest first)
            stock_data.sort(key=lambda x: x['date'])
            
            print(f"Successfully fetched {len(stock_data)} records for {symbol}")
            return stock_data
            
        except requests.exceptions.RequestException as e:
            print(f"Request error for {symbol}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error for {symbol}: {e}")
            return None
    
    def fetch_multiple_symbols(self, symbols: List[str], delay: float = 12.0) -> Dict[str, List[Dict]]:
        """
        Fetch data for multiple symbols with delay between requests.
        
        Args:
            symbols: List of stock symbols
            delay: Delay between requests in seconds (Alpha Vantage free tier: 5 requests/minute)
            
        Returns:
            Dictionary mapping symbol to data list
        """
        results = {}
        
        for i, symbol in enumerate(symbols):
            print(f"\nFetching {symbol} ({i+1}/{len(symbols)})...")
            
            data = self.fetch_stock_data(symbol)
            if data:
                results[symbol] = data
            else:
                print(f"Failed to fetch data for {symbol}")
            
            # Add delay between requests (except for last one)
            if i < len(symbols) - 1:
                print(f"Waiting {delay} seconds before next request...")
                time.sleep(delay)
        
        return results
