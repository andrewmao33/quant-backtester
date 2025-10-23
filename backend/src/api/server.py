from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
import pandas as pd

from src.data.fetcher import fetch_stock_data
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
    period: str = "1y"
    strategy: str = "ma_crossover" # just ma_crossover for now
    fast_period: int = 10
    slow_period: int = 20

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/symbols")
def get_symbols():
    '''
    returns list of all available tickers
    '''
    return {"symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]}

@app.get("/strategies")
def get_strategies():
    '''
    returns list of all available strategies
    '''
    return {"strategies": ["ma_crossover"]}

@app.post("/backtest")
def run_backtest(request: BacktestRequest):
    try:
        print(request)
        data_list = fetch_stock_data(request.symbol, request.period)
        
        # Handle case where data fetching fails
        if data_list is None:
            return {"error": "Failed to fetch data from yfinance and no cached data available"}
        
        data = pd.DataFrame(data_list)  # Convert list to DataFrame

        strategy = MA_Crossover(fast_period=request.fast_period, slow_period=request.slow_period)
        engine = BacktestingEngine(strategy)
        results = engine.run(data)
        return results
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)