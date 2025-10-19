from base_strategy import BaseStrategy
import pandas as pd
from typing import Dict

class MA_Crossover(BaseStrategy):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)

    def generate_signals(self) -> pd.DataFrame:
        pass

    def simulate_trades(self) -> pd.DataFrame:
        pass

    def calculate_performance(self) -> Dict:
        pass