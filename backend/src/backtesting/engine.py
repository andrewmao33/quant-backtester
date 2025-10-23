'''
backtesting engine

should take in a strategy and return backtest result and visualizations
'''

import pandas as pd
from src.strategies.base_strategy import BaseStrategy

class BacktestingEngine:
    def __init__(self, strategy: BaseStrategy):
        self.strategy = strategy

    def run(self, data: pd.DataFrame):
        signals = self.strategy.generate_signals(data)
        trade_results = self.strategy.simulate_trades(data, signals)
        #performance_metrics = self.strategy.calculate_performance()
        
        # Combine trade results with performance metrics
        return {
            **trade_results
            #**performance_metrics
        }
