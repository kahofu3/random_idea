"""
Technical Indicators Module for SPX Trading System
Implements various technical indicators for signal generation
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import pandas_ta as ta


class TechnicalIndicators:
    """
    Class containing all technical indicator calculations
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
        data = self.add_stochastic(data)
        data = self.add_volume_indicators(data)
        
        return data
    
    def add_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Add Relative Strength Index
        """
        df[f'RSI_{period}'] = ta.rsi(df['Close'], length=period)
        return df
    
    def add_ema(self, df: pd.DataFrame, period: int, prefix: str = None) -> pd.DataFrame:
        """
        Add Exponential Moving Average
        """
        col_name = prefix if prefix else f'EMA_{period}'
        df[col_name] = ta.ema(df['Close'], length=period)
        return df
    
    def add_sma(self, df: pd.DataFrame, periods: list) -> pd.DataFrame:
        """
        Add Simple Moving Averages
        """
        for period in periods:
            df[f'SMA_{period}'] = ta.sma(df['Close'], length=period)
        return df
    
    def add_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, 
                 signal: int = 9) -> pd.DataFrame:
        """
        Add MACD indicator
        """
        macd_result = ta.macd(df['Close'], fast=fast, slow=slow, signal=signal)
        
        # Rename columns with parameters for uniqueness
        prefix = f'MACD_{fast}_{slow}_{signal}'
        df[f'{prefix}'] = macd_result[f'MACD_{fast}_{slow}_{signal}']
        df[f'{prefix}_signal'] = macd_result[f'MACDs_{fast}_{slow}_{signal}']
        df[f'{prefix}_hist'] = macd_result[f'MACDh_{fast}_{slow}_{signal}']
        
        return df
    
    def add_bollinger_bands(self, df: pd.DataFrame, period: int = 20, 
                           std_dev: float = 2) -> pd.DataFrame:
        """
        Add Bollinger Bands
        """
        bb_result = ta.bbands(df['Close'], length=period, std=std_dev)
        
        # Add with unique names based on parameters
        prefix = f'BB_{period}_{std_dev}'
        df[f'{prefix}_upper'] = bb_result[f'BBU_{period}_{std_dev}']
        df[f'{prefix}_middle'] = bb_result[f'BBM_{period}_{std_dev}']
        df[f'{prefix}_lower'] = bb_result[f'BBL_{period}_{std_dev}']
        df[f'{prefix}_bandwidth'] = bb_result[f'BBB_{period}_{std_dev}']
        df[f'{prefix}_percent'] = bb_result[f'BBP_{period}_{std_dev}']
        
        return df
    
    def add_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Add Average True Range
        """
        df[f'ATR_{period}'] = ta.atr(df['High'], df['Low'], df['Close'], length=period)
        return df
    
    def add_stochastic(self, df: pd.DataFrame, k_period: int = 14, 
                      d_period: int = 3) -> pd.DataFrame:
        """
        Add Stochastic Oscillator
        """
        stoch_result = ta.stoch(df['High'], df['Low'], df['Close'], 
                               k=k_period, d=d_period)
        
        df[f'Stoch_K_{k_period}'] = stoch_result[f'STOCHk_{k_period}_{d_period}_3']
        df[f'Stoch_D_{k_period}'] = stoch_result[f'STOCHd_{k_period}_{d_period}_3']
        
        return df
    
    def add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume-based indicators
        """
        # On-Balance Volume
        df['OBV'] = ta.obv(df['Close'], df['Volume'])
        
        # Volume Weighted Average Price (VWAP)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        
        # Volume Rate of Change
        df['VROC'] = ta.roc(df['Volume'], length=10)
        
        # Money Flow Index
        df['MFI'] = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'])
        
        return df
    
    def add_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Add Average Directional Index
        """
        adx_result = ta.adx(df['High'], df['Low'], df['Close'], length=period)
        
        df[f'ADX_{period}'] = adx_result[f'ADX_{period}']
        df[f'DI+_{period}'] = adx_result[f'DMP_{period}']
        df[f'DI-_{period}'] = adx_result[f'DMN_{period}']
        
        return df
    
    def add_cci(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Add Commodity Channel Index
        """
        df[f'CCI_{period}'] = ta.cci(df['High'], df['Low'], df['Close'], length=period)
        return df
    
    def identify_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify candlestick patterns
        """
        # Doji
        df['Doji'] = ta.cdl_doji(df['Open'], df['High'], df['Low'], df['Close'])
        
        # Hammer
        df['Hammer'] = ta.cdl_hammer(df['Open'], df['High'], df['Low'], df['Close'])
        
        # Engulfing patterns
        df['Bullish_Engulfing'] = ta.cdl_engulfing(df['Open'], df['High'], 
                                                   df['Low'], df['Close']) > 0
        df['Bearish_Engulfing'] = ta.cdl_engulfing(df['Open'], df['High'], 
                                                   df['Low'], df['Close']) < 0
        
        return df
    
    def add_support_resistance(self, df: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
        """
        Calculate dynamic support and resistance levels
        """
        # Rolling high/low as resistance/support
        df['Resistance'] = df['High'].rolling(window=lookback).max()
        df['Support'] = df['Low'].rolling(window=lookback).min()
        
        # Pivot points
        df['Pivot'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['R1'] = 2 * df['Pivot'] - df['Low']
        df['S1'] = 2 * df['Pivot'] - df['High']
        df['R2'] = df['Pivot'] + (df['High'] - df['Low'])
        df['S2'] = df['Pivot'] - (df['High'] - df['Low'])
        
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


# Example usage
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='5min')
    sample_data = pd.DataFrame({
        'Open': np.random.randn(len(dates)).cumsum() + 4000,
        'High': np.random.randn(len(dates)).cumsum() + 4010,
        'Low': np.random.randn(len(dates)).cumsum() + 3990,
        'Close': np.random.randn(len(dates)).cumsum() + 4000,
        'Volume': np.random.randint(1000000, 5000000, len(dates))
    }, index=dates)
    
    # Initialize indicators
    indicators = TechnicalIndicators()
    
    # Define parameters
    params = {
        'RSI': {'periods': [14], 'oversold': [30], 'overbought': [70]},
        'EMA': {'short_periods': [10], 'long_periods': [50]},
        'MACD': {'fast': [12], 'slow': [26], 'signal': [9]},
        'Bollinger_Bands': {'periods': [20], 'std_dev': [2]},
        'ATR': {'periods': [14]}
    }
    
    # Calculate indicators
    data_with_indicators = indicators.calculate_all_indicators(sample_data, params)
    
    print("Indicators calculated:")
    print(data_with_indicators.columns.tolist())
    print("\nFirst 5 rows:")
    print(data_with_indicators.head())