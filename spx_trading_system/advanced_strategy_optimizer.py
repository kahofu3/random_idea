"""
Advanced Strategy Optimizer for SPX Trading
Tests multiple strategy types to find the best performer
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import json
from concurrent.futures import ProcessPoolExecutor
import itertools

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_handler import DataHandler
from src.indicators_simple import TechnicalIndicators
from src.backtest import Backtester

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedStrategy:
    """Base class for advanced trading strategies"""
    
    def __init__(self, params: Dict):
        self.params = params
        self.indicators = TechnicalIndicators()
        
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Must be implemented by each strategy"""
        raise NotImplementedError


class MeanReversionStrategy(AdvancedStrategy):
    """Mean reversion using Bollinger Bands and RSI"""
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Add Bollinger Bands
        bb_period = self.params.get('bb_period', 20)
        bb_std = self.params.get('bb_std', 2)
        data = self.indicators.add_bollinger_bands(data, bb_period, bb_std)
        
        # Add RSI
        rsi_period = self.params.get('rsi_period', 14)
        data = self.indicators.add_rsi(data, rsi_period)
        
        # Mean reversion signals
        bb_col = f'BB_{bb_period}_{bb_std}'
        rsi_col = f'RSI_{rsi_period}'
        
        # Buy when price touches lower band and RSI oversold
        data['buy_signal'] = (
            (data['Close'] <= data[f'{bb_col}_lower']) & 
            (data[rsi_col] < self.params.get('rsi_oversold', 30))
        ).astype(int)
        
        # Sell when price touches upper band and RSI overbought
        data['sell_signal'] = (
            (data['Close'] >= data[f'{bb_col}_upper']) & 
            (data[rsi_col] > self.params.get('rsi_overbought', 70))
        ).astype(int)
        
        return data


