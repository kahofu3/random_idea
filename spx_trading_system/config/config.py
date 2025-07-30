"""
Configuration settings for SPX Trading System
"""
from datetime import datetime

# Trading Configuration
TRADING_CONFIG = {
    'symbol': '^GSPC',  # S&P 500 Index symbol for yfinance
    'timeframes': {
        '5min': '5m',
        '10min': '10m'
    },
    'start_date': '2023-07-30',
    'end_date': '2025-07-30',
    'initial_capital': 100000,
    'commission': 0.001,  # 0.1% commission
    'slippage': 0.0005,  # 0.05% slippage
}

# Risk Management Parameters
RISK_CONFIG = {
    'risk_per_trade': 0.02,  # 2% risk per trade
    'max_drawdown': 0.20,  # 20% maximum drawdown
    'position_sizing_method': 'fixed_risk',  # Options: 'fixed_risk', 'volatility_based'
}

# Technical Indicator Parameters
INDICATOR_PARAMS = {
    'RSI': {
        'periods': [9, 14, 21],
        'oversold': [20, 30],
        'overbought': [70, 80]
    },
    'EMA': {
        'short_periods': [10, 20],
        'long_periods': [50, 100]
    },
    'MACD': {
        'fast': [8, 12],
        'slow': [21, 26],
        'signal': [5, 9]
    },
    'Bollinger_Bands': {
        'periods': [20],
        'std_dev': [2, 2.5]
    },
    'ATR': {
        'periods': [14],
        'stop_loss_multiplier': [1, 2, 3]
    }
}

# Trading Rules
TRADING_RULES = {
    'entry_rules': {
        'long': {
            'RSI_oversold': True,
            'MACD_crossover': True,
            'EMA_crossover': True,
            'BB_lower_band': True
        },
        'short': {
            'RSI_overbought': True,
            'MACD_crossunder': True,
            'EMA_crossunder': True,
            'BB_upper_band': True
        }
    },
    'exit_rules': {
        'stop_loss_pct': 0.02,  # 2% stop loss
        'take_profit_ratio': 2,  # 1:2 risk-reward ratio
        'trailing_stop': True,
        'time_based_exit': True,
        'end_of_day_exit': True
    }
}

# Time Filters
TIME_FILTERS = {
    'avoid_first_minutes': 30,  # Avoid first 30 minutes
    'avoid_last_minutes': 30,   # Avoid last 30 minutes
    'trading_hours': {
        'start': '09:30',
        'end': '16:00'
    }
}

# Backtesting Parameters
BACKTEST_CONFIG = {
    'train_test_split': 0.8,  # 80% train, 20% test
    'walk_forward_windows': 12,  # Number of walk-forward windows
    'optimization_metric': 'sharpe_ratio',  # Metric to optimize
    'min_trades': 100,  # Minimum trades for valid backtest
}

# Performance Targets
PERFORMANCE_TARGETS = {
    'min_win_rate': 0.50,  # 50% win rate
    'min_profit_factor': 1.5,
    'min_sharpe_ratio': 1.0,
    'min_annual_return': 0.10,  # 10% annual return
    'max_drawdown': 0.20  # 20% maximum drawdown
}

# Logging Configuration
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_file': 'logs/trading_system.log',
    'enable_console_log': True
}