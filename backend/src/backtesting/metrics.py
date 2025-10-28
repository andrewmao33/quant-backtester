import pandas as pd

def get_basic_metrics(
    initial_cash: float,
    trades: list,
    portfolio_values: list
) -> dict:
    '''
    calculate basic metrics
    '''
    return {}

def get_sharpe_ratio(portfolio_values: list, risk_free_rate: float) -> float:
    '''
    calculate sharpe ratio
    risk_free_rate: annual risk-free rate
    '''
    if len(portfolio_values) < 2:
        return 0.0
    
    # Convert portfolio values to returns
    portfolio_series = pd.Series(portfolio_values)
    returns = portfolio_series.pct_change().dropna()
    
    if len(returns) == 0 or returns.std() == 0:
        return 0.0
    
    # Calculate annualized metrics
    # Assuming daily data, annualize by multiplying by 252 trading days
    annualized_return = returns.mean() * 252
    annualized_volatility = returns.std() * (252 ** 0.5)
    
    # Sharpe ratio = (Portfolio Return - Risk-Free Rate) / Portfolio Volatility
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    
    return sharpe_ratio

def get_sortino_ratio(portfolio_values: list, risk_free_rate: float) -> float:
    '''
    calculate sortino ratio
    risk_free_rate: annual risk-free rate (default 2%)
    '''
    if len(portfolio_values) < 2:
        return 0.0
    
    # Convert portfolio values to returns
    portfolio_series = pd.Series(portfolio_values)
    returns = portfolio_series.pct_change().dropna()
    
    if len(returns) == 0:
        return 0.0
    
    # Calculate annualized return
    annualized_return = returns.mean() * 252
    
    # Calculate downside deviation (only negative returns)
    negative_returns = returns[returns < 0]
    
    if len(negative_returns) == 0 or negative_returns.std() == 0:
        # If no negative returns, Sortino ratio is infinite (perfect downside protection)
        return float('inf') if annualized_return > risk_free_rate else 0.0
    
    # Calculate annualized downside deviation
    downside_deviation = negative_returns.std() * (252 ** 0.5)
    
    # Sortino ratio = (Portfolio Return - Risk-Free Rate) / Downside Deviation
    sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation
    
    return sortino_ratio

def get_max_drawdown(portfolio_values: list) -> float:
    '''
    calculate max drawdown
    '''
    return 0.0

def get_volatility(portfolio_values: list) -> float:
    '''
    calculate volatility
    '''
    return 0.0

def calculate_full_metrics(
    strategy: str,
    params: dict,
    initial_cash: float,
    trades: list,
    portfolio_values: list,
    risk_free_rate: float
) -> dict:
    '''
    calculate all metrics
    '''
    basic_metrics = get_basic_metrics(initial_cash, trades, portfolio_values)
    sharpe_ratio = get_sharpe_ratio(portfolio_values, risk_free_rate)
    sortino_ratio = get_sortino_ratio(portfolio_values, risk_free_rate)
    max_drawdown = get_max_drawdown(portfolio_values)
    volatility = get_volatility(portfolio_values)
    return {
        **basic_metrics,
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "max_drawdown": max_drawdown,
        "volatility": volatility
    }