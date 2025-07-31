"""
Plot P&L Curve for Triple_Optimized Strategy
Shows the progression of profits/losses from day one to end
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import json

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import TRADING_CONFIG
from src.data_handler import DataHandler
from src.indicators_simple import TechnicalIndicators
from src.strategy import TradingStrategy
from src.backtest import Backtester

def plot_pl_progression():
    """
    Generate and plot P&L progression for Triple_Optimized strategy
    """
    print("Generating P&L progression chart...")
    
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
    print(f"Fetching data from {start_date} to {end_date}...")
    data = data_handler.fetch_data(
        interval='5m',
        start_date=start_date,
        end_date=end_date
    )
    
    # Calculate indicators
    print("Calculating indicators...")
    data_with_indicators = indicators.calculate_all_indicators(data, params)
    
    # Run backtest
    print("Running backtest...")
    results = backtester.run_backtest(data_with_indicators, params)
    
    # Extract equity curve and trades
    equity_curve = results['equity_curve']
    trades = results['trades']
    metrics = results['metrics']
    
    # Debug: Check equity curve structure
    print(f"Equity curve columns: {equity_curve.columns.tolist()}")
    print(f"Equity curve shape: {equity_curve.shape}")
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 10))
    
    # Main plot: Equity curve
    ax1 = plt.subplot(3, 1, (1, 2))
    
    # Plot equity curve
    # Check if 'equity' column exists (lowercase)
    if 'equity' in equity_curve.columns:
        equity_col = 'equity'
    else:
        equity_col = 'Equity'
    
    equity_curve[equity_col].plot(ax=ax1, linewidth=2, color='darkblue', label='Account Equity')
    
    # Add initial capital line
    ax1.axhline(y=TRADING_CONFIG['initial_capital'], color='gray', linestyle='--', 
                alpha=0.5, label=f'Initial Capital (${TRADING_CONFIG["initial_capital"]:,})')
    
    # Mark trade entry and exit points
    for trade in trades:
        entry_time = pd.Timestamp(trade['timestamp'])
        exit_time = pd.Timestamp(trade['exit_timestamp']) if 'exit_timestamp' in trade else None
        
        if exit_time:
            # Color based on profit/loss
            color = 'green' if trade['pnl'] > 0 else 'red'
            marker = '^' if trade['direction'] == 1 else 'v'
            
            # Entry point
            if entry_time in equity_curve.index:
                ax1.scatter(entry_time, equity_curve.loc[entry_time, equity_col], 
                           color=color, marker=marker, s=50, alpha=0.7, zorder=5)
            
            # Exit point
            if exit_time in equity_curve.index:
                ax1.scatter(exit_time, equity_curve.loc[exit_time, equity_col], 
                           color=color, marker='o', s=50, alpha=0.7, zorder=5)
                
                # Draw line connecting entry and exit
                if entry_time in equity_curve.index:
                    ax1.plot([entry_time, exit_time], 
                            [equity_curve.loc[entry_time, equity_col], 
                             equity_curve.loc[exit_time, equity_col]], 
                            color=color, alpha=0.3, linewidth=1)
    
    # Fill area under equity curve
    ax1.fill_between(equity_curve.index, TRADING_CONFIG['initial_capital'], 
                     equity_curve[equity_col], 
                     where=(equity_curve[equity_col] >= TRADING_CONFIG['initial_capital']), 
                     color='green', alpha=0.1, label='Profit')
    ax1.fill_between(equity_curve.index, TRADING_CONFIG['initial_capital'], 
                     equity_curve[equity_col], 
                     where=(equity_curve[equity_col] < TRADING_CONFIG['initial_capital']), 
                     color='red', alpha=0.1, label='Loss')
    
    # Formatting
    ax1.set_title('Triple_Optimized Strategy - P&L Progression Over Time', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Account Equity ($)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')
    
    # Format y-axis as currency
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Add performance metrics text
    textstr = f'Total Return: {metrics["total_return"]:.2f}%\n'
    textstr += f'Win Rate: {metrics["win_rate"]*100:.1f}%\n'
    textstr += f'Max Drawdown: {metrics["max_drawdown"]*100:.1f}%\n'
    textstr += f'Sharpe Ratio: {metrics["sharpe_ratio"]:.2f}\n'
    textstr += f'Total Trades: {len(trades)}'
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    # Subplot 2: Daily P&L
    ax2 = plt.subplot(3, 1, 3)
    
    # Calculate daily P&L
    daily_pl = []
    daily_dates = []
    
    # Group trades by date
    trades_df = pd.DataFrame(trades)
    if len(trades_df) > 0:
        trades_df['date'] = pd.to_datetime(trades_df['exit_timestamp']).dt.date
        daily_pnl = trades_df.groupby('date')['pnl'].sum()
        
        # Create bar chart
        colors = ['green' if x > 0 else 'red' for x in daily_pnl.values]
        ax2.bar(daily_pnl.index, daily_pnl.values, color=colors, alpha=0.7)
        
        # Add cumulative line
        cumulative_pnl = daily_pnl.cumsum()
        ax2_twin = ax2.twinx()
        ax2_twin.plot(daily_pnl.index, cumulative_pnl.values, 
                     color='darkblue', linewidth=2, marker='o', markersize=4)
        ax2_twin.set_ylabel('Cumulative P&L ($)', fontsize=10)
        ax2_twin.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
    ax2.set_title('Daily P&L Distribution', fontsize=12)
    ax2.set_xlabel('Date', fontsize=10)
    ax2.set_ylabel('Daily P&L ($)', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Rotate x-axis labels
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Format x-axis dates
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('triple_optimized_pl_curve.png', dpi=300, bbox_inches='tight')
    print("\n✅ P&L progression chart saved as 'triple_optimized_pl_curve.png'")
    
    # Also create a simplified version
    fig2, ax = plt.subplots(figsize=(12, 6))
    
    # Plot simple equity curve
    equity_curve[equity_col].plot(ax=ax, linewidth=3, color='darkblue')
    
    # Add shaded area
    ax.fill_between(equity_curve.index, equity_curve[equity_col].values, 
                    TRADING_CONFIG['initial_capital'], alpha=0.3, color='lightblue')
    
    # Add initial capital line
    ax.axhline(y=TRADING_CONFIG['initial_capital'], color='black', linestyle='--', 
               linewidth=1, alpha=0.5)
    
    # Formatting
    ax.set_title('Account Equity Growth - Triple_Optimized Strategy', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Account Value ($)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Add final statistics
    final_equity = equity_curve[equity_col].iloc[-1]
    total_return = (final_equity - TRADING_CONFIG['initial_capital']) / TRADING_CONFIG['initial_capital'] * 100
    
    stats_text = f'Initial: ${TRADING_CONFIG["initial_capital"]:,}\n'
    stats_text += f'Final: ${final_equity:,.2f}\n'
    stats_text += f'Return: {total_return:.2f}%\n'
    stats_text += f'Period: {start_date} to {end_date}'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('triple_optimized_equity_curve.png', dpi=300, bbox_inches='tight')
    print("✅ Simplified equity curve saved as 'triple_optimized_equity_curve.png'")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("P&L PROGRESSION SUMMARY")
    print("="*60)
    print(f"Starting Capital: ${TRADING_CONFIG['initial_capital']:,}")
    print(f"Final Equity: ${final_equity:,.2f}")
    print(f"Total P&L: ${final_equity - TRADING_CONFIG['initial_capital']:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Trading Period: {start_date} to {end_date}")
    print(f"Total Trading Days: {len(equity_curve) / 78:.0f}")  # ~78 5-min bars per day
    
    # Show plots (will be saved even if display doesn't work)
    try:
        plt.show()
    except:
        pass

if __name__ == "__main__":
    plot_pl_progression()