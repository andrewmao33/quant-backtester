'''
abstract class that defines the interface for all strategies. One stock, full portfolio simulation.

attributes:
- name
- cash
- shares owned
- position (long/flat/short)
- list of trades
- list of portfolio values each day

methods:
- generate_signals(self, data) -> pd.DataFrame:
- simulate_trades(self, data, signals) -> pd.DataFrame:
- calculate_performance(self) -> Dict:

'''
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict

class BaseStrategy(ABC):
    def __init__(self, initial_cash: float = 100000):
        self.cash = initial_cash
        self.shares_owned = 0
        self.position = "flat"  # flat or long
        self.trades = []
        self.portfolio_values = []
    
    def buy(self, date, price):
        if self.position == "flat":
            shares_to_buy = self.cash / price
            self.cash = 0 
            self.shares_owned = shares_to_buy
            self.position = "long"
            self.trades.append({
                "date": date,
                "action": "buy",
                "price": price,
                "shares": shares_to_buy
            })
        else:
            raise ValueError("Cannot buy shares when position is not flat")

    def sell(self, date, price):
        if self.position == "long":
            shares_to_sell = self.shares_owned
            profit = shares_to_sell * price
            self.cash += profit
            self.shares_owned = 0
            self.position = "flat"
            self.trades.append({
                "date": date,
                "action": "sell",
                "price": price,
                "shares": shares_to_sell
            })
        else:
            raise ValueError("Cannot sell shares when position is not long")

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        '''
        generate signals for the strategy
        input: data - pd.DataFrame with stock data
        output: pd.DataFrame with signals
        '''
        pass

    @abstractmethod
    def simulate_trades(self, data: pd.DataFrame, signals: pd.DataFrame) -> Dict:
        '''
        data should include buy and sell signals
        return metrics
        '''
        return {"test": "test"}
        

    def calculate_performance(self) -> Dict:
        '''
        calculate performance metrics for the strategy
        output: Dict with performance metrics
        '''
        pass