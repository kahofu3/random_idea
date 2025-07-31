"""
Display ASCII representation of P&L curve
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import TRADING_CONFIG
from src.data_handler import DataHandler
from src.indicators_simple import TechnicalIndicators
from src.strategy import TradingStrategy
from src.backtest import Backtester

def create_ascii_chart():
    """Generate ASCII chart of P&L progression"""
    
    # Triple_Optimized parameters
    params = {
        'RSI': {'periods': [9], 'oversold': [25], 'overbought': [75]},
        'MACD': {'fast': [8], 'slow': [21], 'signal': [5]},
        'EMA': {'short_periods': [5], 'long_periods': [20]}
    }
    
    # Initialize and run backtest
    data_handler = DataHandler()
    indicators = TechnicalIndicators()
    strategy = TradingStrategy()
    backtester = Backtester(strategy)
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - pd.Timedelta(days=60)).strftime('%Y-%m-%d')
    
    data = data_handler.fetch_data(interval='5m', start_date=start_date, end_date=end_date)
    data_with_indicators = indicators.calculate_all_indicators(data, params)
    results = backtester.run_backtest(data_with_indicators, params)
    
    # Extract equity curve
    equity_curve = results['equity_curve']
    trades = results['trades']
    
    # Resample to daily for ASCII display
    equity_curve['timestamp'] = pd.to_datetime(equity_curve['timestamp'])
    equity_curve.set_index('timestamp', inplace=True)
    daily_equity = equity_curve['equity'].resample('D').last().dropna()
    
    # Create ASCII chart
    print("\n" + "="*80)
    print("TRIPLE_OPTIMIZED STRATEGY - P&L PROGRESSION (DAILY)")
    print("="*80)
    
    # Chart parameters
    chart_height = 20
    chart_width = 70
    
    # Calculate scaling
    min_val = daily_equity.min()
    max_val = daily_equity.max()
    value_range = max_val - min_val
    
    # Create chart array
    chart = [[' ' for _ in range(chart_width)] for _ in range(chart_height)]
    
    # Add horizontal axis (initial capital line)
    initial_line = int((TRADING_CONFIG['initial_capital'] - min_val) / value_range * (chart_height - 1))
    if 0 <= initial_line < chart_height:
        for x in range(chart_width):
            chart[chart_height - 1 - initial_line][x] = '-'
    
    # Plot equity curve
    x_scale = len(daily_equity) / chart_width
    for x in range(chart_width):
        idx = int(x * x_scale)
        if idx < len(daily_equity):
            value = daily_equity.iloc[idx]
            y = int((value - min_val) / value_range * (chart_height - 1))
            if 0 <= y < chart_height:
                chart[chart_height - 1 - y][x] = '*'
    
    # Add value labels
    print(f"${max_val:,.0f} |")
    
    # Print chart
    for row in chart:
        print(f"       |{''.join(row)}")
    
    print(f"${min_val:,.0f} |" + "_" * chart_width)
    print(f"       {start_date:<35}{end_date:>35}")
    
    # Print summary statistics
    print("\n" + "-"*80)
    print("SUMMARY STATISTICS:")
    print("-"*80)
    print(f"Starting Capital:    ${TRADING_CONFIG['initial_capital']:>12,.2f}")
    print(f"Final Equity:        ${daily_equity.iloc[-1]:>12,.2f}")
    print(f"Total P&L:           ${daily_equity.iloc[-1] - TRADING_CONFIG['initial_capital']:>12,.2f}")
    print(f"Total Return:        {(daily_equity.iloc[-1] - TRADING_CONFIG['initial_capital']) / TRADING_CONFIG['initial_capital'] * 100:>12.2f}%")
    print(f"Total Trades:        {len(trades):>12}")
    print(f"Win Rate:            {results['metrics']['win_rate']*100:>12.1f}%")
    print(f"Max Drawdown:        {results['metrics']['max_drawdown']*100:>12.2f}%")
    print(f"Sharpe Ratio:        {results['metrics']['sharpe_ratio']:>12.2f}")
    
    # Show daily P&L distribution
    print("\n" + "-"*80)
    print("DAILY P&L DISTRIBUTION:")
    print("-"*80)
    
    # Calculate daily P&L
    daily_pnl = daily_equity.diff().dropna()
    positive_days = (daily_pnl > 0).sum()
    negative_days = (daily_pnl < 0).sum()
    
    print(f"Positive Days: {positive_days} ({positive_days/len(daily_pnl)*100:.1f}%)")
    print(f"Negative Days: {negative_days} ({negative_days/len(daily_pnl)*100:.1f}%)")
    print(f"Best Day:      ${daily_pnl.max():>10,.2f}")
    print(f"Worst Day:     ${daily_pnl.min():>10,.2f}")
    print(f"Average Day:   ${daily_pnl.mean():>10,.2f}")
    
    # Mini bar chart of P&L distribution
    print("\nDaily P&L Bar Chart (last 20 days):")
    print("-" * 50)
    
    recent_pnl = daily_pnl.tail(20)
    max_abs_pnl = max(abs(recent_pnl.max()), abs(recent_pnl.min()))
    
    for date, pnl in recent_pnl.items():
        bar_length = int(abs(pnl) / max_abs_pnl * 20)
        if pnl >= 0:
            bar = ' ' * 20 + '|' + '█' * bar_length
        else:
            bar = ' ' * (20 - bar_length) + '█' * bar_length + '|' + ' ' * 20
        print(f"{date.strftime('%m/%d')} {bar} ${pnl:>8,.0f}")
    
    print("\n" + "="*80)
    print("Legend: * = Equity value, - = Initial capital ($100,000), █ = Daily P&L")
    print("="*80)

if __name__ == "__main__":
    create_ascii_chart()