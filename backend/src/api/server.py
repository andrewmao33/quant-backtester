from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, date
from pathlib import Path
import json
import os
from dotenv import load_dotenv

from src.database.models import get_available_symbols, get_date_range, get_stock_data
from src.database.connection import get_db_connection
from src.data.alpha_vantage_fetcher import AlphaVantageFetcher
from src.strategies.ma_crossover import MA_Crossover
from src.strategies.bollinger_breakout import BollingerBreakout
from src.backtesting.engine import BacktestingEngine

app = FastAPI()

# Load environment variables from backend/.env if present
load_dotenv()

# Add CORS middleware
frontend_origin = os.getenv("FRONTEND_ORIGIN")
allowed_origins = ["http://localhost:3000"]
if frontend_origin:
    allowed_origins.append(frontend_origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # React dev server + optional deployed frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BacktestRequest(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    strategy: str
    initial_cash: float
    strategy_params: dict = {}


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/symbols")
def get_symbols():
    '''
    Returns list of all available tickers for selection.
    Prefers curated list from data/symbols.json; falls back to DB symbols.
    '''
    try:
        # backend/src/api/server.py -> backend/data/symbols.json
        backend_dir = Path(__file__).parent.parent.parent
        symbols_path = backend_dir / "data" / "symbols.json"
        if symbols_path.exists():
            with symbols_path.open("r") as f:
                symbols = json.load(f)
                # Ensure list of strings and uppercase
                symbols = [str(s).upper() for s in symbols if isinstance(s, str)]
                return {"symbols": symbols}
    except Exception:
        # On any issue reading JSON, fall back to DB
        pass

    symbols = get_available_symbols()
    return {"symbols": symbols}

def _insert_ohlcv_rows(rows):
    if not rows:
        return 0
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')
        cursor.executemany(
            '''
            INSERT OR IGNORE INTO stock_data (symbol, date, open, high, low, close, volume)
            VALUES (:symbol, :date, :open, :high, :low, :close, :volume)
            ''',
            rows,
        )
        conn.commit()
        return cursor.rowcount or 0
    finally:
        conn.close()

def _fetch_alpha_and_upsert(symbol: str, since_date: str | None = None) -> int:
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail='ALPHA_VANTAGE_API_KEY not set')
    fetcher = AlphaVantageFetcher(api_key)
    data = fetcher.fetch_stock_data(symbol)
    if not data:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data for symbol '{symbol}' from Alpha Vantage")
    if since_date:
        data = [r for r in data if r['date'] >= since_date]
    return _insert_ohlcv_rows(data)

@app.get("/strategies")
def get_strategies():
    '''
    returns list of all available strategies
    '''
    return {"strategies": ["Moving Average Crossover", "Bollinger Breakout"]}

@app.get("/symbols/{symbol}/dates")
def get_symbol_dates(symbol: str):
    '''
    returns available date range for a specific symbol
    '''
    available_symbols = get_available_symbols()
    if symbol not in available_symbols:
        raise HTTPException(
            status_code=404, 
            detail=f"Symbol '{symbol}' not found. Available symbols: {available_symbols}"
        )
    
    start_date, end_date = get_date_range(symbol)
    return {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date
    }

@app.post("/backtest")
def run_backtest(request: BacktestRequest):
    try:
        print(f"Backtest request: {request}")
        symbol = request.symbol.upper()

        # Ensure data exists; if symbol missing, fetch all history first
        available_symbols = get_available_symbols()
        if symbol not in available_symbols:
            inserted = _fetch_alpha_and_upsert(symbol)
            print(f"Fetched full history for {symbol} via Alpha Vantage: {inserted} rows")
            available_symbols = get_available_symbols()
            if symbol not in available_symbols:
                raise HTTPException(status_code=400, detail=f"Symbol '{symbol}' still not available after fetch")

        # Current available range after ensuring presence
        start_available, end_available = get_date_range(symbol)
        
        # Validate requested dates
        try:
            start_requested = datetime.strptime(request.start_date, '%Y-%m-%d').date()
            end_requested = datetime.strptime(request.end_date, '%Y-%m-%d').date()
            start_available_dt = datetime.strptime(start_available, '%Y-%m-%d').date()
            end_available_dt = datetime.strptime(end_available, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # If missing recent dates, fetch only newer data and upsert
        if end_requested > end_available_dt:
            since_date = (end_available_dt.strftime('%Y-%m-%d'))
            inserted = _fetch_alpha_and_upsert(symbol, since_date=since_date)
            print(f"Incremental fetch for {symbol} since {since_date}: {inserted} rows")
            start_available, end_available = get_date_range(symbol)
            start_available_dt = datetime.strptime(start_available, '%Y-%m-%d').date()
            end_available_dt = datetime.strptime(end_available, '%Y-%m-%d').date()

        # Final guards after fetch attempts
        if start_requested < start_available_dt:
            raise HTTPException(status_code=400, detail=f"Start date {request.start_date} is before available data. Earliest available: {start_available}")
        # If requested end date is beyond latest available (e.g., today's data not yet posted),
        # clamp to latest available instead of erroring
        if end_requested > end_available_dt:
            end_requested = end_available_dt
        
        # Use possibly clamped dates for downstream steps
        start_str = start_requested.strftime('%Y-%m-%d')
        end_str = end_requested.strftime('%Y-%m-%d')
        
        # Get data from database
        data_list = get_stock_data(symbol, start_str, end_str)
        
        if not data_list:
            raise HTTPException(
                status_code=400, 
                detail=f"No data found for {request.symbol} in the specified date range"
            )
        
        # Convert to DataFrame
        data = pd.DataFrame(data_list)
        data['date'] = pd.to_datetime(data['date'])
        data = data.set_index('date').sort_index()
        
        print(f"Retrieved {len(data)} records for {symbol} from {start_str} to {end_str}")
        
        # Initialize strategy based on request
        if request.strategy == "Moving Average Crossover":
            # Extract strategy parameters with defaults
            fast_period = request.strategy_params.get('fast_period', 10)
            slow_period = request.strategy_params.get('slow_period', 30)
            initial_cash = request.initial_cash or 100000
            
            strategy = MA_Crossover(fast_period=fast_period, slow_period=slow_period, initial_cash=initial_cash)
        elif request.strategy == "Bollinger Breakout":
            period = request.strategy_params.get('period', 20)
            std = request.strategy_params.get('std', 2)
            initial_cash = request.initial_cash or 100000
            
            strategy = BollingerBreakout(period=period, std=std, initial_cash=initial_cash)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown strategy: {request.strategy}. Available strategies: ['Moving Average Crossover', 'Bollinger Breakout']"
            )
        
        # Run backtest
        engine = BacktestingEngine(strategy)
        results = engine.run(data)
    
        return results
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)