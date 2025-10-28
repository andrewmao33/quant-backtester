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
        self.initial_cash = initial_cash
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

    def simulate_trades(self, data: pd.DataFrame, signals: pd.DataFrame) -> Dict:
        """
        Execute trades based on buy/sell signals - common logic for all strategies
        """
        # Reset strategy state
        self.cash = self.initial_cash  # Use consistent initial cash value
        self.shares_owned = 0
        self.position = "flat"
        self.trades = []
        
        # Execute trades day by day
        for index, row in signals.iterrows():
            date = index  # Use the index (date) since it's set as index
            price = row['close']
            
            # Buy signal
            if row['buy_signal'] == 1 and self.position == "flat":
                self.buy(date, price)
            
            # Sell signal  
            elif row['sell_signal'] == 1 and self.position == "long":
                self.sell(date, price)

            self.portfolio_values.append({
                "date": date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)[:10],
                "portfolio_value": self.cash + (self.shares_owned * price)
            })
        
        # Calculate final portfolio value
        final_price = signals.iloc[-1]['close']
        final_portfolio_value = self.cash + (self.shares_owned * final_price)
        metrics = self.calculate_metrics(data)
        
        return {
            "trades": self.trades,
            "total_trades": len(self.trades),
            "final_cash": self.cash,
            "final_shares": self.shares_owned,
            "final_portfolio_value": final_portfolio_value,
            "total_return": (final_portfolio_value - 100000) / 100000 * 100,
            "portfolio_values": self.portfolio_values,
            **metrics
        }
        
    def calculate_metrics(self, data: pd.DataFrame) -> Dict:
        '''
        calculate metrics
        '''
        from src.backtesting.metrics import calculate_full_metrics
        
        # Extract just the portfolio values as numbers
        portfolio_values_list = [pv['portfolio_value'] for pv in self.portfolio_values]
        
        return calculate_full_metrics(
            strategy=self.__class__.__name__,
            params=self.params,
            initial_cash=self.initial_cash,
            trades=self.trades,
            portfolio_values=portfolio_values_list,
            risk_free_rate=0.02  # Use 2% as default risk-free rate
        )