class MomentumBreakoutStrategy(AdvancedStrategy):
    """Momentum breakout using price channels and volume"""
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calculate price channels
        channel_period = self.params.get('channel_period', 20)
        data['high_channel'] = data['High'].rolling(channel_period).max()
        data['low_channel'] = data['Low'].rolling(channel_period).min()
        
        # Volume analysis
        data['volume_sma'] = data['Volume'].rolling(20).mean()
        data['volume_ratio'] = data['Volume'] / data['volume_sma']
        
        # Add ADX for trend strength
        data = self._add_adx(data, self.params.get('adx_period', 14))
        
        # Breakout signals with volume confirmation
        min_volume_ratio = self.params.get('min_volume_ratio', 1.5)
        min_adx = self.params.get('min_adx', 25)
        
        data['buy_signal'] = (
            (data['Close'] > data['high_channel'].shift(1)) & 
            (data['volume_ratio'] > min_volume_ratio) &
            (data['ADX'] > min_adx)
        ).astype(int)
        
        data['sell_signal'] = (
            (data['Close'] < data['low_channel'].shift(1)) & 
            (data['volume_ratio'] > min_volume_ratio) &
            (data['ADX'] > min_adx)
        ).astype(int)
        
        return data
    
    def _add_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Average Directional Index"""
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        # Directional movements
        up_move = df['High'] - df['High'].shift()
        down_move = df['Low'].shift() - df['Low']
        
        pos_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0), index=df.index)
        neg_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0), index=df.index)
        
        pos_di = 100 * (pos_dm.rolling(period).mean() / atr)
        neg_di = 100 * (neg_dm.rolling(period).mean() / atr)
        
        dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di)
        adx = dx.rolling(period).mean()
        
        df['ADX'] = adx
        df['+DI'] = pos_di
        df['-DI'] = neg_di
        
        return df


class VWAPReversionStrategy(AdvancedStrategy):
    """VWAP reversion with volume profile"""
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calculate VWAP
        data['typical_price'] = (data['High'] + data['Low'] + data['Close']) / 3
        data['price_volume'] = data['typical_price'] * data['Volume']
        
        # Reset VWAP daily (simplified - in reality would reset at market open)
        data['cumulative_volume'] = data['Volume'].cumsum()
        data['cumulative_pv'] = data['price_volume'].cumsum()
        data['VWAP'] = data['cumulative_pv'] / data['cumulative_volume']
        
        # Standard deviation bands
        vwap_std = self.params.get('vwap_std', 2)
        data['vwap_std'] = ((data['typical_price'] - data['VWAP']) ** 2).rolling(20).mean() ** 0.5
        data['vwap_upper'] = data['VWAP'] + (vwap_std * data['vwap_std'])
        data['vwap_lower'] = data['VWAP'] - (vwap_std * data['vwap_std'])
        
        # Add RSI for confirmation
        data = self.indicators.add_rsi(data, self.params.get('rsi_period', 9))
        rsi_col = f"RSI_{self.params.get('rsi_period', 9)}"
        
        # Reversion signals
        data['buy_signal'] = (
            (data['Close'] < data['vwap_lower']) & 
            (data[rsi_col] < self.params.get('rsi_oversold', 30))
        ).astype(int)
        
        data['sell_signal'] = (
            (data['Close'] > data['vwap_upper']) & 
            (data[rsi_col] > self.params.get('rsi_overbought', 70))
        ).astype(int)
        
        return data


class SupertrendStrategy(AdvancedStrategy):
    """Supertrend indicator strategy"""
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calculate Supertrend
        period = self.params.get('supertrend_period', 10)
        multiplier = self.params.get('supertrend_multiplier', 3)
        
        # ATR
        data = self.indicators.add_atr(data, period)
        atr_col = f'ATR_{period}'
        
        # Basic bands
        hl_avg = (data['High'] + data['Low']) / 2
        data['basic_upper'] = hl_avg + multiplier * data[atr_col]
        data['basic_lower'] = hl_avg - multiplier * data[atr_col]
        
        # Final bands
        data['final_upper'] = data['basic_upper']
        data['final_lower'] = data['basic_lower']
        
        # Supertrend calculation
        data['supertrend'] = 0
        data['trend'] = 1  # 1 for uptrend, -1 for downtrend
        
        for i in range(1, len(data)):
            if data['Close'].iloc[i] <= data['final_upper'].iloc[i]:
                data.loc[data.index[i], 'supertrend'] = data['final_upper'].iloc[i]
            else:
                data.loc[data.index[i], 'supertrend'] = data['final_lower'].iloc[i]
            
            # Determine trend
            if data['supertrend'].iloc[i] == data['final_upper'].iloc[i]:
                data.loc[data.index[i], 'trend'] = -1
            else:
                data.loc[data.index[i], 'trend'] = 1
        
        # Generate signals on trend change
        data['buy_signal'] = ((data['trend'] == 1) & (data['trend'].shift(1) == -1)).astype(int)
        data['sell_signal'] = ((data['trend'] == -1) & (data['trend'].shift(1) == 1)).astype(int)
        
        return data


class ScalpingStrategy(AdvancedStrategy):
    """High-frequency scalping using EMA crosses and momentum"""
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Fast EMAs for scalping
        ema_fast = self.params.get('ema_fast', 3)
        ema_slow = self.params.get('ema_slow', 8)
        
        data = self.indicators.add_ema(data, ema_fast, f'EMA_{ema_fast}')
        data = self.indicators.add_ema(data, ema_slow, f'EMA_{ema_slow}')
        
        # Momentum indicator
        momentum_period = self.params.get('momentum_period', 5)
        data['momentum'] = data['Close'] - data['Close'].shift(momentum_period)
        data['momentum_sma'] = data['momentum'].rolling(momentum_period).mean()
        
        # Scalping signals
        data['buy_signal'] = (
            (data[f'EMA_{ema_fast}'] > data[f'EMA_{ema_slow}']) & 
            (data[f'EMA_{ema_fast}'].shift(1) <= data[f'EMA_{ema_slow}'].shift(1)) &
            (data['momentum'] > data['momentum_sma'])
        ).astype(int)
        
        data['sell_signal'] = (
            (data[f'EMA_{ema_fast}'] < data[f'EMA_{ema_slow}']) & 
            (data[f'EMA_{ema_fast}'].shift(1) >= data[f'EMA_{ema_slow}'].shift(1)) &
            (data['momentum'] < data['momentum_sma'])
        ).astype(int)
        
        return data


class SupportResistanceStrategy(AdvancedStrategy):
    """Support and resistance breakout strategy"""
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calculate pivot points
        data['pivot'] = (data['High'].shift(1) + data['Low'].shift(1) + data['Close'].shift(1)) / 3
        data['r1'] = 2 * data['pivot'] - data['Low'].shift(1)
        data['s1'] = 2 * data['pivot'] - data['High'].shift(1)
        data['r2'] = data['pivot'] + (data['High'].shift(1) - data['Low'].shift(1))
        data['s2'] = data['pivot'] - (data['High'].shift(1) - data['Low'].shift(1))
        
        # Recent highs and lows for dynamic S/R
        lookback = self.params.get('sr_lookback', 20)
        data['recent_high'] = data['High'].rolling(lookback).max()
        data['recent_low'] = data['Low'].rolling(lookback).min()
        
        # Volume for confirmation
        data['volume_sma'] = data['Volume'].rolling(20).mean()
        volume_threshold = self.params.get('volume_threshold', 1.2)
        
        # Breakout signals
        data['buy_signal'] = (
            ((data['Close'] > data['r1']) | (data['Close'] > data['recent_high'].shift(1))) &
            (data['Volume'] > data['volume_sma'] * volume_threshold)
        ).astype(int)
        
        data['sell_signal'] = (
            ((data['Close'] < data['s1']) | (data['Close'] < data['recent_low'].shift(1))) &
            (data['Volume'] > data['volume_sma'] * volume_threshold)
        ).astype(int)
        
        return data


class AdvancedOptimizer:
    """Optimizer for testing multiple strategies"""
    
    def __init__(self):
        self.data_handler = DataHandler()
        self.strategies = {
            'mean_reversion': MeanReversionStrategy,
            'momentum_breakout': MomentumBreakoutStrategy,
            'vwap_reversion': VWAPReversionStrategy,
            'supertrend': SupertrendStrategy,
            'scalping': ScalpingStrategy,
            'support_resistance': SupportResistanceStrategy
        }
        
        # Parameter ranges for each strategy
        self.parameter_ranges = {
            'mean_reversion': {
                'bb_period': [15, 20, 25],
                'bb_std': [1.5, 2, 2.5],
                'rsi_period': [9, 14],
                'rsi_oversold': [20, 25, 30],
                'rsi_overbought': [70, 75, 80]
            },
            'momentum_breakout': {
                'channel_period': [10, 20, 30],
                'min_volume_ratio': [1.2, 1.5, 2.0],
                'min_adx': [20, 25, 30],
                'adx_period': [14]
            },
            'vwap_reversion': {
                'vwap_std': [1.5, 2, 2.5],
                'rsi_period': [9, 14],
                'rsi_oversold': [25, 30],
                'rsi_overbought': [70, 75]
            },
            'supertrend': {
                'supertrend_period': [7, 10, 14],
                'supertrend_multiplier': [2, 3, 4]
            },
            'scalping': {
                'ema_fast': [3, 5],
                'ema_slow': [8, 10, 13],
                'momentum_period': [3, 5, 8]
            },
            'support_resistance': {
                'sr_lookback': [10, 20, 30],
                'volume_threshold': [1.1, 1.2, 1.5]
            }
        }
        
    def test_strategy(self, strategy_name: str, params: Dict, data: pd.DataFrame) -> Dict:
        """Test a single strategy configuration"""
        try:
            # Initialize strategy
            strategy_class = self.strategies[strategy_name]
            strategy = strategy_class(params)
            
            # Calculate signals
            data_with_signals = strategy.calculate_signals(data.copy())
            
            # Create simple strategy wrapper for backtester
            class StrategyWrapper:
                def __init__(self):
                    self.min_confirmations = 1
                    
                def generate_signals(self, data, _):
                    data['long_signal'] = data.get('buy_signal', 0)
                    data['short_signal'] = data.get('sell_signal', 0)
                    return data
            
            # Run backtest
            wrapper = StrategyWrapper()
            backtester = Backtester(wrapper)
            
            # Simple indicator params for backtester
            indicator_params = {'strategy': {strategy_name: params}}
            
            results = backtester.run_backtest(data_with_signals, indicator_params)
            
            if results and results['metrics']:
                return {
                    'strategy': strategy_name,
                    'params': params,
                    'metrics': results['metrics'],
                    'trades': len(results['trades'])
                }
            
        except Exception as e:
            logger.error(f"Error testing {strategy_name}: {e}")
            
        return None
    
    def optimize_all_strategies(self, days_back: int = 60):
        """Test all strategies and find the best performers"""
        logger.info("Starting comprehensive strategy optimization...")
        
        # Fetch data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        data = self.data_handler.fetch_data(
            interval='5m',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        if len(data) < 100:
            logger.error("Insufficient data")
            return None
        
        all_results = []
        
        # Test each strategy type
        for strategy_name, param_ranges in self.parameter_ranges.items():
            logger.info(f"\nTesting {strategy_name} strategy...")
            
            # Generate parameter combinations
            param_names = list(param_ranges.keys())
            param_values = [param_ranges[name] for name in param_names]
            
            for values in itertools.product(*param_values):
                params = dict(zip(param_names, values))
                
                result = self.test_strategy(strategy_name, params, data)
                if result:
                    all_results.append(result)
                    
                    # Log promising results immediately
                    if result['metrics']['sharpe_ratio'] > 1.0:
                        logger.info(f"Promising result: {strategy_name} - Sharpe: {result['metrics']['sharpe_ratio']:.2f}")
        
        # Sort by different metrics
        if all_results:
            # Sort by Sharpe ratio
            by_sharpe = sorted(all_results, key=lambda x: x['metrics']['sharpe_ratio'], reverse=True)
            
            # Sort by total return
            by_return = sorted(all_results, key=lambda x: x['metrics']['total_return'], reverse=True)
            
            # Sort by win rate
            by_win_rate = sorted(all_results, key=lambda x: x['metrics']['win_rate'], reverse=True)
            
            # Calculate composite score
            for result in all_results:
                metrics = result['metrics']
                
                # Normalize metrics for scoring
                sharpe_score = min(metrics['sharpe_ratio'] / 2, 1) * 0.3  # 30% weight
                return_score = min(metrics['annual_return'] / 0.5, 1) * 0.3  # 30% weight
                win_rate_score = metrics['win_rate'] * 0.2  # 20% weight
                drawdown_score = max(0, 1 - metrics['max_drawdown'] / 0.3) * 0.2  # 20% weight
                
                result['composite_score'] = sharpe_score + return_score + win_rate_score + drawdown_score
            
            # Sort by composite score
            by_composite = sorted(all_results, key=lambda x: x['composite_score'], reverse=True)
            
            # Save results
            results_summary = {
                'test_date': datetime.now().isoformat(),
                'data_period': f"{days_back} days",
                'total_strategies_tested': len(all_results),
                'top_10_by_sharpe': self._format_results(by_sharpe[:10]),
                'top_10_by_return': self._format_results(by_return[:10]),
                'top_10_by_win_rate': self._format_results(by_win_rate[:10]),
                'top_10_overall': self._format_results(by_composite[:10])
            }
            
            with open('advanced_strategy_results.json', 'w') as f:
                json.dump(results_summary, f, indent=4)
            
            # Print summary
            self._print_results_summary(by_composite[:10])
            
            return results_summary
        
        return None
    
    def _format_results(self, results: List[Dict]) -> List[Dict]:
        """Format results for saving"""
        formatted = []
        for r in results:
            formatted.append({
                'strategy': r['strategy'],
                'params': r['params'],
                'sharpe_ratio': round(r['metrics']['sharpe_ratio'], 2),
                'annual_return': round(r['metrics']['annual_return'], 4),
                'win_rate': round(r['metrics']['win_rate'], 4),
                'max_drawdown': round(r['metrics']['max_drawdown'], 4),
                'total_trades': r['trades'],
                'profit_factor': round(r['metrics']['profit_factor'], 2),
                'expected_value': round(r['metrics']['expected_value'], 2),
                'composite_score': round(r.get('composite_score', 0), 3)
            })
        return formatted
    
    def _print_results_summary(self, top_results: List[Dict]):
        """Print formatted results summary"""
        print("\n" + "="*100)
        print("TOP 10 STRATEGIES BY COMPOSITE SCORE")
        print("="*100)
        print(f"{'Rank':<5} {'Strategy':<20} {'Return':<10} {'Win Rate':<10} {'Sharpe':<10} {'Max DD':<10} {'Score':<10}")
        print("-"*100)
        
        for i, result in enumerate(top_results, 1):
            print(f"{i:<5} {result['strategy']:<20} "
                  f"{result['metrics']['annual_return']*100:>8.1f}% "
                  f"{result['metrics']['win_rate']*100:>8.1f}% "
                  f"{result['metrics']['sharpe_ratio']:>9.2f} "
                  f"{result['metrics']['max_drawdown']*100:>8.1f}% "
                  f"{result.get('composite_score', 0):>9.3f}")
        
        print("\n" + "="*100)
        print("WINNER: " + top_results[0]['strategy'].upper())
        print("="*100)
        
        winner = top_results[0]
        print(f"Strategy: {winner['strategy']}")
        print(f"Parameters: {json.dumps(winner['params'], indent=2)}")
        print(f"\nPerformance Metrics:")
        print(f"  - Annual Return: {winner['metrics']['annual_return']*100:.2f}%")
        print(f"  - Win Rate: {winner['metrics']['win_rate']*100:.2f}%")
        print(f"  - Sharpe Ratio: {winner['metrics']['sharpe_ratio']:.2f}")
        print(f"  - Max Drawdown: {winner['metrics']['max_drawdown']*100:.2f}%")
        print(f"  - Profit Factor: {winner['metrics']['profit_factor']:.2f}")
        print(f"  - Expected Value: ${winner['metrics']['expected_value']:.2f}")
        print(f"  - Total Trades: {winner['trades']}")


def main():
    """Run comprehensive strategy optimization"""
    optimizer = AdvancedOptimizer()
    
    print("🚀 Advanced Strategy Optimization for SPX")
    print("Testing 6 different strategy types with multiple parameters...")
    print("This may take several minutes...\n")
    
    results = optimizer.optimize_all_strategies(days_back=60)
    
    if results:
        print("\n✅ Optimization complete!")
        print(f"Results saved to: advanced_strategy_results.json")
        print(f"\nTotal strategies tested: {results['total_strategies_tested']}")
    else:
        print("\n❌ Optimization failed")


if __name__ == "__main__":
    main()