"""
Optimization Module for SPX Trading System
Finds optimal parameter combinations through backtesting
"""
import os
import sys
import pandas as pd
import numpy as np
from itertools import product
from typing import Dict, List, Tuple, Optional
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from tqdm import tqdm
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import INDICATOR_PARAMS, BACKTEST_CONFIG
from src.data_handler import DataHandler
from src.indicators import TechnicalIndicators
from src.strategy import TradingStrategy
from src.backtest import Backtester

logger = logging.getLogger(__name__)


class StrategyOptimizer:
    """
    Optimizes trading strategy parameters through systematic backtesting
    """
    
    def __init__(self, data: pd.DataFrame, optimization_metric: str = BACKTEST_CONFIG['optimization_metric']):
        self.data = data
        self.optimization_metric = optimization_metric
        self.results = []
        self.best_params = None
        self.best_score = -np.inf
        
    def generate_parameter_combinations(self, param_ranges: Dict) -> List[Dict]:
        """
        Generate all possible parameter combinations
        
        Args:
            param_ranges: Dictionary with parameter ranges
            
        Returns:
            List of parameter combination dictionaries
        """
        combinations = []
        
        # Extract all parameter options
        param_keys = []
        param_values = []
        
        for indicator, params in param_ranges.items():
            for param_name, values in params.items():
                param_keys.append(f"{indicator}.{param_name}")
                param_values.append(values)
        
        # Generate all combinations
        for combo in product(*param_values):
            param_dict = {}
            for key, value in zip(param_keys, combo):
                indicator, param = key.split('.')
                if indicator not in param_dict:
                    param_dict[indicator] = {}
                param_dict[indicator][param] = [value] if not isinstance(value, list) else value
            
            combinations.append(param_dict)
        
        return combinations
    
    def optimize_single_indicator(self, indicator_name: str, param_ranges: Dict) -> Dict:
        """
        Optimize parameters for a single indicator
        
        Args:
            indicator_name: Name of the indicator to optimize
            param_ranges: Parameter ranges for the indicator
            
        Returns:
            Best parameters and results
        """
        logger.info(f"Optimizing {indicator_name} indicator...")
        
        # Generate combinations for single indicator
        single_indicator_params = {indicator_name: param_ranges}
        combinations = self.generate_parameter_combinations(single_indicator_params)
        
        best_result = None
        best_score = -np.inf
        
        for params in tqdm(combinations, desc=f"Testing {indicator_name}"):
            result = self._run_single_backtest(params)
            
            if result and result['score'] > best_score:
                best_score = result['score']
                best_result = result
        
        return best_result
    
    def optimize_indicator_combination(self, indicators: List[str], 
                                     param_ranges: Dict = None) -> Dict:
        """
        Optimize parameters for a combination of indicators
        
        Args:
            indicators: List of indicator names to combine
            param_ranges: Optional custom parameter ranges
            
        Returns:
            Best parameters and results
        """
        if param_ranges is None:
            param_ranges = {ind: INDICATOR_PARAMS[ind] for ind in indicators if ind in INDICATOR_PARAMS}
        
        logger.info(f"Optimizing combination: {', '.join(indicators)}")
        
        combinations = self.generate_parameter_combinations(param_ranges)
        logger.info(f"Testing {len(combinations)} parameter combinations...")
        
        # Use multiprocessing for faster optimization
        results = []
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = {
                executor.submit(self._run_single_backtest, params): params 
                for params in combinations
            }
            
            for future in tqdm(as_completed(futures), total=len(futures), 
                              desc="Optimizing"):
                result = future.result()
                if result:
                    results.append(result)
        
        # Find best result
        if results:
            best_result = max(results, key=lambda x: x['score'])
            return best_result
        else:
            return None
    
    def _run_single_backtest(self, params: Dict) -> Optional[Dict]:
        """
        Run a single backtest with given parameters
        
        Args:
            params: Parameter dictionary
            
        Returns:
            Results dictionary or None if failed
        """
        try:
            # Initialize components
            indicators = TechnicalIndicators()
            strategy = TradingStrategy()
            backtester = Backtester(strategy)
            
            # Calculate indicators
            data_with_indicators = indicators.calculate_all_indicators(self.data.copy(), params)
            
            # Run backtest
            results = backtester.run_backtest(data_with_indicators, params)
            
            # Extract optimization metric
            metrics = results['metrics']
            score = metrics.get(self.optimization_metric, 0)
            
            # Apply penalties for not meeting minimum requirements
            if metrics['total_trades'] < BACKTEST_CONFIG['min_trades']:
                score *= 0.5  # Penalize strategies with too few trades
            
            if metrics['max_drawdown'] > 0.3:  # Penalize excessive drawdown
                score *= 0.7
            
            return {
                'params': params,
                'metrics': metrics,
                'score': score,
                'trades': len(results['trades'])
            }
            
        except Exception as e:
            logger.error(f"Backtest failed for params {params}: {e}")
            return None
    
    def find_best_indicators(self) -> Dict:
        """
        Find the best performing indicators and their optimal parameters
        """
        all_results = {}
        
        # Test each indicator individually
        logger.info("Testing individual indicators...")
        for indicator in INDICATOR_PARAMS.keys():
            result = self.optimize_single_indicator(indicator, INDICATOR_PARAMS[indicator])
            if result:
                all_results[indicator] = result
        
        # Test common indicator combinations
        logger.info("Testing indicator combinations...")
        combinations_to_test = [
            ['RSI', 'MACD'],
            ['RSI', 'Bollinger_Bands'],
            ['MACD', 'EMA'],
            ['RSI', 'MACD', 'Bollinger_Bands'],
            ['EMA', 'Bollinger_Bands', 'ATR'],
            ['RSI', 'MACD', 'EMA', 'ATR']
        ]
        
        for combo in combinations_to_test:
            # Filter to only available indicators
            available_combo = [ind for ind in combo if ind in INDICATOR_PARAMS]
            if len(available_combo) >= 2:
                result = self.optimize_indicator_combination(available_combo)
                if result:
                    combo_name = '+'.join(available_combo)
                    all_results[combo_name] = result
        
        # Find overall best
        if all_results:
            best_name = max(all_results.keys(), key=lambda k: all_results[k]['score'])
            self.best_params = all_results[best_name]['params']
            self.best_score = all_results[best_name]['score']
            
            return {
                'best_indicator_set': best_name,
                'best_params': self.best_params,
                'best_score': self.best_score,
                'best_metrics': all_results[best_name]['metrics'],
                'all_results': all_results
            }
        else:
            return None
    
    def walk_forward_optimization(self, window_size: int = 252*2, 
                                test_size: int = 252//2) -> List[Dict]:
        """
        Perform walk-forward optimization
        
        Args:
            window_size: Training window size in days
            test_size: Test window size in days
            
        Returns:
            List of optimization results for each window
        """
        results = []
        data_length = len(self.data)
        
        # Calculate number of windows
        num_windows = (data_length - window_size) // test_size
        
        logger.info(f"Performing walk-forward optimization with {num_windows} windows...")
        
        for i in range(num_windows):
            # Define train and test periods
            train_start = i * test_size
            train_end = train_start + window_size
            test_start = train_end
            test_end = min(test_start + test_size, data_length)
            
            # Split data
            train_data = self.data.iloc[train_start:train_end]
            test_data = self.data.iloc[test_start:test_end]
            
            # Optimize on training data
            train_optimizer = StrategyOptimizer(train_data, self.optimization_metric)
            train_results = train_optimizer.find_best_indicators()
            
            if train_results:
                # Test on out-of-sample data
                test_result = self._run_single_backtest_on_data(
                    test_data, 
                    train_results['best_params']
                )
                
                if test_result:
                    results.append({
                        'window': i + 1,
                        'train_period': f"{train_data.index[0]} to {train_data.index[-1]}",
                        'test_period': f"{test_data.index[0]} to {test_data.index[-1]}",
                        'best_params': train_results['best_params'],
                        'train_score': train_results['best_score'],
                        'test_score': test_result['score'],
                        'test_metrics': test_result['metrics']
                    })
        
        return results
    
    def _run_single_backtest_on_data(self, data: pd.DataFrame, params: Dict) -> Optional[Dict]:
        """
        Run backtest on specific data
        """
        try:
            indicators = TechnicalIndicators()
            strategy = TradingStrategy()
            backtester = Backtester(strategy)
            
            data_with_indicators = indicators.calculate_all_indicators(data.copy(), params)
            results = backtester.run_backtest(data_with_indicators, params)
            
            metrics = results['metrics']
            score = metrics.get(self.optimization_metric, 0)
            
            return {
                'params': params,
                'metrics': metrics,
                'score': score
            }
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            return None
    
    def save_results(self, filepath: str):
        """
        Save optimization results
        """
        results_dict = {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'optimization_metric': self.optimization_metric,
            'results': self.results
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_dict, f, indent=4, default=str)
        
        logger.info(f"Results saved to {filepath}")
    
    def generate_optimization_report(self) -> str:
        """
        Generate a text report of optimization results
        """
        report = []
        report.append("="*80)
        report.append("PARAMETER OPTIMIZATION REPORT")
        report.append("="*80)
        report.append(f"Optimization Metric: {self.optimization_metric}")
        report.append(f"Best Score: {self.best_score:.4f}")
        report.append("")
        
        if self.best_params:
            report.append("BEST PARAMETERS:")
            report.append("-"*80)
            for indicator, params in self.best_params.items():
                report.append(f"\n{indicator}:")
                for param, value in params.items():
                    report.append(f"  {param}: {value}")
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    # Load sample data
    data_handler = DataHandler()
    data = data_handler.fetch_data(
        interval='5m',
        start_date='2024-01-01',
        end_date='2024-02-29'
    )
    
    # Initialize optimizer
    optimizer = StrategyOptimizer(data)
    
    # Run optimization
    print("Starting optimization...")
    results = optimizer.find_best_indicators()
    
    if results:
        print("\nOptimization Results:")
        print(f"Best Indicator Set: {results['best_indicator_set']}")
        print(f"Best Score: {results['best_score']:.4f}")
        print("\nBest Parameters:")
        for indicator, params in results['best_params'].items():
            print(f"{indicator}: {params}")
        
        print("\nBest Metrics:")
        metrics = results['best_metrics']
        print(f"Annual Return: {metrics['annual_return']:.2%}")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Win Rate: {metrics['win_rate']:.2%}")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")