from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np
from typing import Dict

class MA_Crossover(BaseStrategy):
    def __init__(self, fast_period: int, slow_period: int, initial_cash: float = 100000):
        self.fast_period = fast_period
        self.slow_period = slow_period
        super().__init__(initial_cash)

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        '''
        adds the following columns to the data:
        - fast_ma: fast moving average
        - slow_ma: slow moving average
        - buy_signal: 1 if fast_ma crosses above slow_ma, 0 otherwise
        - sell_signal: 1 if fast_ma crosses below slow_ma, 0 otherwise
        '''

        df = data.copy()
        df['fast_ma'] = df['close'].rolling(window=self.fast_period).mean()
        df['slow_ma'] = df['close'].rolling(window=self.slow_period).mean()
        
        # Detect crossovers (not just when one is above the other)
        df['fast_above_slow'] = df['fast_ma'] > df['slow_ma']
        df['fast_above_slow_prev'] = df['fast_above_slow'].shift(1)
        
        # Buy signal: fast_ma crosses above slow_ma
        df['buy_signal'] = np.where(
            (df['fast_above_slow'] == True) & (df['fast_above_slow_prev'] == False), 1, 0
        )
        
        # Sell signal: fast_ma crosses below slow_ma  
        df['sell_signal'] = np.where(
            (df['fast_above_slow'] == False) & (df['fast_above_slow_prev'] == True), 1, 0
        )
        
        # Clean up helper columns
        df = df.drop(['fast_above_slow', 'fast_above_slow_prev'], axis=1)
        
        return df

    def simulate_trades(self, data: pd.DataFrame, signals: pd.DataFrame) -> Dict:
        # For now, just return the signals for testing
        return {
            "signals": signals.to_dict('records'),
            "total_buy_signals": signals['buy_signal'].sum(),
            "total_sell_signals": signals['sell_signal'].sum()
        }

    def calculate_performance(self) -> Dict:
        pass