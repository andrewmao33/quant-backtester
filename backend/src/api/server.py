from fastapi import FastAPI
from pydantic import BaseModel
import yfinance as yf
import pandas as pd

from src.data.fetcher import fetch_stock_data

app = FastAPI()

class BacktestRequest(BaseModel):
    symbol: str
    period: str = "1y"

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/backtest")
def run_backtest(request: BacktestRequest):
    try:
        print(request)
        data = fetch_stock_data(request.symbol, request.period)
        return data
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)