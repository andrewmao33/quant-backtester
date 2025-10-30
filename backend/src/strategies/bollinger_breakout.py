from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np
from typing import Dict

class BollingerBreakout(BaseStrategy):
    def __init__(self, period: int = 20, std: int = 2, initial_cash: float = 100000):
        self.params = {
            "period": period,
            "std": std
        }
        super().__init__(initial_cash)

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        '''
        Adds Bollinger Bands and breakout signals to the dataframe:
        - middle_band: simple moving average over period
        - upper_band: middle + std * rolling_std
        - lower_band: middle - std * rolling_std
        - buy_signal: 1 if close crosses above upper_band
        - sell_signal: 1 if close crosses below lower_band
        '''

        df = data.copy()
        period = int(self.params["period"])
        num_std = float(self.params["std"])

        rolling_mean = df['close'].rolling(window=period).mean()
        rolling_std = df['close'].rolling(window=period).std(ddof=0)

        df['middle_band'] = rolling_mean
        df['upper_band'] = rolling_mean + num_std * rolling_std
        df['lower_band'] = rolling_mean - num_std * rolling_std

        # Prior day values for crossover detection
        prev_close = df['close'].shift(1)
        prev_upper = df['upper_band'].shift(1)
        prev_lower = df['lower_band'].shift(1)

        # Buy when price crosses above upper band; sell when crosses below lower band
        df['buy_signal'] = np.where((prev_close <= prev_upper) & (df['close'] > df['upper_band']), 1, 0)
        df['sell_signal'] = np.where((prev_close >= prev_lower) & (df['close'] < df['lower_band']), 1, 0)

        return df
