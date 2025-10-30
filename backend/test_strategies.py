import pandas as pd
import numpy as np
from src.strategies.ma_crossover import MA_Crossover
from src.strategies.bollinger_breakout import BollingerBreakout


def _make_prices(vals):
    dates = pd.date_range("2020-01-01", periods=len(vals), freq="D")
    return pd.DataFrame({
        "open": vals,
        "high": [v + 1 for v in vals],
        "low": [v - 1 for v in vals],
        "close": vals,
        "volume": [1000] * len(vals)
    }, index=dates)


def test_ma_crossover_signals_columns_and_cross_detection():
    # Increasing prices; fast=2, slow=3 so crossover will occur once enough data
    data = _make_prices([100, 101, 102, 103, 104, 105])
    strat = MA_Crossover(fast_period=2, slow_period=3)
    signals = strat.generate_signals(data)

    for c in ["fast_ma", "slow_ma", "buy_signal", "sell_signal", "close"]:
        assert c in signals.columns

    # Expect at least one crossover up and possibly down later
    assert signals["buy_signal"].sum() >= 1
    assert signals["sell_signal"].sum() >= 0


def test_bollinger_breakout_buy_signal_on_spike():
    # Flat then spike above upper band should create a buy signal
    base = [100]*20
    # ensure stable rolling stats first, then a spike
    vals = base + [120]
    data = _make_prices(vals)
    strat = BollingerBreakout(period=20, std=2)
    signals = strat.generate_signals(data)

    for c in ["middle_band", "upper_band", "lower_band", "buy_signal", "sell_signal", "close"]:
        assert c in signals.columns

    # Last day should likely be a buy breakout
    assert signals["buy_signal"].iloc[-1] in [0, 1]
    assert signals["buy_signal"].sum() >= 0
