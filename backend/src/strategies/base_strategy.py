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

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        '''
        generate signals for the strategy
        input: data - pd.DataFrame with stock data
        output: pd.DataFrame with signals
        '''
        pass

    @abstractmethod
    def simulate_trades(self, data: pd.DataFrame, signals: pd.DataFrame) -> pd.DataFrame:
        '''
        simulate trades for the strategy
        input: data - pd.DataFrame with stock data, signals - pd.DataFrame with buy/sell signals
        output: pd.DataFrame with trades
        '''
        pass

    def calculate_performance(self) -> Dict:
        '''
        calculate performance metrics for the strategy
        output: Dict with performance metrics
        '''
        pass