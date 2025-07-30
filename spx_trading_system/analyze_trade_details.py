"""
Analyze Detailed Trade Metrics for Triple_Optimized Strategy
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import TRADING_CONFIG, INDICATOR_PARAMS
from src.data_handler import DataHandler
from src.indicators_simple import TechnicalIndicators
from src.strategy import TradingStrategy
from src.backtest import Backtester

def analyze_winning_strategy():
    """
    Run detailed analysis on the Triple_Optimized strategy
    """
    print("="*80)
    print("DETAILED TRADE ANALYSIS - TRIPLE_OPTIMIZED STRATEGY")
    print("="*80)
    
    # Triple_Optimized parameters
    params = {
        'RSI': {'periods': [9], 'oversold': [25], 'overbought': [75]},
        'MACD': {'fast': [8], 'slow': [21], 'signal': [5]},
        'EMA': {'short_periods': [5], 'long_periods': [20]}
    }
    
    # Initialize components
    data_handler = DataHandler()
    indicators = TechnicalIndicators()
    strategy = TradingStrategy()
    backtester = Backtester(strategy)
    
    # Calculate date range (60 days)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - pd.Timedelta(days=60)).strftime('%Y-%m-%d')
    
    # Fetch data
    data = data_handler.fetch_data(
        interval='5m',
        start_date=start_date,
        end_date=end_date
    )
    
    # Calculate indicators
    data_with_indicators = indicators.calculate_all_indicators(data, params)
    
    # Run backtest
    results = backtester.run_backtest(data_with_indicators, params)
    
    # Extract trades
    trades = results['trades']
    metrics = results['metrics']
    
    # Calculate detailed metrics
    if trades:
        trades_df = pd.DataFrame(trades)
        
        # Separate winning and losing trades
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]
        
        # Calculate average win and loss
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 0
        
        # Risk/Reward Ratio
        risk_reward_ratio = avg_win / avg_loss if avg_loss > 0 else float('inf')
        
        # Calculate stop loss statistics
        sl_distances = []
        tp_distances = []
        entry_prices = []
        
        for trade in trades:
            if trade['entry_price'] > 0:
                entry_prices.append(trade['entry_price'])
                
                # Calculate stop loss distance
                if trade['direction'] == 1:  # Long
                    sl_distance = abs(trade['entry_price'] - trade['stop_loss']) / trade['entry_price'] * 100
                else:  # Short
                    sl_distance = abs(trade['stop_loss'] - trade['entry_price']) / trade['entry_price'] * 100
                sl_distances.append(sl_distance)
                
                # Calculate take profit distance
                if trade['direction'] == 1:  # Long
                    tp_distance = abs(trade['take_profit'] - trade['entry_price']) / trade['entry_price'] * 100
                else:  # Short
                    tp_distance = abs(trade['entry_price'] - trade['take_profit']) / trade['entry_price'] * 100
                tp_distances.append(tp_distance)
        
        avg_sl_distance = np.mean(sl_distances) if sl_distances else 0
        avg_tp_distance = np.mean(tp_distances) if tp_distances else 0
        
        # Trade frequency calculations
        total_days = 60
        trades_per_day = len(trades) / total_days
        trades_per_week = trades_per_day * 5  # Trading days
        trades_per_month = trades_per_day * 21  # Average trading days per month
        trades_per_year = trades_per_day * 252  # Trading days per year
        
        # Exit reason analysis
        exit_reasons = trades_df['exit_reason'].value_counts()
        
        # Trade duration
        durations = []
        for trade in trades:
            if 'exit_timestamp' in trade and trade['exit_timestamp'] and 'timestamp' in trade:
                duration = (pd.Timestamp(trade['exit_timestamp']) - pd.Timestamp(trade['timestamp'])).total_seconds() / 60
                durations.append(duration)
        
        avg_duration = np.mean(durations) if durations else 0
        
        # Print results
        print("\n📊 TRADE STATISTICS")
        print("-" * 50)
        print(f"Total Trades: {len(trades)}")
        print(f"Winning Trades: {len(winning_trades)} ({len(winning_trades)/len(trades)*100:.1f}%)")
        print(f"Losing Trades: {len(losing_trades)} ({len(losing_trades)/len(trades)*100:.1f}%)")
        
        print("\n💰 PROFIT/LOSS METRICS")
        print("-" * 50)
        print(f"Average Win: ${avg_win:.2f}")
        print(f"Average Loss: ${avg_loss:.2f}")
        print(f"Risk/Reward Ratio: 1:{risk_reward_ratio:.2f}")
        print(f"Expected Value per Trade: ${metrics['expected_value']:.2f}")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        
        print("\n🛡️ RISK MANAGEMENT")
        print("-" * 50)
        print(f"Average Stop Loss Distance: {avg_sl_distance:.2f}%")
        print(f"Average Take Profit Distance: {avg_tp_distance:.2f}%")
        print(f"TP/SL Ratio: {avg_tp_distance/avg_sl_distance:.2f}:1" if avg_sl_distance > 0 else "N/A")
        print(f"Risk per Trade: {TRADING_CONFIG['initial_capital'] * 0.02 / TRADING_CONFIG['initial_capital'] * 100:.1f}% of capital")
        
        print("\n📅 TRADE FREQUENCY")
        print("-" * 50)
        print(f"Trades per Day: {trades_per_day:.2f}")
        print(f"Trades per Week: {trades_per_week:.1f}")
        print(f"Trades per Month: {trades_per_month:.1f}")
        print(f"Trades per Year (projected): {trades_per_year:.0f}")
        print(f"Average Trade Duration: {avg_duration:.1f} minutes")
        
        print("\n🚪 EXIT ANALYSIS")
        print("-" * 50)
        for reason, count in exit_reasons.items():
            print(f"{reason}: {count} trades ({count/len(trades)*100:.1f}%)")
        
        print("\n📈 PERFORMANCE SUMMARY")
        print("-" * 50)
        print(f"Total Return: {metrics['total_return']:.2f}%")
        print(f"Annual Return: {metrics['annual_return']*100:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
        print(f"Win Rate: {metrics['win_rate']*100:.2f}%")
        
        # Calculate monthly expected profit
        monthly_expected_profit = metrics['expected_value'] * trades_per_month
        yearly_expected_profit = metrics['expected_value'] * trades_per_year
        
        print("\n💵 PROFIT PROJECTIONS")
        print("-" * 50)
        print(f"Expected Monthly Profit: ${monthly_expected_profit:,.2f}")
        print(f"Expected Yearly Profit: ${yearly_expected_profit:,.2f}")
        print(f"Monthly Return on $100k: {monthly_expected_profit/100000*100:.2f}%")
        print(f"Required Capital for $10k/month: ${10000/monthly_expected_profit*100000:,.0f}")
        
        # Distribution of returns
        returns = trades_df['pnl'].values
        print("\n📊 RETURN DISTRIBUTION")
        print("-" * 50)
        print(f"Best Trade: ${returns.max():.2f}")
        print(f"Worst Trade: ${returns.min():.2f}")
        print(f"Median Trade: ${np.median(returns):.2f}")
        print(f"Standard Deviation: ${np.std(returns):.2f}")
        
        # Win/Loss streaks
        win_streak = 0
        loss_streak = 0
        current_win_streak = 0
        current_loss_streak = 0
        
        for pnl in trades_df['pnl']:
            if pnl > 0:
                current_win_streak += 1
                current_loss_streak = 0
                win_streak = max(win_streak, current_win_streak)
            else:
                current_loss_streak += 1
                current_win_streak = 0
                loss_streak = max(loss_streak, current_loss_streak)
        
        print(f"\nMax Winning Streak: {win_streak} trades")
        print(f"Max Losing Streak: {loss_streak} trades")
        
        # Save detailed results
        detailed_results = {
            'strategy': 'Triple_Optimized',
            'total_trades': len(trades),
            'win_rate': metrics['win_rate'],
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'risk_reward_ratio': risk_reward_ratio,
            'expected_value': metrics['expected_value'],
            'avg_stop_loss_pct': avg_sl_distance,
            'avg_take_profit_pct': avg_tp_distance,
            'trades_per_day': trades_per_day,
            'trades_per_week': trades_per_week,
            'trades_per_month': trades_per_month,
            'trades_per_year': trades_per_year,
            'monthly_expected_profit': monthly_expected_profit,
            'yearly_expected_profit': yearly_expected_profit,
            'avg_trade_duration_minutes': avg_duration,
            'max_win_streak': win_streak,
            'max_loss_streak': loss_streak
        }
        
        with open('triple_optimized_detailed_analysis.json', 'w') as f:
            json.dump(detailed_results, f, indent=4)
        
        print("\n✅ Detailed analysis saved to 'triple_optimized_detailed_analysis.json'")
        
    else:
        print("No trades found in backtest results!")

if __name__ == "__main__":
    analyze_winning_strategy()