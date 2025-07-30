"""
SPX Trading System - Source Package
"""

from .data_handler import DataHandler
from .indicators_simple import TechnicalIndicators
from .strategy import TradingStrategy
from .backtest import Backtester
# from .visualization import ReportGenerator
# from .optimizer import StrategyOptimizer

__version__ = "1.0.0"
__all__ = [
    'DataHandler',
    'TechnicalIndicators',
    'TradingStrategy',
    'Backtester',
    # 'ReportGenerator',
    # 'StrategyOptimizer'
]