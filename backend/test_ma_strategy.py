#!/usr/bin/env python3
"""
Test script for MA Crossover Strategy
Creates sample data and tests the strategy without needing the API server
"""

import pandas as pd
import numpy as np
import os
import sys

# Add src to path so we can import our modules
sys.path.append('src')

from src.strategies.ma_crossover import MA_Crossover
from src.backtesting.engine import BacktestingEngine

def create_sample_data():
    """Create sample stock data for testing"""
    print("Creating sample data...")
    
    # Generate 100 days of price data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)  # For reproducible results
    
    # Create a price series with some trend and volatility
    base_price = 100
    returns = np.random.normal(0.001, 0.02, 100)  # 0.1% daily return, 2% volatility
    prices = base_price * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'date': dates,
        'close': prices
    })
    
    print(f"Created {len(data)} days of sample data")
    print(f"Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    return data

def test_ma_strategy():
    """Test the MA crossover strategy"""
    print("\n" + "="*50)
    print("TESTING MA CROSSOVER STRATEGY")
    print("="*50)
    
    # Create sample data
    data = create_sample_data()
    
    # Create strategy
    print("\nCreating MA Crossover strategy (fast=10, slow=20)...")
    strategy = MA_Crossover(fast_period=10, slow_period=20)
    
    # Create backtesting engine
    print("Creating backtesting engine...")
    engine = BacktestingEngine(strategy)
    
    # Run the strategy
    print("Running backtest...")
    results = engine.run(data)
    
    # Display results
    print("\n" + "="*30)
    print("RESULTS")
    print("="*30)
    print(f"Total trades executed: {results['total_trades']}")
    print(f"Final cash: ${results['final_cash']:.2f}")
    print(f"Final shares: {results['final_shares']:.2f}")
    print(f"Final portfolio value: ${results['final_portfolio_value']:.2f}")
    print(f"Total return: {results['total_return']:.2f}%")
    
    # Show trades
    if results['trades']:
        print(f"\nTrades executed:")
        for trade in results['trades']:
            print(f"  {trade['date']}: {trade['action'].upper()} {trade['shares']:.2f} shares at ${trade['price']:.2f}")
    
    # Show signals for reference
    signals_df = pd.DataFrame(results.get('signals', []))
    if not signals_df.empty:
        buy_signals = signals_df[signals_df['buy_signal'] == 1]
        sell_signals = signals_df[signals_df['sell_signal'] == 1]
        print(f"\nSignal counts:")
        print(f"  Buy signals: {len(buy_signals)}")
        print(f"  Sell signals: {len(sell_signals)}")
    
    if not signals_df.empty and len(buy_signals) > 0:
        print(f"\nFirst buy signal:")
        print(buy_signals[['date', 'close', 'fast_ma', 'slow_ma']].iloc[0])
    
    if not signals_df.empty and len(sell_signals) > 0:
        print(f"\nFirst sell signal:")
        print(sell_signals[['date', 'close', 'fast_ma', 'slow_ma']].iloc[0])
    
    if not signals_df.empty:
        print(f"\nSample of data with signals:")
        print(signals_df[['date', 'close', 'fast_ma', 'slow_ma', 'buy_signal', 'sell_signal']].head(10))
    
    return results

def save_sample_data_to_cache():
    """Save sample data to cache for API testing"""
    print("\n" + "="*50)
    print("SAVING SAMPLE DATA TO CACHE")
    print("="*50)
    
    # Create cache directory
    os.makedirs('cache', exist_ok=True)
    
    # Create sample data
    data = create_sample_data()
    
    # Save to cache
    cache_file = 'cache/AAPL_1y.parquet'
    data.to_parquet(cache_file)
    print(f"Saved sample data to {cache_file}")
    
    # Verify it was saved
    if os.path.exists(cache_file):
        print("✅ Cache file created successfully")
        cached_data = pd.read_parquet(cache_file)
        print(f"✅ Cached data shape: {cached_data.shape}")
    else:
        print("❌ Failed to create cache file")

if __name__ == "__main__":
    print("MA CROSSOVER STRATEGY TEST")
    print("="*50)
    
    try:
        # Test the strategy
        results = test_ma_strategy()
        
        # Save sample data to cache
        save_sample_data_to_cache()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("\nNext steps:")
        print("1. Start your API server: python -m src.api.server")
        print("2. Test the API: curl -X POST 'http://localhost:8000/backtest' -H 'Content-Type: application/json' -d '{\"symbol\": \"AAPL\", \"period\": \"1y\"}'")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
