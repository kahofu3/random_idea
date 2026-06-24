"""
Simplified SPX Trading System - Backtest Runner
Run backtests with simplified indicators (no TA-Lib required)
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
from src.indicators_simple import TechnicalIndicators  # Use simplified version
from src.strategy import TradingStrategy
from src.backtest import Backtester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_single_strategy_test(params_subset: dict, timeframe: str = '5m', 
                           days_back: int = 30) -> dict:
    """
    Run a backtest with a specific set of parameters
    
    Args:
        params_subset: Indicator parameters to test
        timeframe: Trading timeframe
        days_back: Number of days to test
        
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
            interval=timeframe,  # Use timeframe directly
            start_date=start_date,
            end_date=end_date
        )
        
        if len(data) < 100:
            logger.warning("Insufficient data points")
            return None
            
        # Calculate indicators
        data_with_indicators = indicators.calculate_all_indicators(data, params_subset)
        
        # Run backtest
        results = backtester.run_backtest(data_with_indicators, params_subset)
        
        return results
        
    except Exception as e:
        import traceback
        logger.error(f"Strategy test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def test_multiple_strategies():
    """
    Test multiple indicator combinations to find the best strategy
    """
    logger.info("Starting strategy optimization...")
    
    # Define strategies to test
    strategies = [
        {
            'name': 'RSI_Only',
            'params': {
                'RSI': {'periods': [14], 'oversold': [30], 'overbought': [70]}
            }
        },
        {
            'name': 'MACD_Only',
            'params': {
                'MACD': {'fast': [12], 'slow': [26], 'signal': [9]}
            }
        },
        {
            'name': 'EMA_Crossover',
            'params': {
                'EMA': {'short_periods': [10], 'long_periods': [50]}
            }
        },
        {
            'name': 'Bollinger_Bands',
            'params': {
                'Bollinger_Bands': {'periods': [20], 'std_dev': [2]}
            }
        },
        {
            'name': 'RSI_MACD_Combo',
            'params': {
                'RSI': {'periods': [14], 'oversold': [30], 'overbought': [70]},
                'MACD': {'fast': [12], 'slow': [26], 'signal': [9]}
            }
        },
        {
            'name': 'RSI_BB_Combo',
            'params': {
                'RSI': {'periods': [14], 'oversold': [30], 'overbought': [70]},
                'Bollinger_Bands': {'periods': [20], 'std_dev': [2]}
            }
        },
        {
            'name': 'Triple_Combo',
            'params': {
                'RSI': {'periods': [14], 'oversold': [30], 'overbought': [70]},
                'MACD': {'fast': [12], 'slow': [26], 'signal': [9]},
                'EMA': {'short_periods': [10], 'long_periods': [50]}
            }
        },
        {
            'name': 'All_Indicators',
            'params': {
                'RSI': {'periods': [14], 'oversold': [30], 'overbought': [70]},
                'MACD': {'fast': [12], 'slow': [26], 'signal': [9]},
                'EMA': {'short_periods': [20], 'long_periods': [50]},
                'Bollinger_Bands': {'periods': [20], 'std_dev': [2]},
                'ATR': {'periods': [14]}
            }
        }
    ]
    
    # Test each strategy
    results_summary = []
    
    for strategy in strategies:
        logger.info(f"\nTesting strategy: {strategy['name']}")
        logger.info(f"Parameters: {strategy['params']}")
        
        results = run_single_strategy_test(strategy['params'])
        
        if results and results['metrics']:
            metrics = results['metrics']
            
            summary = {
                'strategy_name': strategy['name'],
                'total_trades': metrics['total_trades'],
                'win_rate': metrics['win_rate'],
                'profit_factor': metrics['profit_factor'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'max_drawdown': metrics['max_drawdown'],
                'annual_return': metrics['annual_return'],
                'total_pnl': metrics['total_pnl'],
                'expected_value': metrics['expected_value'],
                'meets_targets': all([
                    metrics['meets_win_rate_target'],
                    metrics['meets_profit_factor_target'],
                    metrics['meets_sharpe_target'],
                    metrics['meets_return_target'],
                    metrics['meets_drawdown_target']
                ])
            }
            
            results_summary.append(summary)
            
            # Print results
            print(f"\n{'='*60}")
            print(f"Strategy: {strategy['name']}")
            print(f"{'='*60}")
            print(f"Total Trades: {metrics['total_trades']}")
            print(f"Win Rate: {metrics['win_rate']:.2%}")
            print(f"Profit Factor: {metrics['profit_factor']:.2f}")
            print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
            print(f"Annual Return: {metrics['annual_return']:.2%}")
            print(f"Total P&L: ${metrics['total_pnl']:,.2f}")
            print(f"Expected Value: ${metrics['expected_value']:.2f}")
            print(f"Meets All Targets: {'YES' if summary['meets_targets'] else 'NO'}")
            
    # Find best strategy
    if results_summary:
        # Sort by multiple criteria
        best_by_sharpe = max(results_summary, key=lambda x: x['sharpe_ratio'])
        best_by_return = max(results_summary, key=lambda x: x['annual_return'])
        best_by_win_rate = max(results_summary, key=lambda x: x['win_rate'])
        
        print(f"\n{'='*80}")
        print("OPTIMIZATION SUMMARY")
        print(f"{'='*80}")
        print(f"\nBest by Sharpe Ratio: {best_by_sharpe['strategy_name']} ({best_by_sharpe['sharpe_ratio']:.2f})")
        print(f"Best by Annual Return: {best_by_return['strategy_name']} ({best_by_return['annual_return']:.2%})")
        print(f"Best by Win Rate: {best_by_win_rate['strategy_name']} ({best_by_win_rate['win_rate']:.2%})")
        
        # Save results
        with open('backtest_results.json', 'w') as f:
            json.dump(results_summary, f, indent=4)
        print(f"\nResults saved to backtest_results.json")
        
        # Show strategies that meet all targets
        successful_strategies = [s for s in results_summary if s['meets_targets']]
        if successful_strategies:
            print(f"\nStrategies meeting ALL performance targets:")
            for s in successful_strategies:
                print(f"- {s['strategy_name']}: Return={s['annual_return']:.2%}, Sharpe={s['sharpe_ratio']:.2f}")
        else:
            print(f"\nNo strategies met all performance targets.")


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("SPX Trading System - Strategy Optimization")
    print("="*80)
    
    test_multiple_strategies()