from fastapi import FastAPI
from pydantic import BaseModel
import yfinance as yf
import pandas as pd

from src.data.fetcher import fetch_stock_data
from src.strategies.ma_crossover import MA_Crossover
from src.backtesting.engine import BacktestingEngine

app = FastAPI()

class BacktestRequest(BaseModel):
    symbol: str
    period: str = "1y"
    strategy: str = "ma_crossover" # just ma_crossover for now

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/backtest")
def run_backtest(request: BacktestRequest):
    try:
        print(request)
        data_list = fetch_stock_data(request.symbol, request.period)
        
        # Handle case where data fetching fails
        if data_list is None:
            return {"error": "Failed to fetch data from yfinance and no cached data available"}
        
        data = pd.DataFrame(data_list)  # Convert list to DataFrame

        strategy = MA_Crossover(fast_period=10, slow_period=20)
        engine = BacktestingEngine(strategy)
        results = engine.run(data)
        return results
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)