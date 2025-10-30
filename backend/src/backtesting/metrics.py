import pandas as pd

def get_basic_metrics(
    initial_cash: float,
    trades: list,
    portfolio_values: list
) -> dict:
    '''
    calculate basic metrics
    '''
    metrics = {
        "initial_cash": float(initial_cash),
        "final_portfolio_value": float(portfolio_values[-1]) if portfolio_values else float(initial_cash),
    }

    # Total return based on portfolio values time series
    final_value = metrics["final_portfolio_value"]
    total_return = 0.0
    if initial_cash > 0:
        total_return = (final_value - initial_cash) / initial_cash
    metrics["total_return"] = float(total_return)

    # Derive round-trip trade PnLs from trades list (buy followed by sell)
    round_trip_pnls = []
    last_buy = None
    for t in trades:
        action = t.get("action")
        if action == "buy":
            last_buy = t
        elif action == "sell" and last_buy is not None:
            buy_price = float(last_buy.get("price", 0.0))
            sell_price = float(t.get("price", 0.0))
            shares = float(min(last_buy.get("shares", 0.0), t.get("shares", 0.0)))
            pnl = (sell_price - buy_price) * shares
            # Return for the trade relative to cost basis
            cost = buy_price * shares if buy_price > 0 else 0.0
            ret = (pnl / cost) if cost > 0 else 0.0
            round_trip_pnls.append({
                "pnl": pnl,
                "return": ret
            })
            last_buy = None

    num_round_trips = len(round_trip_pnls)
    wins = [p for p in round_trip_pnls if p["pnl"] > 0]
    losses = [p for p in round_trip_pnls if p["pnl"] <= 0]

    metrics.update({
        "total_trades": int(len(trades)),
        "round_trips": int(num_round_trips),
        "win_rate": (len(wins) / num_round_trips) if num_round_trips > 0 else 0.0,
        "avg_win": float(sum(p["pnl"] for p in wins) / len(wins)) if wins else 0.0,
        "avg_loss": float(sum(p["pnl"] for p in losses) / len(losses)) if losses else 0.0,
        "avg_trade_return": float(sum(p["return"] for p in round_trip_pnls) / num_round_trips) if num_round_trips > 0 else 0.0,
    })

    return metrics

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
    if not portfolio_values:
        return 0.0
    s = pd.Series(portfolio_values, dtype="float64")
    running_max = s.cummax()
    drawdown = s / running_max - 1.0
    max_dd = drawdown.min()  # most negative
    return float(abs(max_dd))

def get_volatility(portfolio_values: list) -> float:
    '''
    calculate volatility
    '''
    if len(portfolio_values) < 2:
        return 0.0
    s = pd.Series(portfolio_values, dtype="float64")
    rets = s.pct_change().dropna()
    if len(rets) == 0:
        return 0.0
    annualized_vol = rets.std() * (252 ** 0.5)
    return float(annualized_vol)

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