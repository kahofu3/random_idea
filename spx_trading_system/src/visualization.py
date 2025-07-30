"""
Visualization and Reporting Module for SPX Trading System
Generates charts and comprehensive reports
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Optional
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ReportGenerator:
    """
    Generates visualizations and reports for backtest results
    """
    
    def __init__(self, report_dir: str = None):
        if report_dir is None:
            self.report_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                'reports'
            )
        else:
            self.report_dir = report_dir
            
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
    def generate_full_report(self, backtest_results: Dict, strategy_name: str = "SPX_Strategy"):
        """
        Generate comprehensive backtest report
        
        Args:
            backtest_results: Dictionary containing backtest results
            strategy_name: Name for the strategy/report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_folder = os.path.join(self.report_dir, f"{strategy_name}_{timestamp}")
        os.makedirs(report_folder, exist_ok=True)
        
        # Extract components
        metrics = backtest_results['metrics']
        trades = backtest_results['trades']
        equity_curve = backtest_results['equity_curve']
        signals = backtest_results['signals']
        
        # Generate all visualizations
        self.plot_equity_curve(equity_curve, save_path=os.path.join(report_folder, "equity_curve.png"))
        self.plot_drawdown(equity_curve, save_path=os.path.join(report_folder, "drawdown.png"))
        self.plot_returns_distribution(trades, save_path=os.path.join(report_folder, "returns_dist.png"))
        self.plot_trade_analysis(trades, save_path=os.path.join(report_folder, "trade_analysis.png"))
        
        # Generate interactive chart
        self.create_interactive_chart(
            signals, trades, equity_curve,
            save_path=os.path.join(report_folder, "interactive_chart.html")
        )
        
        # Generate text report
        self.generate_text_report(
            metrics, trades,
            save_path=os.path.join(report_folder, "report.txt")
        )
        
        # Save metrics as JSON
        with open(os.path.join(report_folder, "metrics.json"), 'w') as f:
            json.dump(metrics, f, indent=4, default=str)
        
        # Save trades as CSV
        if trades:
            pd.DataFrame(trades).to_csv(
                os.path.join(report_folder, "trades.csv"),
                index=False
            )
        
        print(f"\nReport generated successfully in: {report_folder}")
        
        return report_folder
    
    def plot_equity_curve(self, equity_curve: pd.DataFrame, save_path: str = None):
        """
        Plot equity curve with benchmark comparison
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot equity curve
        ax.plot(equity_curve['timestamp'], equity_curve['equity'], 
                linewidth=2, label='Strategy Equity')
        
        # Add initial capital line
        initial_capital = equity_curve['equity'].iloc[0]
        ax.axhline(y=initial_capital, color='gray', linestyle='--', 
                  alpha=0.5, label='Initial Capital')
        
        # Calculate and plot linear regression trend
        x_numeric = np.arange(len(equity_curve))
        z = np.polyfit(x_numeric, equity_curve['equity'], 1)
        p = np.poly1d(z)
        ax.plot(equity_curve['timestamp'], p(x_numeric), 
               'r--', alpha=0.5, label='Trend')
        
        # Formatting
        ax.set_title('Equity Curve', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Equity ($)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Rotate x-axis labels
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_drawdown(self, equity_curve: pd.DataFrame, save_path: str = None):
        """
        Plot drawdown chart
        """
        # Calculate drawdown
        equity_curve['cummax'] = equity_curve['equity'].cummax()
        equity_curve['drawdown'] = (equity_curve['equity'] - equity_curve['cummax']) / equity_curve['cummax']
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                       gridspec_kw={'height_ratios': [2, 1]})
        
        # Equity curve with cummax
        ax1.plot(equity_curve['timestamp'], equity_curve['equity'], 
                label='Equity', linewidth=2)
        ax1.plot(equity_curve['timestamp'], equity_curve['cummax'], 
                label='Peak Equity', linewidth=1, linestyle='--', alpha=0.7)
        ax1.fill_between(equity_curve['timestamp'], 
                        equity_curve['cummax'], equity_curve['equity'],
                        alpha=0.3, color='red')
        
        ax1.set_title('Equity Curve with Drawdown', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Equity ($)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Drawdown percentage
        ax2.fill_between(equity_curve['timestamp'], 
                        equity_curve['drawdown'] * 100, 0,
                        alpha=0.5, color='red')
        ax2.plot(equity_curve['timestamp'], equity_curve['drawdown'] * 100, 
                color='darkred', linewidth=1)
        
        ax2.set_title('Drawdown %', fontsize=14)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Drawdown %', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Highlight maximum drawdown
        max_dd_idx = equity_curve['drawdown'].idxmin()
        max_dd = equity_curve.loc[max_dd_idx, 'drawdown']
        ax2.axhline(y=max_dd * 100, color='red', linestyle=':', 
                   label=f'Max DD: {max_dd:.2%}')
        ax2.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_returns_distribution(self, trades: List[Dict], save_path: str = None):
        """
        Plot returns distribution and statistics
        """
        if not trades:
            return
            
        trades_df = pd.DataFrame(trades)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Returns histogram
        ax = axes[0, 0]
        returns_pct = (trades_df['pnl'] / trades_df['entry_price'] / trades_df['position_size']) * 100
        ax.hist(returns_pct, bins=30, alpha=0.7, edgecolor='black')
        ax.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        ax.axvline(x=returns_pct.mean(), color='green', linestyle='--', 
                  label=f'Mean: {returns_pct.mean():.2f}%')
        ax.set_title('Returns Distribution (%)', fontsize=14)
        ax.set_xlabel('Return %')
        ax.set_ylabel('Frequency')
        ax.legend()
        
        # 2. P&L distribution
        ax = axes[0, 1]
        ax.hist(trades_df['pnl'], bins=30, alpha=0.7, color='green', edgecolor='black')
        ax.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        ax.axvline(x=trades_df['pnl'].mean(), color='blue', linestyle='--',
                  label=f'Mean: ${trades_df["pnl"].mean():.2f}')
        ax.set_title('P&L Distribution ($)', fontsize=14)
        ax.set_xlabel('P&L ($)')
        ax.set_ylabel('Frequency')
        ax.legend()
        
        # 3. Win/Loss ratio pie chart
        ax = axes[1, 0]
        wins = len(trades_df[trades_df['pnl'] > 0])
        losses = len(trades_df[trades_df['pnl'] < 0])
        breakeven = len(trades_df[trades_df['pnl'] == 0])
        
        sizes = [wins, losses, breakeven] if breakeven > 0 else [wins, losses]
        labels = ['Wins', 'Losses', 'Breakeven'] if breakeven > 0 else ['Wins', 'Losses']
        colors = ['green', 'red', 'gray'] if breakeven > 0 else ['green', 'red']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title('Win/Loss Ratio', fontsize=14)
        
        # 4. Cumulative P&L
        ax = axes[1, 1]
        trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum()
        ax.plot(range(len(trades_df)), trades_df['cumulative_pnl'], linewidth=2)
        ax.fill_between(range(len(trades_df)), trades_df['cumulative_pnl'], 
                       alpha=0.3)
        ax.set_title('Cumulative P&L', fontsize=14)
        ax.set_xlabel('Trade Number')
        ax.set_ylabel('Cumulative P&L ($)')
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_trade_analysis(self, trades: List[Dict], save_path: str = None):
        """
        Plot detailed trade analysis
        """
        if not trades:
            return
            
        trades_df = pd.DataFrame(trades)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Trade duration analysis
        ax = axes[0, 0]
        durations_minutes = pd.to_timedelta(trades_df['duration']).dt.total_seconds() / 60
        ax.hist(durations_minutes, bins=30, alpha=0.7, edgecolor='black')
        ax.set_title('Trade Duration Distribution', fontsize=14)
        ax.set_xlabel('Duration (minutes)')
        ax.set_ylabel('Frequency')
        ax.axvline(x=durations_minutes.mean(), color='red', linestyle='--',
                  label=f'Avg: {durations_minutes.mean():.1f} min')
        ax.legend()
        
        # 2. P&L by exit reason
        ax = axes[0, 1]
        exit_reasons = trades_df.groupby('exit_reason')['pnl'].agg(['sum', 'count'])
        exit_reasons.plot(kind='bar', y='sum', ax=ax, legend=False)
        ax.set_title('P&L by Exit Reason', fontsize=14)
        ax.set_xlabel('Exit Reason')
        ax.set_ylabel('Total P&L ($)')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add count labels
        for i, (idx, row) in enumerate(exit_reasons.iterrows()):
            ax.text(i, row['sum'], f"n={row['count']}", ha='center', va='bottom')
        
        # 3. Win rate over time (rolling)
        ax = axes[1, 0]
        trades_df['is_win'] = trades_df['pnl'] > 0
        trades_df['rolling_win_rate'] = trades_df['is_win'].rolling(window=20, min_periods=1).mean()
        ax.plot(range(len(trades_df)), trades_df['rolling_win_rate'] * 100, linewidth=2)
        ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% line')
        ax.set_title('Rolling Win Rate (20 trades)', fontsize=14)
        ax.set_xlabel('Trade Number')
        ax.set_ylabel('Win Rate %')
        ax.set_ylim(0, 100)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 4. Long vs Short performance
        ax = axes[1, 1]
        direction_stats = trades_df.groupby('direction')['pnl'].agg(['sum', 'count', 'mean'])
        direction_stats.index = ['Short', 'Long']
        
        x = np.arange(len(direction_stats))
        width = 0.35
        
        ax.bar(x - width/2, direction_stats['sum'], width, label='Total P&L')
        ax.bar(x + width/2, direction_stats['mean'], width, label='Avg P&L')
        
        ax.set_title('Long vs Short Performance', fontsize=14)
        ax.set_xlabel('Direction')
        ax.set_xticks(x)
        ax.set_xticklabels(direction_stats.index)
        ax.set_ylabel('P&L ($)')
        ax.legend()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add count labels
        for i, (idx, row) in enumerate(direction_stats.iterrows()):
            ax.text(i, max(row['sum'], row['mean']) * 1.05, f"n={row['count']}", 
                   ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def create_interactive_chart(self, signals: pd.DataFrame, trades: List[Dict], 
                                equity_curve: pd.DataFrame, save_path: str = None):
        """
        Create interactive Plotly chart with signals and trades
        """
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=('Price & Signals', 'Indicators', 'Equity Curve')
        )
        
        # 1. Price candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=signals.index,
                open=signals['Open'],
                high=signals['High'],
                low=signals['Low'],
                close=signals['Close'],
                name='SPX',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Add buy/sell signals
        buy_signals = signals[signals['long_signal'] > 0]
        sell_signals = signals[signals['short_signal'] > 0]
        
        if not buy_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals.index,
                    y=buy_signals['Low'] * 0.995,
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=10, color='green'),
                    name='Buy Signal'
                ),
                row=1, col=1
            )
        
        if not sell_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals.index,
                    y=sell_signals['High'] * 1.005,
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=10, color='red'),
                    name='Sell Signal'
                ),
                row=1, col=1
            )
        
        # Add EMAs if available
        for col in signals.columns:
            if col.startswith('EMA_'):
                fig.add_trace(
                    go.Scatter(
                        x=signals.index,
                        y=signals[col],
                        mode='lines',
                        name=col,
                        line=dict(width=1)
                    ),
                    row=1, col=1
                )
        
        # 2. RSI indicator (if available)
        if 'RSI_14' in signals.columns:
            fig.add_trace(
                go.Scatter(
                    x=signals.index,
                    y=signals['RSI_14'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple', width=2)
                ),
                row=2, col=1
            )
            
            # Add overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         opacity=0.5, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         opacity=0.5, row=2, col=1)
        
        # 3. Equity curve
        fig.add_trace(
            go.Scatter(
                x=equity_curve['timestamp'],
                y=equity_curve['equity'],
                mode='lines',
                name='Equity',
                fill='tozeroy',
                line=dict(color='blue', width=2)
            ),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            title='SPX Trading Strategy - Interactive Analysis',
            xaxis_title='Date',
            height=1000,
            showlegend=True,
            hovermode='x unified'
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="Equity ($)", row=3, col=1)
        
        # Update x-axis to remove range slider from candlestick
        fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
        
        if save_path:
            fig.write_html(save_path)
        else:
            fig.show()
    
    def generate_text_report(self, metrics: Dict, trades: List[Dict], save_path: str = None):
        """
        Generate comprehensive text report
        """
        report_lines = []
        
        # Header
        report_lines.append("="*80)
        report_lines.append("SPX TRADING STRATEGY - BACKTEST REPORT")
        report_lines.append("="*80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Performance Summary
        report_lines.append("PERFORMANCE SUMMARY")
        report_lines.append("-"*80)
        report_lines.append(f"Initial Capital: ${metrics.get('initial_capital', 100000):,.2f}")
        report_lines.append(f"Final Equity: ${metrics['final_equity']:,.2f}")
        report_lines.append(f"Total Return: {metrics['total_return']:.2%}")
        report_lines.append(f"Annual Return: {metrics['annual_return']:.2%}")
        report_lines.append(f"Total P&L: ${metrics['total_pnl']:,.2f}")
        report_lines.append("")
        
        # Trade Statistics
        report_lines.append("TRADE STATISTICS")
        report_lines.append("-"*80)
        report_lines.append(f"Total Trades: {metrics['total_trades']}")
        report_lines.append(f"Winning Trades: {metrics['winning_trades']}")
        report_lines.append(f"Losing Trades: {metrics['losing_trades']}")
        report_lines.append(f"Win Rate: {metrics['win_rate']:.2%}")
        report_lines.append(f"Average Win: ${metrics['avg_win']:,.2f}")
        report_lines.append(f"Average Loss: ${metrics['avg_loss']:,.2f}")
        report_lines.append(f"Expected Value: ${metrics['expected_value']:,.2f} ({metrics['expected_value_pct']:.2%})")
        report_lines.append(f"Max Win Streak: {metrics['max_win_streak']}")
        report_lines.append(f"Max Loss Streak: {metrics['max_loss_streak']}")
        report_lines.append(f"Average Trade Duration: {metrics['avg_trade_duration']}")
        report_lines.append("")
        
        # Risk Metrics
        report_lines.append("RISK METRICS")
        report_lines.append("-"*80)
        report_lines.append(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        report_lines.append(f"Profit Factor: {metrics['profit_factor']:.2f}")
        report_lines.append(f"Maximum Drawdown: {metrics['max_drawdown']:.2%}")
        report_lines.append(f"Calmar Ratio: {metrics['calmar_ratio']:.2f}")
        report_lines.append(f"Recovery Factor: {metrics['recovery_factor']:.2f}")
        report_lines.append(f"Average Risk per Trade: {metrics['avg_risk_per_trade']:.2%}")
        report_lines.append("")
        
        # Performance Targets
        report_lines.append("PERFORMANCE TARGETS")
        report_lines.append("-"*80)
        report_lines.append(f"Win Rate Target (>50%): {'✓ PASS' if metrics['meets_win_rate_target'] else '✗ FAIL'}")
        report_lines.append(f"Profit Factor Target (>1.5): {'✓ PASS' if metrics['meets_profit_factor_target'] else '✗ FAIL'}")
        report_lines.append(f"Sharpe Ratio Target (>1.0): {'✓ PASS' if metrics['meets_sharpe_target'] else '✗ FAIL'}")
        report_lines.append(f"Annual Return Target (>10%): {'✓ PASS' if metrics['meets_return_target'] else '✗ FAIL'}")
        report_lines.append(f"Max Drawdown Target (<20%): {'✓ PASS' if metrics['meets_drawdown_target'] else '✗ FAIL'}")
        report_lines.append("")
        
        # Top 10 Trades
        if trades:
            report_lines.append("TOP 10 WINNING TRADES")
            report_lines.append("-"*80)
            trades_df = pd.DataFrame(trades)
            top_trades = trades_df.nlargest(10, 'pnl')
            
            for idx, trade in top_trades.iterrows():
                report_lines.append(
                    f"{trade['timestamp']}: "
                    f"{'LONG' if trade['direction'] == 1 else 'SHORT'} "
                    f"@ ${trade['entry_price']:.2f} → ${trade['exit_price']:.2f} "
                    f"P&L: ${trade['pnl']:.2f} ({trade['exit_reason']})"
                )
            
            report_lines.append("")
            report_lines.append("TOP 10 LOSING TRADES")
            report_lines.append("-"*80)
            worst_trades = trades_df.nsmallest(10, 'pnl')
            
            for idx, trade in worst_trades.iterrows():
                report_lines.append(
                    f"{trade['timestamp']}: "
                    f"{'LONG' if trade['direction'] == 1 else 'SHORT'} "
                    f"@ ${trade['entry_price']:.2f} → ${trade['exit_price']:.2f} "
                    f"P&L: ${trade['pnl']:.2f} ({trade['exit_reason']})"
                )
        
        report_lines.append("")
        report_lines.append("="*80)
        report_lines.append("END OF REPORT")
        report_lines.append("="*80)
        
        # Save or print report
        report_text = '\n'.join(report_lines)
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report_text)
        else:
            print(report_text)


# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    
    sample_equity = pd.DataFrame({
        'timestamp': dates,
        'equity': 100000 + np.random.randn(len(dates)).cumsum() * 1000
    })
    
    sample_trades = [
        {
            'timestamp': '2024-01-05',
            'exit_timestamp': '2024-01-06',
            'direction': 1,
            'entry_price': 4000,
            'exit_price': 4020,
            'position_size': 10,
            'pnl': 200,
            'exit_reason': 'Take Profit',
            'duration': pd.Timedelta(hours=2)
        },
        {
            'timestamp': '2024-01-10',
            'exit_timestamp': '2024-01-10',
            'direction': -1,
            'entry_price': 4050,
            'exit_price': 4060,
            'position_size': 10,
            'pnl': -100,
            'exit_reason': 'Stop Loss',
            'duration': pd.Timedelta(minutes=45)
        }
    ]
    
    sample_metrics = {
        'total_trades': 2,
        'winning_trades': 1,
        'losing_trades': 1,
        'win_rate': 0.50,
        'total_pnl': 100,
        'total_return': 0.001,
        'annual_return': 0.012,
        'avg_win': 200,
        'avg_loss': 100,
        'expected_value': 50,
        'expected_value_pct': 0.0005,
        'sharpe_ratio': 1.2,
        'profit_factor': 2.0,
        'max_drawdown': 0.05,
        'calmar_ratio': 0.24,
        'recovery_factor': 2.0,
        'avg_risk_per_trade': 0.02,
        'avg_trade_duration': '1:22:30',
        'max_win_streak': 1,
        'max_loss_streak': 1,
        'final_equity': 100100,
        'meets_win_rate_target': True,
        'meets_profit_factor_target': True,
        'meets_sharpe_target': True,
        'meets_return_target': False,
        'meets_drawdown_target': True
    }
    
    # Generate report
    reporter = ReportGenerator()
    reporter.plot_equity_curve(sample_equity)
    reporter.plot_returns_distribution(sample_trades)
    reporter.generate_text_report(sample_metrics, sample_trades)