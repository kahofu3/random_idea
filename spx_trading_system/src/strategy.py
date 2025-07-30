"""
Trading Strategy Module for SPX Trading System
Implements entry/exit rules and position management
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, time
from typing import Dict, List, Tuple, Optional
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import TRADING_CONFIG, RISK_CONFIG, TRADING_RULES, TIME_FILTERS, INDICATOR_PARAMS

logger = logging.getLogger(__name__)


class TradingStrategy:
    """
    Main trading strategy class that combines indicators to generate signals
    """
    
    def __init__(self, capital: float = TRADING_CONFIG['initial_capital'],
                 risk_per_trade: float = RISK_CONFIG['risk_per_trade']):
        self.initial_capital = capital
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.positions = []
        self.trades = []
        self.current_position = None
        
    def generate_signals(self, df: pd.DataFrame, indicator_params: Dict) -> pd.DataFrame:
        """
        Generate trading signals based on multiple indicators
        
        Args:
            df: DataFrame with price data and indicators
            indicator_params: Parameters for signal generation
            
        Returns:
            DataFrame with signals added
        """
        # Initialize signal columns
        df['long_signal'] = 0
        df['short_signal'] = 0
        df['exit_signal'] = 0
        
        # Apply time filters
        df = self._apply_time_filters(df)
        
        # Generate signals for each indicator combination
        df = self._generate_rsi_signals(df, indicator_params)
        df = self._generate_macd_signals(df, indicator_params)
        df = self._generate_bollinger_signals(df, indicator_params)
        df = self._generate_ema_signals(df, indicator_params)
        
        # Combine signals
        df = self._combine_signals(df)
        
        # Add stop loss and take profit levels
        df = self._calculate_exit_levels(df, indicator_params)
        
        return df
    
    def _apply_time_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply time-based filters to avoid trading during specific periods
        """
        df['tradable_time'] = True
        
        # Get time from index
        times = pd.to_datetime(df.index).time
        
        # Avoid first N minutes of trading day
        start_time = time(9, 30 + TIME_FILTERS['avoid_first_minutes'] // 60, 
                         TIME_FILTERS['avoid_first_minutes'] % 60)
        
        # Avoid last N minutes of trading day
        end_hour = 16 - TIME_FILTERS['avoid_last_minutes'] // 60
        end_minute = 0 - TIME_FILTERS['avoid_last_minutes'] % 60
        if end_minute < 0:
            end_minute = 60 + end_minute
            end_hour -= 1
        end_time = time(end_hour, end_minute)
        
        # Mark non-tradable times
        for i, t in enumerate(times):
            if t < start_time or t > end_time:
                df.iloc[i, df.columns.get_loc('tradable_time')] = False
                
        return df
    
    def _generate_rsi_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """
        Generate RSI-based signals
        """
        if 'RSI' not in params:
            return df
            
        for period in params['RSI']['periods']:
            for oversold in params['RSI']['oversold']:
                for overbought in params['RSI']['overbought']:
                    col_name = f'RSI_{period}'
                    if col_name in df.columns:
                        # Long signal when RSI crosses above oversold
                        df[f'{col_name}_long'] = (
                            (df[col_name] > oversold) & 
                            (df[col_name].shift(1) <= oversold) &
                            df['tradable_time']
                        ).astype(int)
                        
                        # Short signal when RSI crosses below overbought
                        df[f'{col_name}_short'] = (
                            (df[col_name] < overbought) & 
                            (df[col_name].shift(1) >= overbought) &
                            df['tradable_time']
                        ).astype(int)
                        
        return df
    
    def _generate_macd_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """
        Generate MACD-based signals
        """
        if 'MACD' not in params:
            return df
            
        for fast in params['MACD']['fast']:
            for slow in params['MACD']['slow']:
                for signal in params['MACD']['signal']:
                    prefix = f'MACD_{fast}_{slow}_{signal}'
                    
                    if prefix in df.columns:
                        # MACD line crosses above signal line (bullish)
                        df[f'{prefix}_long'] = (
                            (df[prefix] > df[f'{prefix}_signal']) & 
                            (df[prefix].shift(1) <= df[f'{prefix}_signal'].shift(1)) &
                            df['tradable_time']
                        ).astype(int)
                        
                        # MACD line crosses below signal line (bearish)
                        df[f'{prefix}_short'] = (
                            (df[prefix] < df[f'{prefix}_signal']) & 
                            (df[prefix].shift(1) >= df[f'{prefix}_signal'].shift(1)) &
                            df['tradable_time']
                        ).astype(int)
                        
        return df
    
    def _generate_bollinger_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """
        Generate Bollinger Bands signals
        """
        if 'Bollinger_Bands' not in params:
            return df
            
        for period in params['Bollinger_Bands']['periods']:
            for std in params['Bollinger_Bands']['std_dev']:
                prefix = f'BB_{period}_{std}'
                
                if f'{prefix}_lower' in df.columns:
                    # Price touches lower band and starts to reverse (long)
                    df[f'{prefix}_long'] = (
                        (df['Close'] > df[f'{prefix}_lower']) & 
                        (df['Low'] <= df[f'{prefix}_lower']) &
                        (df['Close'] > df['Open']) &  # Bullish candle
                        df['tradable_time']
                    ).astype(int)
                    
                    # Price touches upper band and starts to reverse (short)
                    df[f'{prefix}_short'] = (
                        (df['Close'] < df[f'{prefix}_upper']) & 
                        (df['High'] >= df[f'{prefix}_upper']) &
                        (df['Close'] < df['Open']) &  # Bearish candle
                        df['tradable_time']
                    ).astype(int)
                    
        return df
    
    def _generate_ema_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """
        Generate EMA crossover signals
        """
        if 'EMA' not in params:
            return df
            
        short_periods = params['EMA']['short_periods']
        long_periods = params['EMA']['long_periods']
        
        for short in short_periods:
            for long in long_periods:
                if short < long:
                    short_col = f'EMA_{short}'
                    long_col = f'EMA_{long}'
                    
                    if short_col in df.columns and long_col in df.columns:
                        # Golden cross (short EMA crosses above long EMA)
                        df[f'EMA_{short}_{long}_long'] = (
                            (df[short_col] > df[long_col]) & 
                            (df[short_col].shift(1) <= df[long_col].shift(1)) &
                            df['tradable_time']
                        ).astype(int)
                        
                        # Death cross (short EMA crosses below long EMA)
                        df[f'EMA_{short}_{long}_short'] = (
                            (df[short_col] < df[long_col]) & 
                            (df[short_col].shift(1) >= df[long_col].shift(1)) &
                            df['tradable_time']
                        ).astype(int)
                        
        return df
    
    def _combine_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Combine signals from multiple indicators
        """
        # Get all long signal columns
        long_signal_cols = [col for col in df.columns if col.endswith('_long')]
        short_signal_cols = [col for col in df.columns if col.endswith('_short')]
        
        # Calculate signal strength (number of confirming indicators)
        df['long_strength'] = df[long_signal_cols].sum(axis=1) if long_signal_cols else 0
        df['short_strength'] = df[short_signal_cols].sum(axis=1) if short_signal_cols else 0
        
        # Generate final signals based on minimum confirmations
        min_confirmations = 2  # Require at least 2 indicators to agree
        
        df['long_signal'] = (df['long_strength'] >= min_confirmations).astype(int)
        df['short_signal'] = (df['short_strength'] >= min_confirmations).astype(int)
        
        # Ensure no conflicting signals
        df.loc[df['long_signal'] & df['short_signal'], 'long_signal'] = 0
        df.loc[df['long_signal'] & df['short_signal'], 'short_signal'] = 0
        
        return df
    
    def _calculate_exit_levels(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """
        Calculate stop loss and take profit levels
        """
        # Use ATR for dynamic stop loss if available
        atr_col = None
        if 'ATR' in params and params['ATR']['periods']:
            atr_col = f"ATR_{params['ATR']['periods'][0]}"
            
        if atr_col and atr_col in df.columns:
            # Dynamic stop loss based on ATR
            df['stop_loss_distance'] = df[atr_col] * 2  # 2x ATR
        else:
            # Fixed percentage stop loss
            df['stop_loss_distance'] = df['Close'] * TRADING_RULES['exit_rules']['stop_loss_pct']
            
        # Calculate take profit based on risk-reward ratio
        df['take_profit_distance'] = df['stop_loss_distance'] * TRADING_RULES['exit_rules']['take_profit_ratio']
        
        return df
    
    def calculate_position_size(self, price: float, stop_loss: float, 
                               capital: float = None) -> int:
        """
        Calculate position size based on risk management rules
        
        Args:
            price: Entry price
            stop_loss: Stop loss price
            capital: Available capital (uses self.capital if not provided)
            
        Returns:
            Number of shares to trade
        """
        if capital is None:
            capital = self.capital
            
        # Calculate risk amount
        risk_amount = capital * self.risk_per_trade
        
        # Calculate position size
        risk_per_share = abs(price - stop_loss)
        
        if risk_per_share > 0:
            position_size = int(risk_amount / risk_per_share)
            
            # Ensure position size doesn't exceed available capital
            max_position_size = int(capital / price)
            position_size = min(position_size, max_position_size)
            
            return position_size
        else:
            return 0
    
    def execute_trade(self, timestamp: pd.Timestamp, signal: int, price: float,
                     stop_loss: float, take_profit: float) -> Dict:
        """
        Execute a trade with proper risk management
        
        Args:
            timestamp: Trade timestamp
            signal: 1 for long, -1 for short
            price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Trade details dictionary
        """
        # Close existing position if opposite signal
        if self.current_position and self.current_position['direction'] != signal:
            self.close_position(timestamp, price, 'Signal Reversal')
            
        # Calculate position size
        position_size = self.calculate_position_size(price, stop_loss)
        
        if position_size > 0:
            trade = {
                'timestamp': timestamp,
                'direction': signal,
                'entry_price': price,
                'position_size': position_size,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'status': 'open'
            }
            
            self.current_position = trade
            self.trades.append(trade)
            
            logger.info(f"Trade executed: {signal} {position_size} shares at {price}")
            
            return trade
        else:
            logger.warning(f"Position size is 0, trade not executed")
            return None
    
    def close_position(self, timestamp: pd.Timestamp, price: float, reason: str) -> Dict:
        """
        Close current position
        
        Args:
            timestamp: Close timestamp
            price: Exit price
            reason: Reason for closing
            
        Returns:
            Closed trade details
        """
        if not self.current_position:
            return None
            
        # Calculate P&L
        if self.current_position['direction'] == 1:  # Long
            pnl = (price - self.current_position['entry_price']) * self.current_position['position_size']
        else:  # Short
            pnl = (self.current_position['entry_price'] - price) * self.current_position['position_size']
            
        # Update trade record
        self.current_position['exit_timestamp'] = timestamp
        self.current_position['exit_price'] = price
        self.current_position['pnl'] = pnl
        self.current_position['exit_reason'] = reason
        self.current_position['status'] = 'closed'
        
        # Update capital
        self.capital += pnl
        
        logger.info(f"Position closed: {reason} at {price}, P&L: ${pnl:.2f}")
        
        closed_trade = self.current_position
        self.current_position = None
        
        return closed_trade
    
    def check_exit_conditions(self, timestamp: pd.Timestamp, current_price: float,
                            high: float, low: float) -> Tuple[bool, str]:
        """
        Check if position should be closed
        
        Args:
            timestamp: Current timestamp
            current_price: Current price
            high: High price of current bar
            low: Low price of current bar
            
        Returns:
            Tuple of (should_exit, reason)
        """
        if not self.current_position:
            return False, ""
            
        # Check stop loss
        if self.current_position['direction'] == 1:  # Long
            if low <= self.current_position['stop_loss']:
                return True, "Stop Loss"
        else:  # Short
            if high >= self.current_position['stop_loss']:
                return True, "Stop Loss"
                
        # Check take profit
        if self.current_position['direction'] == 1:  # Long
            if high >= self.current_position['take_profit']:
                return True, "Take Profit"
        else:  # Short
            if low <= self.current_position['take_profit']:
                return True, "Take Profit"
                
        # Check end of day exit
        if TRADING_RULES['exit_rules']['end_of_day_exit']:
            current_time = pd.to_datetime(timestamp).time()
            if current_time >= time(15, 55):  # Close 5 minutes before market close
                return True, "End of Day"
                
        return False, ""
    
    def update_trailing_stop(self, current_price: float):
        """
        Update trailing stop loss for current position
        """
        if not self.current_position or not TRADING_RULES['exit_rules']['trailing_stop']:
            return
            
        if self.current_position['direction'] == 1:  # Long
            # Move stop loss up but never down
            new_stop = current_price - (self.current_position['entry_price'] - 
                                       self.current_position['stop_loss'])
            if new_stop > self.current_position['stop_loss']:
                self.current_position['stop_loss'] = new_stop
                logger.debug(f"Trailing stop updated to {new_stop}")
                
        else:  # Short
            # Move stop loss down but never up
            new_stop = current_price + (self.current_position['stop_loss'] - 
                                       self.current_position['entry_price'])
            if new_stop < self.current_position['stop_loss']:
                self.current_position['stop_loss'] = new_stop
                logger.debug(f"Trailing stop updated to {new_stop}")


# Example usage
if __name__ == "__main__":
    strategy = TradingStrategy()
    
    print(f"Initial capital: ${strategy.initial_capital}")
    print(f"Risk per trade: {strategy.risk_per_trade * 100}%")
    
    # Test position sizing
    entry_price = 4000
    stop_loss = 3980
    position_size = strategy.calculate_position_size(entry_price, stop_loss)
    
    print(f"\nPosition sizing example:")
    print(f"Entry price: ${entry_price}")
    print(f"Stop loss: ${stop_loss}")
    print(f"Position size: {position_size} shares")
    print(f"Total value: ${position_size * entry_price}")
    print(f"Risk amount: ${position_size * (entry_price - stop_loss)}")