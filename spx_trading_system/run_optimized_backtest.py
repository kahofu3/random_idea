"""
Optimized SPX Trading System - Enhanced Backtest
Test with optimized parameters and longer data periods
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import json

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import TRADING_CONFIG, INDICATOR_PARAMS, PERFORMANCE_TARGETS
from src.data_handler import DataHandler
from src.indicators_simple import TechnicalIndicators
from src.strategy import TradingStrategy
from src.backtest import Backtester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_optimized_test(params_subset: dict, timeframe: str = '10m', 
                      days_back: int = 60, min_confirmations: int = 1) -> dict:
    """
    Run a backtest with optimized parameters
    
    Args:
        params_subset: Indicator parameters to test
        timeframe: Trading timeframe
        days_back: Number of days to test
        min_confirmations: Minimum indicator confirmations required
        
    Returns:
        Results dictionary
    """
    try:
        # Calculate date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - pd.Timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        logger.info(f"Testing strategy from {start_date} to {end_date}")
        
        # Initialize components
        data_handler = DataHandler()
        indicators = TechnicalIndicators()
        strategy = TradingStrategy()
        backtester = Backtester(strategy)
        
        # Fetch data
        data = data_handler.fetch_data(
            interval=timeframe,
            start_date=start_date,
            end_date=end_date
        )
        
        if len(data) < 100:
            logger.warning("Insufficient data points")
            return None
            
        # Calculate indicators
        data_with_indicators = indicators.calculate_all_indicators(data, params_subset)
        
        # Temporarily modify strategy to use different min_confirmations
        original_combine = strategy._combine_signals
        
        def modified_combine(df):
            # Get all long signal columns
            long_signal_cols = [col for col in df.columns if col.endswith('_long')]
            short_signal_cols = [col for col in df.columns if col.endswith('_short')]
            
            # Calculate signal strength
            df['long_strength'] = df[long_signal_cols].sum(axis=1) if long_signal_cols else 0
            df['short_strength'] = df[short_signal_cols].sum(axis=1) if short_signal_cols else 0
            
            # Use custom min_confirmations
            df['long_signal'] = (df['long_strength'] >= min_confirmations).astype(int)
            df['short_signal'] = (df['short_strength'] >= min_confirmations).astype(int)
            
            # Ensure no conflicting signals
            conflict_mask = (df['long_signal'] == 1) & (df['short_signal'] == 1)
            df.loc[conflict_mask, 'long_signal'] = 0
            df.loc[conflict_mask, 'short_signal'] = 0
            
            return df
        
        strategy._combine_signals = modified_combine
        
        # Run backtest
        results = backtester.run_backtest(data_with_indicators, params_subset)
        
        # Restore original method
        strategy._combine_signals = original_combine
        
        return results
        
    except Exception as e:
        import traceback
        logger.error(f"Strategy test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def test_optimized_strategies():
    """
    Test optimized strategy configurations
    """
    logger.info("Starting optimized strategy testing...")
    
    # Define optimized strategies based on initial results
    strategies = [
        {
            'name': 'Optimized_RSI',
            'params': {
                'RSI': {'periods': [9, 14], 'oversold': [25, 30], 'overbought': [70, 75]}
            },
            'min_confirmations': 1,
            'timeframe': '10m'
        },
        {
            'name': 'Optimized_MACD',
            'params': {
                'MACD': {'fast': [8, 12], 'slow': [21, 26], 'signal': [5, 9]}
            },
            'min_confirmations': 1,
            'timeframe': '10m'
        },
        {
            'name': 'Fast_EMA_Cross',
            'params': {
                'EMA': {'short_periods': [5, 10], 'long_periods': [20, 30]}
            },
            'min_confirmations': 1,
            'timeframe': '5m'
        },
        {
            'name': 'Tight_Bollinger',
            'params': {
                'Bollinger_Bands': {'periods': [20], 'std_dev': [1.5, 2]},
                'RSI': {'periods': [14], 'oversold': [30], 'overbought': [70]}
            },
            'min_confirmations': 1,
            'timeframe': '10m'
        },
        {
            'name': 'Triple_Optimized',
            'params': {
                'RSI': {'periods': [9], 'oversold': [25], 'overbought': [75]},
                'MACD': {'fast': [8], 'slow': [21], 'signal': [5]},
                'EMA': {'short_periods': [5], 'long_periods': [20]}
            },
            'min_confirmations': 1,
            'timeframe': '5m'
        },
        {
            'name': 'Momentum_Strategy',
            'params': {
                'RSI': {'periods': [14], 'oversold': [35], 'overbought': [65]},
                'MACD': {'fast': [12], 'slow': [26], 'signal': [9]},
                'ATR': {'periods': [14]}
            },
            'min_confirmations': 2,
            'timeframe': '10m'
        },
        {
            'name': 'Volatility_Breakout',
            'params': {
                'Bollinger_Bands': {'periods': [20], 'std_dev': [2, 2.5]},
                'ATR': {'periods': [14, 20]},
                'EMA': {'short_periods': [10], 'long_periods': [30]}
            },
            'min_confirmations': 1,
            'timeframe': '10m'
        },
        {
            'name': 'Mean_Reversion',
            'params': {
                'RSI': {'periods': [7, 14], 'oversold': [20, 25], 'overbought': [75, 80]},
                'Bollinger_Bands': {'periods': [20], 'std_dev': [2.5]}
            },
            'min_confirmations': 1,
            'timeframe': '5m'
        }
    ]
    
    # Test each strategy
    results_summary = []
    best_overall = None
    best_score = -float('inf')
    
    for strategy in strategies:
        logger.info(f"\nTesting strategy: {strategy['name']}")
        logger.info(f"Parameters: {strategy['params']}")
        logger.info(f"Min confirmations: {strategy['min_confirmations']}")
        
        results = run_optimized_test(
            strategy['params'],
            timeframe=strategy['timeframe'],
            days_back=60,  # Use 60 days for more data
            min_confirmations=strategy['min_confirmations']
        )
        
        if results and results['metrics']:
            metrics = results['metrics']
            
            # Calculate composite score for ranking
            score = (
                metrics['sharpe_ratio'] * 0.3 +
                (metrics['annual_return'] * 10) * 0.3 +  # Scale to similar range
                metrics['win_rate'] * 0.2 +
                (1 - metrics['max_drawdown']) * 0.2
            )
            
            summary = {
                'strategy_name': strategy['name'],
                'timeframe': strategy['timeframe'],
                'total_trades': metrics['total_trades'],
                'win_rate': metrics['win_rate'],
                'profit_factor': metrics['profit_factor'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'max_drawdown': metrics['max_drawdown'],
                'annual_return': metrics['annual_return'],
                'total_pnl': metrics['total_pnl'],
                'expected_value': metrics['expected_value'],
                'composite_score': score,
                'meets_targets': all([
                    metrics['meets_win_rate_target'],
                    metrics['meets_profit_factor_target'],
                    metrics['meets_sharpe_target'],
                    metrics['meets_return_target'],
                    metrics['meets_drawdown_target']
                ])
            }
            
            results_summary.append(summary)
            
            if score > best_score:
                best_score = score
                best_overall = summary
            
            # Print results
            print(f"\n{'='*60}")
            print(f"Strategy: {strategy['name']} ({strategy['timeframe']})")
            print(f"{'='*60}")
            print(f"Total Trades: {metrics['total_trades']}")
            print(f"Win Rate: {metrics['win_rate']:.2%}")
            print(f"Profit Factor: {metrics['profit_factor']:.2f}")
            print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
            print(f"Annual Return: {metrics['annual_return']:.2%}")
            print(f"Total P&L: ${metrics['total_pnl']:,.2f}")
            print(f"Expected Value: ${metrics['expected_value']:.2f}")
            print(f"Composite Score: {score:.3f}")
            print(f"Meets All Targets: {'YES' if summary['meets_targets'] else 'NO'}")
            
    # Find best strategies by different criteria
    if results_summary:
        # Sort by different metrics
        best_by_score = max(results_summary, key=lambda x: x['composite_score'])
        best_by_sharpe = max(results_summary, key=lambda x: x['sharpe_ratio'])
        best_by_return = max(results_summary, key=lambda x: x['annual_return'])
        best_by_win_rate = max(results_summary, key=lambda x: x['win_rate'])
        best_by_trades = max(results_summary, key=lambda x: x['total_trades'])
        
        print(f"\n{'='*80}")
        print("OPTIMIZATION SUMMARY")
        print(f"{'='*80}")
        print(f"\nBest Overall (Composite Score): {best_by_score['strategy_name']} (Score: {best_by_score['composite_score']:.3f})")
        print(f"Best by Sharpe Ratio: {best_by_sharpe['strategy_name']} ({best_by_sharpe['sharpe_ratio']:.2f})")
        print(f"Best by Annual Return: {best_by_return['strategy_name']} ({best_by_return['annual_return']:.2%})")
        print(f"Best by Win Rate: {best_by_win_rate['strategy_name']} ({best_by_win_rate['win_rate']:.2%})")
        print(f"Most Active (Trades): {best_by_trades['strategy_name']} ({best_by_trades['total_trades']} trades)")
        
        # Show top 3 strategies
        sorted_strategies = sorted(results_summary, key=lambda x: x['composite_score'], reverse=True)
        print(f"\nTop 3 Strategies by Composite Score:")
        for i, s in enumerate(sorted_strategies[:3], 1):
            print(f"{i}. {s['strategy_name']}: Return={s['annual_return']:.2%}, "
                  f"Sharpe={s['sharpe_ratio']:.2f}, Win Rate={s['win_rate']:.2%}, "
                  f"Score={s['composite_score']:.3f}")
        
        # Save results
        with open('optimized_backtest_results.json', 'w') as f:
            json.dump({
                'summary': results_summary,
                'best_overall': best_overall,
                'test_parameters': {
                    'days_back': 60,
                    'data_points': 'varies by strategy'
                }
            }, f, indent=4)
        print(f"\nDetailed results saved to optimized_backtest_results.json")
        
        # Show successful strategies
        successful_strategies = [s for s in results_summary if s['meets_targets']]
        if successful_strategies:
            print(f"\nStrategies meeting ALL performance targets:")
            for s in successful_strategies:
                print(f"✓ {s['strategy_name']} ({s['timeframe']}): "
                      f"Return={s['annual_return']:.2%}, Sharpe={s['sharpe_ratio']:.2f}")
        else:
            print(f"\nNote: No strategies met all performance targets with current market conditions.")
            print("Consider adjusting targets or testing with different market periods.")


if __name__ == "__main__":
    print("SPX Trading System - Optimized Strategy Testing")
    print("="*80)
    print("Testing with 60 days of data and optimized parameters...")
    print()
    
    test_optimized_strategies()