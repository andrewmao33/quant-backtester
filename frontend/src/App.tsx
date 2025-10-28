import React, { useState, useEffect } from 'react';
import './App.css';
import PortfolioChart from './components/PortfolioChart';

function App() {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [strategies, setStrategies] = useState<string[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [fastPeriod, setFastPeriod] = useState(10);
  const [slowPeriod, setSlowPeriod] = useState(20);
  const [initialCash, setInitialCash] = useState(100000);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

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
          strategy_params: {
            fast_period: fastPeriod,
            slow_period: slowPeriod,
          }
        })
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      setResults({ error: 'Failed to run backtest' });
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Backtester</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <label>Stock: </label>
        <select value={selectedSymbol} onChange={(e) => setSelectedSymbol(e.target.value)}>
          <option value="">Select stock</option>
          {symbols.map(symbol => (
            <option key={symbol} value={symbol}>{symbol}</option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label>Start Date: </label>
        <input 
          type="date" 
          value={startDate} 
          onChange={(e) => setStartDate(e.target.value)}
          style={{ marginRight: '20px' }}
        />
        <label>End Date: </label>
        <input 
          type="date" 
          value={endDate} 
          onChange={(e) => setEndDate(e.target.value)}
        />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label>Strategy: </label>
        <select value={selectedStrategy} onChange={(e) => setSelectedStrategy(e.target.value)}>
          <option value="">Select strategy</option>
          {strategies.map(strategy => (
            <option key={strategy} value={strategy}>{strategy}</option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label>Fast Period: </label>
        <input 
          type="number" 
          value={fastPeriod} 
          onChange={(e) => setFastPeriod(Number(e.target.value))}
          style={{ width: '80px' }}
        />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label>Slow Period: </label>
        <input 
          type="number" 
          value={slowPeriod} 
          onChange={(e) => setSlowPeriod(Number(e.target.value))}
          style={{ width: '80px' }}
        />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label>Initial Cash: $</label>
        <input 
          type="number" 
          value={initialCash} 
          onChange={(e) => setInitialCash(Number(e.target.value))}
          style={{ width: '120px' }}
          min="1000"
          step="1000"
        />
      </div>

      <button 
        onClick={runBacktest} 
        disabled={!selectedSymbol || !selectedStrategy || !startDate || !endDate || loading}
        style={{ padding: '10px 20px', fontSize: '16px' }}
      >
        {loading ? 'Running...' : 'Run Backtest'}
      </button>

      {results && (
        <div style={{ marginTop: '30px' }}>
          <h2>Results:</h2>
          
          {/* Portfolio Chart */}
          {results.portfolio_values && results.portfolio_values.length > 0 && (
            <div style={{ marginBottom: '30px' }}>
              <PortfolioChart data={results.portfolio_values} />
            </div>
          )}
          
          {/* Raw Results */}
          <pre style={{ background: '#f5f5f5', padding: '15px', overflow: 'auto' }}>
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;
