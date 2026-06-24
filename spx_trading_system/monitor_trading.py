#!/usr/bin/env python3
"""
Real-time Trading Monitor for IB SPX Trading System
Displays live performance metrics and trade activity
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import curses
from pathlib import Path


class TradingMonitor:
    """
    Real-time monitoring dashboard for trading activity
    """
    
    def __init__(self):
        self.log_file = "logs/ib_trading.log"
        self.trades_file = "logs/trades.csv"
        self.refresh_interval = 2  # seconds
        
    def read_recent_logs(self, minutes=10):
        """Read recent log entries"""
        if not Path(self.log_file).exists():
            return []
        
        recent_logs = []
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    # Parse timestamp from log
                    timestamp_str = line.split(' - ')[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    
                    if timestamp > cutoff_time:
                        recent_logs.append(line.strip())
                except:
                    continue
        
        return recent_logs[-20:]  # Last 20 entries
    
    def read_trades(self):
        """Read trade history"""
        if not Path(self.trades_file).exists():
            return pd.DataFrame()
        
        try:
            trades = pd.read_csv(self.trades_file, names=[
                'timestamp', 'symbol', 'action', 'quantity', 'price', 'commission'
            ])
            trades['timestamp'] = pd.to_datetime(trades['timestamp'])
            return trades
        except:
            return pd.DataFrame()
    
    def calculate_daily_pnl(self, trades):
        """Calculate daily P&L from trades"""
        if trades.empty:
            return 0, 0, 0
        
        today = datetime.now().date()
        today_trades = trades[trades['timestamp'].dt.date == today]
        
        if today_trades.empty:
            return 0, 0, 0
        
        # Simple P&L calculation (would need position tracking for accuracy)
        # This is a simplified version
        total_trades = len(today_trades)
        
        # Estimate based on commission (real P&L would come from IB)
        total_commission = today_trades['commission'].sum()
        
        return total_trades, -total_commission, 0  # Placeholder
    
    def format_dashboard(self, stdscr):
        """Create dashboard display"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Title
        title = "🤖 SPX Trading Bot Monitor"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stdscr.addstr(1, (width - len(timestamp)) // 2, timestamp)
        
        # Divider
        stdscr.addstr(2, 0, "=" * width)
        
        # Read data
        trades = self.read_trades()
        recent_logs = self.read_recent_logs()
        
        # Trading Statistics
        row = 4
        stdscr.addstr(row, 2, "📊 TRADING STATISTICS", curses.A_BOLD)
        row += 2
        
        # Today's performance
        today_trades, today_commission, today_pnl = self.calculate_daily_pnl(trades)
        
        stats = [
            f"Today's Trades: {today_trades}",
            f"Total Trades: {len(trades)}",
            f"Commission Paid: ${abs(today_commission):.2f}",
            f"Status: {'🟢 ACTIVE' if self.is_bot_running() else '🔴 STOPPED'}"
        ]
        
        for stat in stats:
            if row < height - 15:
                stdscr.addstr(row, 4, stat)
                row += 1
        
        # Recent Activity
        row += 2
        if row < height - 10:
            stdscr.addstr(row, 2, "📜 RECENT ACTIVITY", curses.A_BOLD)
            row += 2
        
        # Show recent logs
        for log in recent_logs[-8:]:  # Show last 8 logs
            if row < height - 5:
                # Color code by log level
                if 'ERROR' in log:
                    color = curses.color_pair(1)  # Red
                elif 'Trade executed' in log or 'BUY' in log or 'SELL' in log:
                    color = curses.color_pair(2)  # Green
                elif 'WARNING' in log:
                    color = curses.color_pair(3)  # Yellow
                else:
                    color = curses.color_pair(0)  # Default
                
                # Truncate long lines
                display_log = log[:width-6] if len(log) > width-6 else log
                try:
                    stdscr.addstr(row, 4, display_log, color)
                except:
                    pass
                row += 1
        
        # Instructions
        if row < height - 2:
            stdscr.addstr(height-2, 2, "Press 'q' to quit, 'r' to refresh", curses.A_DIM)
        
        stdscr.refresh()
    
    def is_bot_running(self):
        """Check if bot is actively running"""
        if not Path(self.log_file).exists():
            return False
        
        # Check if log was updated recently
        try:
            mod_time = datetime.fromtimestamp(os.path.getmtime(self.log_file))
            return (datetime.now() - mod_time).seconds < 30
        except:
            return False
    
    def run(self, stdscr):
        """Main monitoring loop"""
        # Set up colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)    # Error
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Trade
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Warning
        
        # Make getch non-blocking
        stdscr.nodelay(True)
        
        while True:
            try:
                self.format_dashboard(stdscr)
                
                # Check for user input
                key = stdscr.getch()
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    continue
                
                time.sleep(self.refresh_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                stdscr.addstr(0, 0, f"Error: {str(e)}")
                time.sleep(2)


def print_simple_monitor():
    """Alternative simple monitoring without curses"""
    monitor = TradingMonitor()
    
    while True:
        try:
            os.system('clear' if os.name != 'nt' else 'cls')
            
            print("=" * 60)
            print("  🤖 SPX Trading Bot Monitor")
            print("=" * 60)
            print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            # Check status
            if monitor.is_bot_running():
                print("  Status: 🟢 ACTIVE")
            else:
                print("  Status: 🔴 STOPPED")
            
            # Read trades
            trades = monitor.read_trades()
            if not trades.empty:
                print(f"\n  Total Trades: {len(trades)}")
                
                # Today's trades
                today = datetime.now().date()
                today_trades = trades[trades['timestamp'].dt.date == today]
                print(f"  Today's Trades: {len(today_trades)}")
            
            # Recent logs
            print("\n  Recent Activity:")
            print("  " + "-" * 56)
            
            logs = monitor.read_recent_logs(5)
            for log in logs[-10:]:
                # Extract key info
                if 'Trade executed' in log or 'Signal' in log:
                    print(f"  ✓ {log[20:100]}")  # Skip timestamp
                elif 'ERROR' in log:
                    print(f"  ✗ {log[20:100]}")
                elif 'Position closed' in log:
                    print(f"  💰 {log[20:100]}")
            
            print("\n  Press Ctrl+C to exit...")
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            break


def main():
    """Main entry point"""
    print("Starting Trading Monitor...")
    
    # Check if logs exist
    if not Path("logs/ib_trading.log").exists():
        print("⚠️  No log file found. Is the trading bot running?")
        print("   Expected log file: logs/ib_trading.log")
        return
    
    # Try curses interface, fall back to simple
    try:
        curses.wrapper(TradingMonitor().run)
    except:
        # Fall back to simple monitoring
        print("Using simple monitoring mode...")
        print_simple_monitor()


if __name__ == "__main__":
    main()