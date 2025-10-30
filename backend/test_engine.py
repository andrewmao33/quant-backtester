import pandas as pd
import pytest
from src.backtesting.engine import BacktestingEngine
from src.strategies.base_strategy import BaseStrategy

class DummyStrategy(BaseStrategy):
    def generate_signals(self, data):
        # Return a dummy signal (all zeros, same length as data)
        return [0] * len(data)
    def simulate_trades(self, data, signals):
        # Return a dummy result
        return {'profit': 0, 'trades': 0}

# Strategy that uses BaseStrategy.simulate_trades to exercise real flow
class DummySignalStrategy(BaseStrategy):
    def __init__(self, pattern: str = "alternate"):
        super().__init__()
        # params used by BaseStrategy.calculate_metrics
        self.params = {"pattern": pattern}
        self.pattern = pattern

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        index = data.index
        close = data["close"].astype(float)
        if self.pattern == "alternate":
            # buy on even idx, sell on odd idx, starting with buy at 0
            buy_signal = [(1 if i % 2 == 0 else 0) for i in range(len(index))]
            sell_signal = [(1 if i % 2 == 1 else 0) for i in range(len(index))]
        elif self.pattern == "none":
            buy_signal = [0] * len(index)
            sell_signal = [0] * len(index)
        else:
            buy_signal = [0] * len(index)
            sell_signal = [0] * len(index)
        df = pd.DataFrame({
            "buy_signal": buy_signal,
            "sell_signal": sell_signal,
            "close": close.values,
        }, index=index)
        return df

def _make_ohlcv(days: int = 4, start_price: float = 100.0) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=days, freq="D")
    prices = [start_price + i for i in range(days)]
    data = pd.DataFrame({
        "open": prices,
        "high": [p + 1 for p in prices],
        "low": [p - 1 for p in prices],
        "close": prices,
        "volume": [1000] * days,
    }, index=dates)
    return data


def test_backtesting_engine_run():
    data = pd.DataFrame({
        'open': [1, 2, 3],
        'close': [2, 3, 4],
        'high': [2, 4, 5],
        'low': [1, 1, 2],
        'volume': [10, 10, 10]
    })
    strategy = DummyStrategy()
    engine = BacktestingEngine(strategy)
    result = engine.run(data)
    assert isinstance(result, dict)
    assert 'profit' in result
    assert 'trades' in result


def test_engine_alternate_buy_sell_round_trips():
    data = _make_ohlcv(days=4, start_price=100.0)
    strategy = DummySignalStrategy(pattern="alternate")
    engine = BacktestingEngine(strategy)
    result = engine.run(data)

    # Should have executed two round trips: buy day0, sell day1, buy day2, sell day3
    assert isinstance(result, dict)
    assert result["total_trades"] == 4
    assert result.get("round_trips") == 2
    assert result["final_shares"] == 0
    assert result["final_cash"] > 100000 - 1  # cash back after sells
    assert isinstance(result.get("portfolio_values"), list)
    assert len(result["portfolio_values"]) == len(data)


def test_engine_no_signals_results_in_no_trades():
    data = _make_ohlcv(days=5, start_price=50.0)
    strategy = DummySignalStrategy(pattern="none")
    engine = BacktestingEngine(strategy)
    result = engine.run(data)

    assert result["total_trades"] == 0
    assert result["final_shares"] == 0
    # With no trades, portfolio tracks cash value each day using close prices; final equals initial_cash
    assert pytest.approx(result["final_portfolio_value"], rel=1e-6) == pytest.approx(strategy.initial_cash, rel=1e-6)


def test_engine_empty_dataframe_raises():
    data = pd.DataFrame(columns=["open", "high", "low", "close", "volume"]).set_index(pd.Index([], name=None))
    strategy = DummySignalStrategy(pattern="none")
    engine = BacktestingEngine(strategy)
    with pytest.raises(IndexError):
        engine.run(data)
