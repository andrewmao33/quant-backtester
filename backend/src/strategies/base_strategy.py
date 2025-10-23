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

    def simulate_trades(self, data: pd.DataFrame, signals: pd.DataFrame) -> Dict:
        """
        Execute trades based on buy/sell signals - common logic for all strategies
        """
        # Reset strategy state
        self.cash = 1000000
        self.shares_owned = 0
        self.position = "flat"
        self.trades = []
        
        # Execute trades day by day
        for index, row in signals.iterrows():
            date = row['Date']  # Use the date column
            price = row['Close']
            
            # Buy signal
            if row['buy_signal'] == 1 and self.position == "flat":
                self.buy(date, price)
            
            # Sell signal  
            elif row['sell_signal'] == 1 and self.position == "long":
                self.sell(date, price)

            self.portfolio_values.append({
                "date": date,
                "portfolio_value": self.cash + (self.shares_owned * price)
            })
        
        # Calculate final portfolio value
        final_price = signals.iloc[-1]['Close']
        final_portfolio_value = self.cash + (self.shares_owned * final_price)
        
        return {
            "trades": self.trades,
            "total_trades": len(self.trades),
            "final_cash": self.cash,
            "final_shares": self.shares_owned,
            "final_portfolio_value": final_portfolio_value,
            "total_return": (final_portfolio_value - 100000) / 100000 * 100,
            "portfolio_values": self.portfolio_values
        }
        

    def calculate_performance(self) -> Dict:
        '''
        calculate basic performance metrics

        total return
        final portfolio value
        total trades
        sharpe ratio - later

        '''
        if len(self.trades) == 0:
            return {
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0
            }
        
        # Simple metrics for now
        total_return = (self.cash + (self.shares_owned * 100) - 100000) / 100000 * 100
        
        return {
            "total_return": total_return,
            "sharpe_ratio": 0.0,  # Placeholder
            "max_drawdown": 0.0   # Placeholder
        }