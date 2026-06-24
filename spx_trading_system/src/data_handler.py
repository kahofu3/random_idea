"""
Data Handler Module for SPX Trading System
Handles data fetching, storage, and preprocessing
"""
import os
import sys
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional, Tuple
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import TRADING_CONFIG, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['log_level']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataHandler:
    """Handles all data-related operations for the trading system"""
    
    def __init__(self, symbol: str = TRADING_CONFIG['symbol']):
        self.symbol = symbol
        self.data_cache = {}
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
    def fetch_data(self, interval: str, start_date: str, end_date: str, 
                   force_download: bool = False) -> pd.DataFrame:
        """
        Fetch historical data for the specified interval and date range
        
        Args:
            interval: Time interval ('5m' or '10m')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            force_download: Force new download even if cached data exists
            
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"{self.symbol}_{interval}_{start_date}_{end_date}"
        cache_file = os.path.join(self.data_dir, f"{cache_key}.pkl")
        
        # Check cache first
        if not force_download and os.path.exists(cache_file):
            logger.info(f"Loading cached data for {cache_key}")
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}. Downloading fresh data.")
        
        # Download data
        logger.info(f"Downloading data for {self.symbol} from {start_date} to {end_date}")
        
        try:
            # For intraday data, yfinance has limitations on historical data
            # We need to download in chunks for longer periods
            if interval in ['5m', '10m']:
                data = self._download_intraday_data(interval, start_date, end_date)
            else:
                ticker = yf.Ticker(self.symbol)
                data = ticker.history(interval=interval, start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError("No data retrieved from yfinance")
            
            # Clean and prepare data
            data = self._clean_data(data)
            
            # Cache the data
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Successfully downloaded and cached {len(data)} records")
            return data
            
        except Exception as e:
            logger.error(f"Failed to download data: {e}")
            raise
    
    def _download_intraday_data(self, interval: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Download intraday data in chunks (yfinance limitation)
        """
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # yfinance limits intraday data to last 60 days
        # For backtesting, we'll need to use daily data and simulate intraday
        all_data = []
        current_end = end
        
        while current_end > start:
            current_start = max(start, current_end - timedelta(days=59))
            
            try:
                ticker = yf.Ticker(self.symbol)
                chunk = ticker.history(
                    interval=interval,
                    start=current_start.strftime('%Y-%m-%d'),
                    end=current_end.strftime('%Y-%m-%d')
                )
                
                if not chunk.empty:
                    all_data.append(chunk)
                    logger.info(f"Downloaded chunk from {current_start} to {current_end}: {len(chunk)} records")
                
            except Exception as e:
                logger.warning(f"Failed to download chunk {current_start} to {current_end}: {e}")
            
            current_end = current_start - timedelta(days=1)
        
        if all_data:
            return pd.concat(all_data).sort_index().drop_duplicates()
        else:
            # If intraday data is not available, use daily data and resample
            logger.warning("Intraday data not available. Using daily data for simulation.")
            return self._simulate_intraday_from_daily(interval, start_date, end_date)
    
    def _simulate_intraday_from_daily(self, interval: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Simulate intraday data from daily data (for backtesting purposes)
        """
        ticker = yf.Ticker(self.symbol)
        daily_data = ticker.history(period='max', start=start_date, end=end_date)
        
        if daily_data.empty:
            raise ValueError("No daily data available")
        
        # Create synthetic intraday data
        intraday_data = []
        interval_minutes = int(interval.replace('m', ''))
        
        for date, row in daily_data.iterrows():
            # Trading hours: 9:30 AM to 4:00 PM ET
            start_time = date.replace(hour=9, minute=30)
            end_time = date.replace(hour=16, minute=0)
            
            # Generate intraday bars
            current_time = start_time
            daily_range = row['High'] - row['Low']
            
            while current_time < end_time:
                # Simulate OHLCV with some randomness
                noise = np.random.normal(0, 0.0002)  # 0.02% noise
                
                bar_data = {
                    'Open': row['Close'] * (1 + noise),
                    'High': row['Close'] * (1 + abs(noise) + 0.0001),
                    'Low': row['Close'] * (1 - abs(noise) - 0.0001),
                    'Close': row['Close'] * (1 + noise + np.random.normal(0, 0.0001)),
                    'Volume': row['Volume'] / (390 / interval_minutes)  # Distribute volume
                }
                
                intraday_data.append({
                    'Datetime': current_time,
                    **bar_data
                })
                
                current_time += timedelta(minutes=interval_minutes)
        
        df = pd.DataFrame(intraday_data)
        df.set_index('Datetime', inplace=True)
        
        return df
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare data for use
        """
        # Remove any NaN values
        data = data.dropna()
        
        # Ensure we have all required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Sort by index (datetime)
        data = data.sort_index()
        
        # Remove any duplicate indices
        data = data[~data.index.duplicated(keep='first')]
        
        # Add additional price columns that might be useful
        data['HL2'] = (data['High'] + data['Low']) / 2
        data['HLC3'] = (data['High'] + data['Low'] + data['Close']) / 3
        data['OHLC4'] = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
        
        return data
    
    def get_latest_data(self, interval: str, lookback_periods: int = 100) -> pd.DataFrame:
        """
        Get the most recent data for live trading
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # Get last 7 days
        
        data = self.fetch_data(
            interval=interval,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            force_download=True
        )
        
        return data.tail(lookback_periods)
    
    def save_data_to_csv(self, data: pd.DataFrame, filename: str):
        """
        Save data to CSV file
        """
        filepath = os.path.join(self.data_dir, filename)
        data.to_csv(filepath)
        logger.info(f"Data saved to {filepath}")
    
    def load_data_from_csv(self, filename: str) -> pd.DataFrame:
        """
        Load data from CSV file
        """
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath, index_col=0, parse_dates=True)
        else:
            raise FileNotFoundError(f"File not found: {filepath}")


# Example usage
if __name__ == "__main__":
    handler = DataHandler()
    
    # Test data fetching
    data = handler.fetch_data(
        interval='5m',
        start_date='2024-01-01',
        end_date='2024-01-31'
    )
    
    print(f"Data shape: {data.shape}")
    print(f"Data range: {data.index[0]} to {data.index[-1]}")
    print("\nFirst 5 rows:")
    print(data.head())
    print("\nData info:")
    print(data.info())