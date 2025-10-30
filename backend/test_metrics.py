import math
import pytest
from src.backtesting.metrics import (
    get_basic_metrics,
    get_sharpe_ratio,
    get_sortino_ratio,
    get_max_drawdown,
    get_volatility,
    calculate_full_metrics,
)


def test_basic_metrics_no_trades_tracks_initial_when_no_portfolio_values():
    m = get_basic_metrics(initial_cash=1000.0, trades=[], portfolio_values=[])
    assert m["initial_cash"] == 1000.0
    assert m["final_portfolio_value"] == 1000.0
    assert m["total_return"] == 0.0
    assert m["total_trades"] == 0
    assert m["round_trips"] == 0


def test_basic_metrics_with_one_round_trip():
    # One buy then sell profit of 10 on 1 share
    trades = [
        {"action": "buy", "price": 100.0, "shares": 1.0},
        {"action": "sell", "price": 110.0, "shares": 1.0},
    ]
    portfolio_values = [1000.0, 1010.0]
    m = get_basic_metrics(initial_cash=1000.0, trades=trades, portfolio_values=portfolio_values)
    assert m["final_portfolio_value"] == 1010.0
    assert m["total_return"] == pytest.approx(0.01, rel=1e-9)
    assert m["total_trades"] == 2
    assert m["round_trips"] == 1
    assert m["win_rate"] == 1.0
    assert m["avg_win"] > 0


def test_sharpe_and_volatility_constant_series_zero():
    pv = [100.0] * 10
    assert get_volatility(pv) == 0.0
    assert get_sharpe_ratio(pv, risk_free_rate=0.02) == 0.0


def test_sortino_no_negative_returns_infinite_if_above_rf():
    # Strictly increasing series → no negative returns
    pv = [100, 101, 102, 103, 104]
    s = get_sortino_ratio(pv, risk_free_rate=0.0)
    assert s == float('inf')


def test_max_drawdown_simple_drop_and_recovery():
    # peak at 120, drop to 90 (25%), recover to 110 → max drawdown is 25%
    pv = [100, 120, 90, 110]
    md = get_max_drawdown(pv)
    assert md == pytest.approx(0.25, rel=1e-9)


def test_calculate_full_metrics_integration():
    trades = [
        {"action": "buy", "price": 100.0, "shares": 1.0},
        {"action": "sell", "price": 110.0, "shares": 1.0},
    ]
    pv = [1000.0, 1010.0, 1005.0, 1015.0]
    res = calculate_full_metrics(
        strategy="TestStrat",
        params={"a": 1},
        initial_cash=1000.0,
        trades=trades,
        portfolio_values=pv,
        risk_free_rate=0.02,
    )
    # Basic presence checks
    for k in [
        "initial_cash", "final_portfolio_value", "total_return",
        "sharpe_ratio", "sortino_ratio", "max_drawdown", "volatility",
        "total_trades", "round_trips"
    ]:
        assert k in res
    assert res["total_trades"] == 2
    assert res["round_trips"] == 1
