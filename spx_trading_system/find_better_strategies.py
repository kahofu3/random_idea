"""
Find Better Strategies for SPX Trading
Tests different approaches to beat our current 65.6% win rate
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import json

from src.data_handler import DataHandler
from src.indicators_simple import TechnicalIndicators

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrategyTester:
    """Test different trading strategies"""
    
    def __init__(self):
        self.data_handler = DataHandler()
        self.indicators = TechnicalIndicators()
        
    def test_strategy(self, data: pd.DataFrame, strategy_func, name: str) -> Dict:
        """Test a single strategy and return metrics"""
        # Apply strategy
        signals = strategy_func(data)
        
        # Simulate trades
        trades = []
        position = None
        
        for i in range(len(data)):
            if position is None and signals['buy'][i]:
                # Enter long position
                position = {
                    'entry_idx': i,
                    'entry_price': data['Close'].iloc[i],
                    'type': 'long'
                }
            elif position is None and signals['sell'][i]:
                # Enter short position
                position = {
                    'entry_idx': i,
                    'entry_price': data['Close'].iloc[i],
                    'type': 'short'
                }
            elif position:
                # Check exit conditions
                exit_signal = False
                exit_reason = ''
                
                if position['type'] == 'long' and signals['sell'][i]:
                    exit_signal = True
                    exit_reason = 'signal'
                elif position['type'] == 'short' and signals['buy'][i]:
                    exit_signal = True
                    exit_reason = 'signal'
                
                # Stop loss check (2% default)
                if position['type'] == 'long':
                    pnl_pct = (data['Close'].iloc[i] - position['entry_price']) / position['entry_price']
                    if pnl_pct < -0.02:
                        exit_signal = True
                        exit_reason = 'stop_loss'
                else:
                    pnl_pct = (position['entry_price'] - data['Close'].iloc[i]) / position['entry_price']
                    if pnl_pct < -0.02:
                        exit_signal = True
                        exit_reason = 'stop_loss'
                
                if exit_signal:
                    # Close position
                    exit_price = data['Close'].iloc[i]
                    
                    if position['type'] == 'long':
                        pnl = exit_price - position['entry_price']
                        pnl_pct = pnl / position['entry_price']
                    else:
                        pnl = position['entry_price'] - exit_price
                        pnl_pct = pnl / position['entry_price']
                    
                    trades.append({
                        'entry_time': data.index[position['entry_idx']],
                        'exit_time': data.index[i],
                        'type': position['type'],
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'exit_reason': exit_reason
                    })
                    
                    position = None
        
        # Calculate metrics
        if trades:
            wins = [t for t in trades if t['pnl'] > 0]
            losses = [t for t in trades if t['pnl'] <= 0]
            
            win_rate = len(wins) / len(trades)
            avg_win = np.mean([t['pnl_pct'] for t in wins]) if wins else 0
            avg_loss = np.mean([abs(t['pnl_pct']) for t in losses]) if losses else 0
            
            # Expected value per trade
            expected_value = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
            
            # Total return
            total_return = sum(t['pnl_pct'] for t in trades)
            
            # Sharpe ratio (simplified)
            returns = [t['pnl_pct'] for t in trades]
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            
            # Max drawdown
            cumulative = np.cumsum([t['pnl_pct'] for t in trades])
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / (1 + running_max)
            max_drawdown = abs(np.min(drawdown))
            
            return {
                'name': name,
                'total_trades': len(trades),
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'expected_value': expected_value,
                'total_return': total_return,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_drawdown,
                'trades': trades
            }
        
        return None
    
    def strategy_1_enhanced_mean_reversion(self, data: pd.DataFrame) -> Dict:
        """Enhanced mean reversion with multiple timeframes"""
        # Add indicators
        data = self.indicators.add_bollinger_bands(data, 20, 2)
        data = self.indicators.add_rsi(data, 7)  # Faster RSI
        data = self.indicators.add_rsi(data, 14)  # Standard RSI
        data = self.indicators.add_atr(data, 14)
        
        # Volume analysis
        data['volume_sma'] = data['Volume'].rolling(20).mean()
        data['high_volume'] = data['Volume'] > data['volume_sma'] * 1.5
        
        # Signals
        buy_signals = (
            (data['Close'] <= data['BB_20_2_lower']) &  # Touch lower band
            (data['RSI_7'] < 20) &  # Extreme oversold on fast RSI
            (data['RSI_14'] < 35) &  # Oversold on standard RSI
            data['high_volume']  # Volume confirmation
        )
        
        sell_signals = (
            (data['Close'] >= data['BB_20_2_upper']) &  # Touch upper band
            (data['RSI_7'] > 80) &  # Extreme overbought on fast RSI
            (data['RSI_14'] > 65) &  # Overbought on standard RSI
            data['high_volume']  # Volume confirmation
        )
        
        return {'buy': buy_signals, 'sell': sell_signals}
    
    def strategy_2_momentum_breakout(self, data: pd.DataFrame) -> Dict:
        """Momentum breakout with volume"""
        # Price channels
        data['high_20'] = data['High'].rolling(20).max()
        data['low_20'] = data['Low'].rolling(20).min()
        
        # Momentum
        data['momentum'] = data['Close'] - data['Close'].shift(10)
        data['momentum_sma'] = data['momentum'].rolling(10).mean()
        
        # Volume
        data['volume_sma'] = data['Volume'].rolling(20).mean()
        data['volume_spike'] = data['Volume'] > data['volume_sma'] * 2
        
        # ATR for volatility
        data = self.indicators.add_atr(data, 14)
        data['high_volatility'] = data['ATR_14'] > data['ATR_14'].rolling(50).mean()
        
        # Signals
        buy_signals = (
            (data['Close'] > data['high_20'].shift(1)) &  # Breakout
            (data['momentum'] > data['momentum_sma']) &  # Positive momentum
            data['volume_spike'] &  # Volume confirmation
            data['high_volatility']  # Volatility present
        )
        
        sell_signals = (
            (data['Close'] < data['low_20'].shift(1)) &  # Breakdown
            (data['momentum'] < data['momentum_sma']) &  # Negative momentum
            data['volume_spike'] &  # Volume confirmation
            data['high_volatility']  # Volatility present
        )
        
        return {'buy': buy_signals, 'sell': sell_signals}
    
    def strategy_3_vwap_reversion(self, data: pd.DataFrame) -> Dict:
        """VWAP mean reversion"""
        # Calculate VWAP
        data['typical_price'] = (data['High'] + data['Low'] + data['Close']) / 3
        data['tpv'] = data['typical_price'] * data['Volume']
        
        # Simple VWAP (resets daily in real implementation)
        data['cum_tpv'] = data['tpv'].rolling(78).sum()  # ~1 day of 5min bars
        data['cum_vol'] = data['Volume'].rolling(78).sum()
        data['vwap'] = data['cum_tpv'] / data['cum_vol']
        
        # VWAP bands
        data['vwap_std'] = data['typical_price'].rolling(78).std()
        data['vwap_upper'] = data['vwap'] + (2 * data['vwap_std'])
        data['vwap_lower'] = data['vwap'] - (2 * data['vwap_std'])
        
        # RSI for confirmation
        data = self.indicators.add_rsi(data, 9)
        
        # Signals
        buy_signals = (
            (data['Close'] < data['vwap_lower']) &
            (data['RSI_9'] < 30)
        )
        
        sell_signals = (
            (data['Close'] > data['vwap_upper']) &
            (data['RSI_9'] > 70)
        )
        
        return {'buy': buy_signals, 'sell': sell_signals}
    
    def strategy_4_triple_ema(self, data: pd.DataFrame) -> Dict:
        """Triple EMA crossover system"""
        # EMAs
        data = self.indicators.add_ema(data, 8, 'EMA_8')
        data = self.indicators.add_ema(data, 13, 'EMA_13')
        data = self.indicators.add_ema(data, 21, 'EMA_21')
        
        # MACD for confirmation
        data = self.indicators.add_macd(data, 12, 26, 9)
        
        # Trend alignment
        uptrend = (data['EMA_8'] > data['EMA_13']) & (data['EMA_13'] > data['EMA_21'])
        downtrend = (data['EMA_8'] < data['EMA_13']) & (data['EMA_13'] < data['EMA_21'])
        
        # Signals
        buy_signals = (
            uptrend &
            (~uptrend.shift(1)) &  # Just turned to uptrend
            (data['MACD_12_26_9'] > data['MACD_12_26_9_signal'])
        )
        
        sell_signals = (
            downtrend &
            (~downtrend.shift(1)) &  # Just turned to downtrend
            (data['MACD_12_26_9'] < data['MACD_12_26_9_signal'])
        )
        
        return {'buy': buy_signals, 'sell': sell_signals}
    
    def strategy_5_stochastic_rsi_combo(self, data: pd.DataFrame) -> Dict:
        """Stochastic + RSI combination"""
        # Stochastic
        data = self.indicators.add_stochastic(data, 14, 3)
        
        # RSI
        data = self.indicators.add_rsi(data, 14)
        
        # Bollinger Bands for context
        data = self.indicators.add_bollinger_bands(data, 20, 1.5)
        
        # Signals
        buy_signals = (
            (data['Stoch_K_14'] < 20) &
            (data['Stoch_K_14'] > data['Stoch_D_14']) &  # K crosses above D
            (data['RSI_14'] < 40) &
            (data['Close'] < data['BB_20_1.5_middle'])  # Below middle band
        )
        
        sell_signals = (
            (data['Stoch_K_14'] > 80) &
            (data['Stoch_K_14'] < data['Stoch_D_14']) &  # K crosses below D
            (data['RSI_14'] > 60) &
            (data['Close'] > data['BB_20_1.5_middle'])  # Above middle band
        )
        
        return {'buy': buy_signals, 'sell': sell_signals}
    
    def strategy_6_hybrid_adaptive(self, data: pd.DataFrame) -> Dict:
        """Adaptive strategy that switches between trend and reversion"""
        # Calculate market regime
        data = self.indicators.add_atr(data, 14)
        data = self.indicators.add_ema(data, 50, 'EMA_50')
        
        # Trend strength
        data['trend_strength'] = abs(data['Close'] - data['EMA_50']) / data['ATR_14']
        data['strong_trend'] = data['trend_strength'] > 2
        
        # Mean reversion indicators
        data = self.indicators.add_bollinger_bands(data, 20, 2)
        data = self.indicators.add_rsi(data, 9)
        
        # Trend indicators
        data = self.indicators.add_macd(data, 8, 21, 5)
        
        # Adaptive signals
        # In strong trend: use momentum
        trend_buy = (
            data['strong_trend'] &
            (data['Close'] > data['EMA_50']) &
            (data['MACD_8_21_5'] > data['MACD_8_21_5_signal']) &
            (data['MACD_8_21_5'] > data['MACD_8_21_5'].shift(1))
        )
        
        trend_sell = (
            data['strong_trend'] &
            (data['Close'] < data['EMA_50']) &
            (data['MACD_8_21_5'] < data['MACD_8_21_5_signal']) &
            (data['MACD_8_21_5'] < data['MACD_8_21_5'].shift(1))
        )
        
        # In range: use mean reversion
        reversion_buy = (
            (~data['strong_trend']) &
            (data['Close'] <= data['BB_20_2_lower']) &
            (data['RSI_9'] < 25)
        )
        
        reversion_sell = (
            (~data['strong_trend']) &
            (data['Close'] >= data['BB_20_2_upper']) &
            (data['RSI_9'] > 75)
        )
        
        # Combine
        buy_signals = trend_buy | reversion_buy
        sell_signals = trend_sell | reversion_sell
        
        return {'buy': buy_signals, 'sell': sell_signals}
    
    def run_all_strategies(self, days_back: int = 60):
        """Test all strategies"""
        logger.info("Testing advanced trading strategies...")
        
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
        
        # Test each strategy
        strategies = [
            (self.strategy_1_enhanced_mean_reversion, "Enhanced Mean Reversion"),
            (self.strategy_2_momentum_breakout, "Momentum Breakout"),
            (self.strategy_3_vwap_reversion, "VWAP Reversion"),
            (self.strategy_4_triple_ema, "Triple EMA System"),
            (self.strategy_5_stochastic_rsi_combo, "Stochastic RSI Combo"),
            (self.strategy_6_hybrid_adaptive, "Hybrid Adaptive")
        ]
        
        results = []
        
        for strategy_func, name in strategies:
            logger.info(f"\nTesting {name}...")
            
            try:
                signals = strategy_func(data.copy())
                metrics = self.test_strategy(data.copy(), lambda x: signals, name)
                
                if metrics:
                    results.append(metrics)
                    
                    # Print summary
                    print(f"\n{name}:")
                    print(f"  Trades: {metrics['total_trades']}")
                    print(f"  Win Rate: {metrics['win_rate']*100:.1f}%")
                    print(f"  Expected Value: {metrics['expected_value']*100:.2f}% per trade")
                    print(f"  Total Return: {metrics['total_return']*100:.1f}%")
                    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
                    print(f"  Max Drawdown: {metrics['max_drawdown']*100:.1f}%")
                    
            except Exception as e:
                logger.error(f"Error testing {name}: {e}")
        
        # Compare with current strategy (Triple_Optimized baseline)
        print("\n" + "="*80)
        print("COMPARISON WITH CURRENT STRATEGY (Triple_Optimized)")
        print("="*80)
        print("Current Performance: Win Rate: 65.6%, Annual Return: 16.54%")
        print("-"*80)
        
        # Sort by different metrics
        if results:
            # By win rate
            by_win_rate = sorted(results, key=lambda x: x['win_rate'], reverse=True)
            print("\nTop 3 by Win Rate:")
            for i, r in enumerate(by_win_rate[:3]):
                print(f"{i+1}. {r['name']}: {r['win_rate']*100:.1f}% "
                      f"(vs current: {(r['win_rate']-0.656)*100:+.1f}%)")
            
            # By expected value
            by_ev = sorted(results, key=lambda x: x['expected_value'], reverse=True)
            print("\nTop 3 by Expected Value per Trade:")
            for i, r in enumerate(by_ev[:3]):
                print(f"{i+1}. {r['name']}: {r['expected_value']*100:.2f}% per trade")
            
            # By Sharpe ratio
            by_sharpe = sorted(results, key=lambda x: x['sharpe_ratio'], reverse=True)
            print("\nTop 3 by Sharpe Ratio:")
            for i, r in enumerate(by_sharpe[:3]):
                print(f"{i+1}. {r['name']}: {r['sharpe_ratio']:.2f}")
            
            # Overall winner
            print("\n" + "="*80)
            print("🏆 OVERALL WINNER")
            print("="*80)
            
            # Calculate composite score
            for r in results:
                # Normalize metrics
                win_score = r['win_rate'] / 0.7  # Target 70% win rate
                ev_score = r['expected_value'] / 0.01  # Target 1% per trade
                sharpe_score = r['sharpe_ratio'] / 1.5  # Target 1.5 Sharpe
                dd_score = 1 - (r['max_drawdown'] / 0.2)  # Target <20% DD
                
                r['composite_score'] = (win_score * 0.3 + ev_score * 0.3 + 
                                       sharpe_score * 0.25 + dd_score * 0.15)
            
            winner = max(results, key=lambda x: x['composite_score'])
            
            print(f"\nBest Overall Strategy: {winner['name']}")
            print(f"  Win Rate: {winner['win_rate']*100:.1f}%")
            print(f"  Expected Value: {winner['expected_value']*100:.2f}% per trade")
            print(f"  Total Return: {winner['total_return']*100:.1f}%")
            print(f"  Sharpe Ratio: {winner['sharpe_ratio']:.2f}")
            print(f"  Max Drawdown: {winner['max_drawdown']*100:.1f}%")
            print(f"  Composite Score: {winner['composite_score']:.3f}")
            
            # Save results
            output = {
                'test_date': datetime.now().isoformat(),
                'data_period': f'{days_back} days',
                'strategies': results,
                'winner': winner['name'],
                'current_baseline': {
                    'name': 'Triple_Optimized',
                    'win_rate': 0.656,
                    'annual_return': 0.1654
                }
            }
            
            with open('better_strategies_results.json', 'w') as f:
                json.dump(output, f, indent=4)
            
            print(f"\n✅ Results saved to better_strategies_results.json")
            
            return results
        
        return None


def main():
    """Run strategy comparison"""
    tester = StrategyTester()
    
    print("🔍 Searching for Better SPX Trading Strategies...")
    print("Testing 6 advanced strategies against current baseline...")
    print("This will take a moment...\n")
    
    results = tester.run_all_strategies(days_back=60)
    
    if results:
        print("\n✅ Analysis complete!")
    else:
        print("\n❌ Analysis failed")


if __name__ == "__main__":
    main()