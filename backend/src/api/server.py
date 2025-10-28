from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

from src.database.models import get_available_symbols, get_date_range, get_stock_data
from src.strategies.ma_crossover import MA_Crossover
from src.backtesting.engine import BacktestingEngine

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
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
    returns list of all available tickers from database
    '''
    symbols = get_available_symbols()
    return {"symbols": symbols}

@app.get("/strategies")
def get_strategies():
    '''
    returns list of all available strategies
    '''
    return {"strategies": ["ma_crossover"]}

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
        
        # Check if symbol exists in database
        available_symbols = get_available_symbols()
        if request.symbol not in available_symbols:
            raise HTTPException(
                status_code=400, 
                detail=f"Symbol '{request.symbol}' not found in database. Available symbols: {available_symbols}"
            )
        
        # Get date range for the symbol
        start_available, end_available = get_date_range(request.symbol)
        
        # Validate requested dates
        try:
            start_requested = datetime.strptime(request.start_date, '%Y-%m-%d').date()
            end_requested = datetime.strptime(request.end_date, '%Y-%m-%d').date()
            start_available_dt = datetime.strptime(start_available, '%Y-%m-%d').date()
            end_available_dt = datetime.strptime(end_available, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Check if requested dates are within available range
        if start_requested < start_available_dt:
            raise HTTPException(
                status_code=400, 
                detail=f"Start date {request.start_date} is before available data. Earliest available: {start_available}"
            )
        
        if end_requested > end_available_dt:
            raise HTTPException(
                status_code=400, 
                detail=f"End date {request.end_date} is after available data. Latest available: {end_available}"
            )
        
        # Get data from database
        data_list = get_stock_data(request.symbol, request.start_date, request.end_date)
        
        if not data_list:
            raise HTTPException(
                status_code=400, 
                detail=f"No data found for {request.symbol} in the specified date range"
            )
        
        # Convert to DataFrame
        data = pd.DataFrame(data_list)
        data['date'] = pd.to_datetime(data['date'])
        data = data.set_index('date').sort_index()
        
        print(f"Retrieved {len(data)} records for {request.symbol} from {request.start_date} to {request.end_date}")
        
        # Initialize strategy based on request
        if request.strategy == "ma_crossover":
            # Extract strategy parameters with defaults
            fast_period = request.strategy_params.get('fast_period', 10)
            slow_period = request.strategy_params.get('slow_period', 30)
            initial_cash = request.initial_cash or 100000
            
            strategy = MA_Crossover(fast_period=fast_period, slow_period=slow_period, initial_cash=initial_cash)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown strategy: {request.strategy}. Available strategies: ['ma_crossover']"
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