"""
Backtesting Module for SPX Trading System
Simulates trading and calculates performance metrics
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import TRADING_CONFIG, PERFORMANCE_TARGETS, BACKTEST_CONFIG
from src.data_handler import DataHandler
from src.indicators import TechnicalIndicators
from src.strategy import TradingStrategy

logger = logging.getLogger(__name__)


class Backtester:
    """
    Backtesting engine for trading strategies
    """
    
    def __init__(self, strategy: TradingStrategy, initial_capital: float = TRADING_CONFIG['initial_capital']):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.equity_curve = []
        self.trades = []
        self.metrics = {}
        
    def run_backtest(self, data: pd.DataFrame, indicator_params: Dict) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            data: DataFrame with price data and indicators
            indicator_params: Parameters for indicators and signals
            
        Returns:
            Dictionary with backtest results
        """
        logger.info("Starting backtest...")
        
        # Reset strategy state
        self.strategy.capital = self.initial_capital
        self.strategy.trades = []
        self.strategy.current_position = None
        
        # Generate signals
        data_with_signals = self.strategy.generate_signals(data, indicator_params)
        
        # Initialize tracking variables
        self.equity_curve = [{'timestamp': data.index[0], 'equity': self.initial_capital}]
        
        # Simulate trading
        for i in tqdm(range(1, len(data_with_signals)), desc="Backtesting"):
            timestamp = data_with_signals.index[i]
            row = data_with_signals.iloc[i]
            prev_row = data_with_signals.iloc[i-1]
            
            # Update trailing stop if in position
            if self.strategy.current_position:
                self.strategy.update_trailing_stop(row['Close'])
                
                # Check exit conditions
                should_exit, exit_reason = self.strategy.check_exit_conditions(
                    timestamp, row['Close'], row['High'], row['Low']
                )
                
                if should_exit:
                    exit_price = self._calculate_exit_price(
                        row, self.strategy.current_position, exit_reason
                    )
                    self.strategy.close_position(timestamp, exit_price, exit_reason)
            
            # Check for new signals (only if not in position)
            if not self.strategy.current_position:
                if row['long_signal'] > 0 and prev_row['long_signal'] == 0:
                    # Long entry
                    stop_loss = row['Close'] - row['stop_loss_distance']
                    take_profit = row['Close'] + row['take_profit_distance']
                    
                    self.strategy.execute_trade(
                        timestamp, 1, row['Close'], stop_loss, take_profit
                    )
                    
                elif row['short_signal'] > 0 and prev_row['short_signal'] == 0:
                    # Short entry
                    stop_loss = row['Close'] + row['stop_loss_distance']
                    take_profit = row['Close'] - row['take_profit_distance']
                    
                    self.strategy.execute_trade(
                        timestamp, -1, row['Close'], stop_loss, take_profit
                    )
            
            # Track equity
            current_equity = self._calculate_current_equity(row['Close'])
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': current_equity
            })
        
        # Close any remaining position at the end
        if self.strategy.current_position:
            last_price = data_with_signals.iloc[-1]['Close']
            self.strategy.close_position(data_with_signals.index[-1], last_price, "End of Backtest")
        
        # Calculate performance metrics
        self.trades = [t for t in self.strategy.trades if t['status'] == 'closed']
        self.metrics = self.calculate_performance_metrics()
        
        logger.info(f"Backtest completed. Total trades: {len(self.trades)}")
        
        return {
            'metrics': self.metrics,
            'trades': self.trades,
            'equity_curve': pd.DataFrame(self.equity_curve),
            'signals': data_with_signals
        }
    
    def _calculate_exit_price(self, row: pd.Series, position: Dict, exit_reason: str) -> float:
        """
        Calculate the actual exit price based on exit reason
        """
        if exit_reason == "Stop Loss":
            return position['stop_loss']
        elif exit_reason == "Take Profit":
            return position['take_profit']
        else:
            return row['Close']
    
    def _calculate_current_equity(self, current_price: float) -> float:
        """
        Calculate current account equity including open position
        """
        equity = self.strategy.capital
        
        if self.strategy.current_position:
            # Calculate unrealized P&L
            position = self.strategy.current_position
            if position['direction'] == 1:  # Long
                unrealized_pnl = (current_price - position['entry_price']) * position['position_size']
            else:  # Short
                unrealized_pnl = (position['entry_price'] - current_price) * position['position_size']
            
            equity += unrealized_pnl
            
        return equity
    
    def calculate_performance_metrics(self) -> Dict:
        """
        Calculate comprehensive performance metrics
        """
        if not self.trades:
            return self._empty_metrics()
        
        # Convert trades to DataFrame for easier analysis
        trades_df = pd.DataFrame(self.trades)
        equity_df = pd.DataFrame(self.equity_curve)
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = trades_df['pnl'].sum()
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 0
        
        # Expected value
        expected_value = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        # Profit factor
        gross_profit = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Returns
        total_return = (equity_df['equity'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # Calculate daily returns for Sharpe ratio
        equity_df['returns'] = equity_df['equity'].pct_change()
        
        # Sharpe ratio (assuming 252 trading days)
        daily_returns = equity_df['returns'].dropna()
        if len(daily_returns) > 1:
            sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std()
        else:
            sharpe_ratio = 0
        
        # Maximum drawdown
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = abs(equity_df['drawdown'].min())
        
        # Trade duration
        trades_df['duration'] = pd.to_datetime(trades_df['exit_timestamp']) - pd.to_datetime(trades_df['timestamp'])
        avg_trade_duration = trades_df['duration'].mean()
        
        # Win/Loss streaks
        trades_df['is_win'] = trades_df['pnl'] > 0
        win_streak = self._calculate_max_streak(trades_df['is_win'].values, True)
        loss_streak = self._calculate_max_streak(trades_df['is_win'].values, False)
        
        # Calmar ratio (annual return / max drawdown)
        days_in_backtest = (equity_df['timestamp'].iloc[-1] - equity_df['timestamp'].iloc[0]).days
        annual_return = total_return * (365 / days_in_backtest) if days_in_backtest > 0 else 0
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0
        
        # Risk metrics
        avg_risk_per_trade = trades_df.apply(
            lambda x: abs(x['entry_price'] - x['stop_loss']) * x['position_size'] / self.initial_capital,
            axis=1
        ).mean()
        
        # Recovery factor
        recovery_factor = total_pnl / (max_drawdown * self.initial_capital) if max_drawdown > 0 else 0
        
        # Build metrics dictionary
        metrics = {
            # Trade statistics
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            
            # P&L metrics
            'total_pnl': total_pnl,
            'total_return': total_return,
            'annual_return': annual_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'expected_value': expected_value,
            'expected_value_pct': expected_value / self.initial_capital if self.initial_capital > 0 else 0,
            
            # Risk-adjusted returns
            'sharpe_ratio': sharpe_ratio,
            'profit_factor': profit_factor,
            'calmar_ratio': calmar_ratio,
            'recovery_factor': recovery_factor,
            
            # Risk metrics
            'max_drawdown': max_drawdown,
            'avg_risk_per_trade': avg_risk_per_trade,
            
            # Trade duration
            'avg_trade_duration': str(avg_trade_duration),
            'max_win_streak': win_streak,
            'max_loss_streak': loss_streak,
            
            # Final equity
            'final_equity': equity_df['equity'].iloc[-1],
            
            # Success criteria
            'meets_win_rate_target': win_rate >= PERFORMANCE_TARGETS['min_win_rate'],
            'meets_profit_factor_target': profit_factor >= PERFORMANCE_TARGETS['min_profit_factor'],
            'meets_sharpe_target': sharpe_ratio >= PERFORMANCE_TARGETS['min_sharpe_ratio'],
            'meets_return_target': annual_return >= PERFORMANCE_TARGETS['min_annual_return'],
            'meets_drawdown_target': max_drawdown <= PERFORMANCE_TARGETS['max_drawdown']
        }
        
        return metrics
    
    def _calculate_max_streak(self, wins: np.ndarray, win_value: bool) -> int:
        """
        Calculate maximum winning or losing streak
        """
        streak = 0
        max_streak = 0
        
        for win in wins:
            if win == win_value:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
                
        return max_streak
    
    def _empty_metrics(self) -> Dict:
        """
        Return empty metrics when no trades
        """
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'total_return': 0,
            'annual_return': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'expected_value': 0,
            'expected_value_pct': 0,
            'sharpe_ratio': 0,
            'profit_factor': 0,
            'calmar_ratio': 0,
            'recovery_factor': 0,
            'max_drawdown': 0,
            'avg_risk_per_trade': 0,
            'avg_trade_duration': 'N/A',
            'max_win_streak': 0,
            'max_loss_streak': 0,
            'final_equity': self.initial_capital,
            'meets_win_rate_target': False,
            'meets_profit_factor_target': False,
            'meets_sharpe_target': False,
            'meets_return_target': False,
            'meets_drawdown_target': True
        }
    
    def print_summary(self):
        """
        Print a summary of backtest results
        """
        if not self.metrics:
            print("No backtest results available")
            return
            
        print("\n" + "="*60)
        print("BACKTEST SUMMARY")
        print("="*60)
        
        print(f"\nTrade Statistics:")
        print(f"  Total Trades: {self.metrics['total_trades']}")
        print(f"  Winning Trades: {self.metrics['winning_trades']}")
        print(f"  Losing Trades: {self.metrics['losing_trades']}")
        print(f"  Win Rate: {self.metrics['win_rate']:.2%}")
        
        print(f"\nReturns:")
        print(f"  Total P&L: ${self.metrics['total_pnl']:,.2f}")
        print(f"  Total Return: {self.metrics['total_return']:.2%}")
        print(f"  Annual Return: {self.metrics['annual_return']:.2%}")
        print(f"  Expected Value per Trade: ${self.metrics['expected_value']:.2f} ({self.metrics['expected_value_pct']:.2%})")
        
        print(f"\nRisk Metrics:")
        print(f"  Sharpe Ratio: {self.metrics['sharpe_ratio']:.2f}")
        print(f"  Profit Factor: {self.metrics['profit_factor']:.2f}")
        print(f"  Max Drawdown: {self.metrics['max_drawdown']:.2%}")
        print(f"  Calmar Ratio: {self.metrics['calmar_ratio']:.2f}")
        
        print(f"\nPerformance Targets:")
        print(f"  Win Rate Target Met: {'✓' if self.metrics['meets_win_rate_target'] else '✗'}")
        print(f"  Profit Factor Target Met: {'✓' if self.metrics['meets_profit_factor_target'] else '✗'}")
        print(f"  Sharpe Ratio Target Met: {'✓' if self.metrics['meets_sharpe_target'] else '✗'}")
        print(f"  Annual Return Target Met: {'✓' if self.metrics['meets_return_target'] else '✗'}")
        print(f"  Max Drawdown Target Met: {'✓' if self.metrics['meets_drawdown_target'] else '✗'}")
        
        print("\n" + "="*60)


# Example usage
if __name__ == "__main__":
    # Initialize components
    data_handler = DataHandler()
    indicators = TechnicalIndicators()
    strategy = TradingStrategy()
    backtester = Backtester(strategy)
    
    # Load sample data
    print("Loading data...")
    data = data_handler.fetch_data(
        interval='5m',
        start_date='2024-01-01',
        end_date='2024-01-31'
    )
    
    # Add indicators
    print("Calculating indicators...")
    params = {
        'RSI': {'periods': [14], 'oversold': [30], 'overbought': [70]},
        'EMA': {'short_periods': [10], 'long_periods': [50]},
        'MACD': {'fast': [12], 'slow': [26], 'signal': [9]},
        'Bollinger_Bands': {'periods': [20], 'std_dev': [2]},
        'ATR': {'periods': [14]}
    }
    
    data_with_indicators = indicators.calculate_all_indicators(data, params)
    
    # Run backtest
    print("Running backtest...")
    results = backtester.run_backtest(data_with_indicators, params)
    
    # Print summary
    backtester.print_summary()