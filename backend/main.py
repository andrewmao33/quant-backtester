from fastapi import FastAPI
import yfinance as yf
import pandas as pd

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# retrieve data for a given symbol
@app.get("/data/{symbol}")
def get_stock_data(symbol: str):
    try:
        ticket = yf.Ticker(symbol)
        data = ticket.history(period="1y")

        result = []
        for index, row in data.iterrows():
            result.append({
                "date": index.strftime("%Y-%m-%d"),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"]
            })

        return {
            "symbol": symbol,
            "data": result[-10:]
        }
    except Exception as e:
        raise {"error": str(e)}

@app.get("/backtest")
def run_backtest():
    return {"message": "Backtest would run here"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)