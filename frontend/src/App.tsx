import React, { useState, useEffect } from 'react';
import './App.css';
import PortfolioChart from './components/PortfolioChart';
import MACrossoverChart from './components/MACrossoverChart';
import BollingerChart from './components/BollingerChart';

function App() {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [strategies, setStrategies] = useState<string[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [symbolQuery, setSymbolQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [highlightIndex, setHighlightIndex] = useState(0);
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [fastPeriod, setFastPeriod] = useState(10);
  const [slowPeriod, setSlowPeriod] = useState(20);
  const [bbPeriod, setBbPeriod] = useState(20);
  const [bbStd, setBbStd] = useState(2);
  const [initialCash, setInitialCash] = useState(100000);
  const [results, setResults] = useState<any>(null);
  const [lastRunSymbol, setLastRunSymbol] = useState('');
  const [loading, setLoading] = useState(false);

  const currency = new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  const percent = new Intl.NumberFormat(undefined, { style: 'percent', maximumFractionDigits: 2 });
  const number = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 });

  const formatMetric = (v: any, fmt: 'currency' | 'percent' | 'number' | 'integer') => {
    if (v === null || v === undefined || Number.isNaN(v)) return '-';
    switch (fmt) {
      case 'currency':
        return currency.format(Number(v));
      case 'percent': {
        // Backend returns some metrics already as fractions (0.12) and some possibly as percent (e.g., total_return in simulate_trades is 0-100). Normalize.
        const n = Number(v);
        const isFraction = Math.abs(n) <= 1;
        return percent.format(isFraction ? n : n / 100);
      }
      case 'integer':
        return Math.round(Number(v)).toString();
      default:
        return number.format(Number(v));
    }
  };

  useEffect(() => {
    // Fetch symbols and strategies
    fetch('http://localhost:8000/symbols')
      .then(res => res.json())
      .then(data => setSymbols(data.symbols));
    
    fetch('http://localhost:8000/strategies')
      .then(res => res.json())
      .then(data => setStrategies(data.strategies));
  }, []);

  const runBacktest = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: selectedSymbol,
          start_date: startDate,
          end_date: endDate,
          strategy: selectedStrategy,
          initial_cash: initialCash,
          strategy_params: selectedStrategy === 'ma_crossover'
            ? {
                fast_period: fastPeriod,
                slow_period: slowPeriod,
              }
            : selectedStrategy === 'bollinger_breakout'
            ? {
                period: bbPeriod,
                std: bbStd,
              }
            : {}
        })
      });
      const data = await response.json();
      setLastRunSymbol(selectedSymbol);
      setResults(data);
    } catch (error) {
      setResults({ error: 'Failed to run backtest' });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="max-w-4xl mx-auto px-3 py-6 pt-16 sm:pt-20 flex flex-col items-center text-center relative">
        {/* Outer vertical lines */}
        <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-gray-700/50 -ml-8"></div>
        <div className="absolute right-0 top-0 bottom-0 w-0.5 bg-gray-700/50 -mr-8"></div>
        {/* Inner vertical lines */}
        <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-gray-700/50"></div>
        <div className="absolute right-0 top-0 bottom-0 w-0.5 bg-gray-700/50"></div>
        <h1 className="text-6xl sm:text-7xl font-extralight tracking-tight mb-10">QuantLab</h1>

        <div className="w-screen border-t-2 border-gray-700/50 mb-8 -mx-6" />

        {/* Core inputs row */}
        <div className="w-full flex flex-wrap items-end justify-center gap-4 mb-8">
          <div className="flex flex-col items-center relative">
            <label className="text-sm text-gray-300 mb-1">Stock</label>
            <input
              type="text"
              value={symbolQuery}
              onChange={(e) => {
                const val = e.target.value.toUpperCase();
                setSymbolQuery(val);
                setShowSuggestions(!!val);
                setHighlightIndex(0);
              }}
              onKeyDown={(e) => {
                const filtered = symbols
                  .filter(s => s.includes(symbolQuery.toUpperCase()))
                  .slice(0, 20);
                if (e.key === 'ArrowDown') {
                  e.preventDefault();
                  if (!showSuggestions) setShowSuggestions(true);
                  if (filtered.length > 0) {
                    setHighlightIndex((prev) => (prev + 1) % filtered.length);
                  }
                } else if (e.key === 'ArrowUp') {
                  e.preventDefault();
                  if (!showSuggestions) setShowSuggestions(true);
                  if (filtered.length > 0) {
                    setHighlightIndex((prev) => (prev - 1 + filtered.length) % filtered.length);
                  }
                } else if (e.key === 'Enter') {
                  const choice = (showSuggestions && filtered.length > 0)
                    ? filtered[highlightIndex]
                    : symbols.filter(s => s.includes(symbolQuery.toUpperCase()))[0];
                  if (choice) {
                    setSelectedSymbol(choice);
                    setSymbolQuery(choice);
                    setShowSuggestions(false);
                  }
                } else if (e.key === 'Escape') {
                  setShowSuggestions(false);
                }
              }}
              onFocus={() => setShowSuggestions(!!symbolQuery)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 100)}
              placeholder="Search symbol..."
              className="bg-gray-900 border border-gray-700 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600 w-48"
            />
            {showSuggestions && symbolQuery && (
              <div className="absolute top-[58px] z-10 max-h-56 w-60 overflow-auto rounded border border-gray-700 bg-black/95 shadow-lg">
                {symbols
                  .filter(s => s.includes(symbolQuery.toUpperCase()))
                  .slice(0, 20)
                  .map((s, idx) => (
                    <div
                      key={s}
                      className={`px-3 py-2 cursor-pointer ${idx === highlightIndex ? 'bg-gray-800' : 'hover:bg-gray-800'} ${s === selectedSymbol ? 'bg-gray-900' : ''}`}
                      onMouseEnter={() => setHighlightIndex(idx)}
                      onMouseDown={() => {
                        setSelectedSymbol(s);
                        setSymbolQuery(s);
                        setShowSuggestions(false);
                      }}
                    >
                      {s}
                    </div>
                  ))}
                {symbols.filter(s => s.includes(symbolQuery.toUpperCase())).length === 0 && (
                  <div className="px-3 py-2 text-gray-400">No matches</div>
                )}
              </div>
            )}
          </div>

          <div className="flex flex-col items-center">
            <label className="text-sm text-gray-300 mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="bg-gray-900 border border-gray-700 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>

          <div className="flex flex-col items-center">
            <label className="text-sm text-gray-300 mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="bg-gray-900 border border-gray-700 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>

          <div className="flex flex-col items-center">
            <label className="text-sm text-gray-300 mb-1">Initial Cash ($)</label>
            <input
              type="number"
              value={initialCash}
              onChange={(e) => setInitialCash(Number(e.target.value))}
              min={1000}
              step={1000}
              className="bg-gray-900 border border-gray-700 rounded px-3 py-2 w-36 focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>
        </div>

        {/* Strategy selector */}
        <div className="w-full flex flex-wrap items-end justify-center gap-4 mb-8">
          <div className="flex flex-col items-center">
            <label className="text-sm text-gray-300 mb-1">Strategy</label>
            <select 
              value={selectedStrategy} 
              onChange={(e) => setSelectedStrategy(e.target.value)}
              className="bg-gray-900 border border-gray-700 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="">Select strategy</option>
              {strategies.map(strategy => (
                <option key={strategy} value={strategy}>{strategy}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Conditional params */}
        {selectedStrategy === 'ma_crossover' && (
          <div className="w-full flex flex-wrap items-end justify-center gap-4 mb-8">
            <div className="flex flex-col items-center">
              <label className="text-sm text-gray-300 mb-1">Fast Period</label>
              <input
                type="number"
                value={fastPeriod}
                onChange={(e) => setFastPeriod(Number(e.target.value))}
                className="bg-gray-900 border border-gray-700 rounded px-3 py-2 w-24 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
            <div className="flex flex-col items-center">
              <label className="text-sm text-gray-300 mb-1">Slow Period</label>
              <input
                type="number"
                value={slowPeriod}
                onChange={(e) => setSlowPeriod(Number(e.target.value))}
                className="bg-gray-900 border border-gray-700 rounded px-3 py-2 w-24 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>
        )}

        {selectedStrategy === 'bollinger_breakout' && (
          <div className="w-full flex flex-wrap items-end justify-center gap-4 mb-8">
            <div className="flex flex-col items-center">
              <label className="text-sm text-gray-300 mb-1">Period</label>
              <input
                type="number"
                value={bbPeriod}
                onChange={(e) => setBbPeriod(Number(e.target.value))}
                className="bg-gray-900 border border-gray-700 rounded px-3 py-2 w-24 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
            <div className="flex flex-col items-center">
              <label className="text-sm text-gray-300 mb-1">Std Dev</label>
              <input
                type="number"
                value={bbStd}
                onChange={(e) => setBbStd(Number(e.target.value))}
                className="bg-gray-900 border border-gray-700 rounded px-3 py-2 w-24 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>
        )}

        {/* Run button */}
        <div className="mb-10 flex justify-center">
          <button
            onClick={runBacktest}
            disabled={!selectedSymbol || !selectedStrategy || !startDate || !endDate || loading}
            className="px-5 py-2 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium"
          >
            {loading ? 'Running…' : 'Run Backtest'}
          </button>
        </div>

        <div className="w-screen border-t-2 border-gray-700/50 mb-8 -mx-6" />

        {results && (
          <div className="mt-8 w-full">
            <div className="mb-8">
              <h3 className="text-lg font-medium mb-3">Key Metrics</h3>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 max-w-3xl mx-auto">
                {([
                  { label: 'Final Portfolio Value', value: results.final_portfolio_value, fmt: 'currency' },
                  { label: 'Total Return', value: results.total_return, fmt: 'percent' },
                  { label: 'Volatility (ann.)', value: results.volatility, fmt: 'percent' },
                  { label: 'Sharpe Ratio', value: results.sharpe_ratio, fmt: 'number' },
                  { label: 'Sortino Ratio', value: results.sortino_ratio, fmt: 'number' },
                  { label: 'Max Drawdown', value: results.max_drawdown, fmt: 'percent' },
                  { label: 'Trades (executions)', value: results.total_trades, fmt: 'integer' },
                  { label: 'Round Trips', value: results.round_trips, fmt: 'integer' },
                  { label: 'Win Rate', value: results.win_rate, fmt: 'percent' },
                  { label: 'Avg Win PnL', value: results.avg_win, fmt: 'currency' },
                  { label: 'Avg Loss PnL', value: results.avg_loss, fmt: 'currency' },
                  { label: 'Avg Trade Return', value: results.avg_trade_return, fmt: 'percent' },
                ] as const).filter(card => card.value !== undefined && card.value !== null).map((card) => (
                  <div key={card.label} className="border border-gray-800 rounded p-3 bg-black/20">
                    <div className="text-xs text-gray-400">{card.label}</div>
                    <div className="text-lg font-semibold">
                      {formatMetric(card.value, card.fmt)}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Edge-to-edge horizontal line below metrics grid */}
            <div className="w-screen border-t-2 border-gray-700/50 relative left-1/2 -translate-x-1/2 mb-8" />

            {results.portfolio_values && results.portfolio_values.length > 0 && (
              <div className="mb-4 w-full">
                <PortfolioChart data={results.portfolio_values} />
              </div>
            )}

            {selectedStrategy === 'ma_crossover' && (
              <div className="mb-4 w-full">
                <MACrossoverChart 
                  key={lastRunSymbol + startDate + endDate + (results?.candles?.length ?? 0) + (results?.trades?.length ?? 0)}
                  title={`${lastRunSymbol} Price with Trading Signals`}
                  candles={results.candles || []}
                  trades={(results.trades || []).map((t: any) => ({ date: t.date, action: t.action, price: t.price }))}
                  fastMA={(results.fast_ma || []).filter((p: any) => p && p.date).map((p: any) => ({ date: p.date, value: p.value }))}
                  slowMA={(results.slow_ma || []).filter((p: any) => p && p.date).map((p: any) => ({ date: p.date, value: p.value }))}
                />
              </div>
            )}

            {selectedStrategy === 'bollinger_breakout' && (
              <div className="mb-4 w-full">
                <BollingerChart
                  key={lastRunSymbol + startDate + endDate + (results?.candles?.length ?? 0) + (results?.trades?.length ?? 0)}
                  title={`${lastRunSymbol} Price with Bollinger Bands`}
                  candles={results.candles || []}
                  upper={(results.upper_band || []).filter((p: any) => p && p.date).map((p: any) => ({ date: p.date, value: p.value }))}
                  lower={(results.lower_band || []).filter((p: any) => p && p.date).map((p: any) => ({ date: p.date, value: p.value }))}
                  trades={(results.trades || []).map((t: any) => ({ date: t.date, action: t.action, price: t.price }))}
                />
              </div>
            )}

            <div className="w-screen border-t-2 border-gray-700/50 relative left-1/2 -translate-x-1/2 mb-8" />

            <details>
              <summary className="cursor-pointer mb-2">Raw JSON</summary>
              <pre className="bg-gray-900 p-4 overflow-auto rounded border border-gray-800 text-left">
                {JSON.stringify(results, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
