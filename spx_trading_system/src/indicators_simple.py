"""
Simplified Technical Indicators Module for SPX Trading System
Implements indicators without TA-Lib dependency
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional


class TechnicalIndicators:
    """
    Class containing simplified technical indicator calculations
    """
    
    def __init__(self):
        self.indicators = {}
        
    def calculate_all_indicators(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """
        Calculate all indicators based on provided parameters
        
        Args:
            df: DataFrame with OHLCV data
            params: Dictionary with indicator parameters
            
        Returns:
            DataFrame with all indicators added
        """
        # Make a copy to avoid modifying original
        data = df.copy()
        
        # Calculate each indicator type
        if 'RSI' in params:
            for period in params['RSI']['periods']:
                data = self.add_rsi(data, period)
                
        if 'EMA' in params:
            for short in params['EMA']['short_periods']:
                data = self.add_ema(data, short, prefix=f'EMA_{short}')
            for long in params['EMA']['long_periods']:
                data = self.add_ema(data, long, prefix=f'EMA_{long}')
                
        if 'MACD' in params:
            for fast in params['MACD']['fast']:
                for slow in params['MACD']['slow']:
                    for signal in params['MACD']['signal']:
                        data = self.add_macd(data, fast, slow, signal)
                        
        if 'Bollinger_Bands' in params:
            for period in params['Bollinger_Bands']['periods']:
                for std in params['Bollinger_Bands']['std_dev']:
                    data = self.add_bollinger_bands(data, period, std)
                    
        if 'ATR' in params:
            for period in params['ATR']['periods']:
                data = self.add_atr(data, period)
        
        # Add additional indicators
        data = self.add_sma(data, [20, 50, 200])
        
        return data
    
    def add_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Add Relative Strength Index
        """
        close_delta = df['Close'].diff()
        gain = close_delta.where(close_delta > 0, 0)
        loss = -close_delta.where(close_delta < 0, 0)
        
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        df[f'RSI_{period}'] = rsi
        return df
    
    def add_ema(self, df: pd.DataFrame, period: int, prefix: str = None) -> pd.DataFrame:
        """
        Add Exponential Moving Average
        """
        col_name = prefix if prefix else f'EMA_{period}'
        df[col_name] = df['Close'].ewm(span=period, adjust=False).mean()
        return df
    
    def add_sma(self, df: pd.DataFrame, periods: list) -> pd.DataFrame:
        """
        Add Simple Moving Averages
        """
        for period in periods:
            df[f'SMA_{period}'] = df['Close'].rolling(window=period, min_periods=1).mean()
        return df
    
    def add_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, 
                 signal: int = 9) -> pd.DataFrame:
        """
        Add MACD indicator
        """
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        macd_hist = macd_line - signal_line
        
        # Add columns with parameter-specific names
        prefix = f'MACD_{fast}_{slow}_{signal}'
        df[f'{prefix}'] = macd_line
        df[f'{prefix}_signal'] = signal_line
        df[f'{prefix}_hist'] = macd_hist
        
        return df
    
    def add_bollinger_bands(self, df: pd.DataFrame, period: int = 20, 
                           std_dev: float = 2) -> pd.DataFrame:
        """
        Add Bollinger Bands
        """
        sma = df['Close'].rolling(window=period, min_periods=1).mean()
        std = df['Close'].rolling(window=period, min_periods=1).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        # Add with unique names based on parameters
        prefix = f'BB_{period}_{std_dev}'
        df[f'{prefix}_upper'] = upper_band
        df[f'{prefix}_middle'] = sma
        df[f'{prefix}_lower'] = lower_band
        df[f'{prefix}_bandwidth'] = (upper_band - lower_band) / sma
        df[f'{prefix}_percent'] = (df['Close'] - lower_band) / (upper_band - lower_band)
        
        return df
    
    def add_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Add Average True Range
        """
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period, min_periods=1).mean()
        
        df[f'ATR_{period}'] = atr
        return df
    
    def add_stochastic(self, df: pd.DataFrame, k_period: int = 14, 
                      d_period: int = 3) -> pd.DataFrame:
        """
        Add Stochastic Oscillator
        """
        lowest_low = df['Low'].rolling(window=k_period, min_periods=1).min()
        highest_high = df['High'].rolling(window=k_period, min_periods=1).max()
        
        k_percent = 100 * ((df['Close'] - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period, min_periods=1).mean()
        
        df[f'Stoch_K_{k_period}'] = k_percent
        df[f'Stoch_D_{k_period}'] = d_percent
        
        return df
    
    def add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume-based indicators
        """
        # On-Balance Volume (OBV)
        obv = (df['Volume'] * (~df['Close'].diff().le(0) * 2 - 1)).cumsum()
        df['OBV'] = obv
        
        # Volume Weighted Average Price (VWAP) - simplified daily reset
        df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        
        # Money Flow Index (MFI) - simplified version
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(), 0)
        
        positive_flow_sum = positive_flow.rolling(window=14, min_periods=1).sum()
        negative_flow_sum = negative_flow.rolling(window=14, min_periods=1).sum()
        
        mfi = 100 - (100 / (1 + positive_flow_sum / negative_flow_sum))
        df['MFI'] = mfi
        
        return df
    
    def calculate_signals(self, df: pd.DataFrame, indicator_params: Dict) -> pd.DataFrame:
        """
        Calculate trading signals based on indicators
        """
        df['Signal'] = 0  # 0: No signal, 1: Buy, -1: Sell
        
        # RSI signals
        if 'RSI' in indicator_params:
            for period in indicator_params['RSI']['periods']:
                for oversold in indicator_params['RSI']['oversold']:
                    for overbought in indicator_params['RSI']['overbought']:
                        # Oversold signal (potential buy)
                        df.loc[df[f'RSI_{period}'] < oversold, f'RSI_{period}_signal'] = 1
                        # Overbought signal (potential sell)
                        df.loc[df[f'RSI_{period}'] > overbought, f'RSI_{period}_signal'] = -1
        
        # MACD signals
        if 'MACD' in indicator_params:
            for fast in indicator_params['MACD']['fast']:
                for slow in indicator_params['MACD']['slow']:
                    for signal in indicator_params['MACD']['signal']:
                        prefix = f'MACD_{fast}_{slow}_{signal}'
                        # Crossover signals
                        df[f'{prefix}_cross'] = np.where(
                            (df[prefix] > df[f'{prefix}_signal']) & 
                            (df[prefix].shift(1) <= df[f'{prefix}_signal'].shift(1)), 1,
                            np.where(
                                (df[prefix] < df[f'{prefix}_signal']) & 
                                (df[prefix].shift(1) >= df[f'{prefix}_signal'].shift(1)), -1, 0
                            )
                        )
        
        # Bollinger Bands signals
        if 'Bollinger_Bands' in indicator_params:
            for period in indicator_params['Bollinger_Bands']['periods']:
                for std in indicator_params['Bollinger_Bands']['std_dev']:
                    prefix = f'BB_{period}_{std}'
                    # Price touches lower band (potential buy)
                    df.loc[df['Close'] <= df[f'{prefix}_lower'], f'{prefix}_signal'] = 1
                    # Price touches upper band (potential sell)
                    df.loc[df['Close'] >= df[f'{prefix}_upper'], f'{prefix}_signal'] = -1
        
        # EMA crossover signals
        if 'EMA' in indicator_params:
            short_periods = indicator_params['EMA']['short_periods']
            long_periods = indicator_params['EMA']['long_periods']
            
            for short in short_periods:
                for long in long_periods:
                    if short < long:  # Ensure short is actually shorter
                        # Golden cross (short EMA crosses above long EMA)
                        df[f'EMA_{short}_{long}_cross'] = np.where(
                            (df[f'EMA_{short}'] > df[f'EMA_{long}']) & 
                            (df[f'EMA_{short}'].shift(1) <= df[f'EMA_{long}'].shift(1)), 1,
                            np.where(
                                (df[f'EMA_{short}'] < df[f'EMA_{long}']) & 
                                (df[f'EMA_{short}'].shift(1) >= df[f'EMA_{long}'].shift(1)), -1, 0
                            )
                        )
        
        return df