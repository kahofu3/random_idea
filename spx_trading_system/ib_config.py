"""
Interactive Brokers Configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# IB Connection Settings
IB_CONFIG = {
    'host': os.getenv('IB_HOST', '127.0.0.1'),  # TWS or IB Gateway host
    'port': int(os.getenv('IB_PORT', '7497')),  # 7497 for paper, 7496 for live
    'client_id': int(os.getenv('IB_CLIENT_ID', '1')),
    'account': os.getenv('IB_ACCOUNT', ''),  # Your IB account number
    'trading_mode': os.getenv('IB_TRADING_MODE', 'paper'),  # 'paper' or 'live'
}

# Trading Contract Settings
CONTRACT_CONFIG = {
    'symbol': 'SPX',
    'sec_type': 'IND',  # Index
    'exchange': 'CBOE',
    'currency': 'USD',
    
    # For trading, we'll use SPY ETF or ES futures
    'tradeable_symbol': os.getenv('TRADEABLE_SYMBOL', 'SPY'),  # SPY or ES
    'tradeable_sec_type': os.getenv('TRADEABLE_SEC_TYPE', 'STK'),  # STK for SPY, FUT for ES
    'tradeable_exchange': os.getenv('TRADEABLE_EXCHANGE', 'SMART'),
    'tradeable_currency': 'USD',
}

# Position Sizing
POSITION_CONFIG = {
    'max_position_size': int(os.getenv('MAX_POSITION_SIZE', '100')),  # Max shares/contracts
    'position_sizing_method': os.getenv('POSITION_SIZING_METHOD', 'fixed'),  # 'fixed' or 'risk_based'
    'risk_per_trade': float(os.getenv('RISK_PER_TRADE', '0.02')),  # 2% risk per trade
    'max_daily_trades': int(os.getenv('MAX_DAILY_TRADES', '5')),
}

# Risk Management
RISK_CONFIG = {
    'max_daily_loss': float(os.getenv('MAX_DAILY_LOSS', '0.05')),  # 5% max daily loss
    'max_positions': int(os.getenv('MAX_POSITIONS', '1')),  # Max simultaneous positions
    'force_close_time': os.getenv('FORCE_CLOSE_TIME', '15:55'),  # Close all positions
}

# Notification Settings
NOTIFICATION_CONFIG = {
    'telegram_enabled': os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true',
    'telegram_token': os.getenv('TELEGRAM_TOKEN', ''),
    'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
    'email_enabled': os.getenv('EMAIL_ENABLED', 'false').lower() == 'true',
    'email_from': os.getenv('EMAIL_FROM', ''),
    'email_to': os.getenv('EMAIL_TO', ''),
    'email_password': os.getenv('EMAIL_PASSWORD', ''),
}

# Data Settings
DATA_CONFIG = {
    'bar_size': '5 mins',  # IB bar size format
    'lookback_periods': 100,  # Number of bars to maintain
    'update_frequency': 5,  # Seconds between strategy updates
}

# Logging Settings
LOGGING_CONFIG = {
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'log_file': 'logs/ib_trading.log',
    'trade_log_file': 'logs/trades.csv',
    'enable_console_log': True,
}

# Strategy Override Settings (for live adjustments)
STRATEGY_OVERRIDE = {
    'enabled': os.getenv('STRATEGY_OVERRIDE_ENABLED', 'false').lower() == 'true',
    'min_confirmations': int(os.getenv('MIN_CONFIRMATIONS', '1')),
    'stop_loss_multiplier': float(os.getenv('STOP_LOSS_MULTIPLIER', '1.0')),
    'take_profit_multiplier': float(os.getenv('TAKE_PROFIT_MULTIPLIER', '1.0')),
}