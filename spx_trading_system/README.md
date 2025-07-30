# SPX Trading System

A comprehensive algorithmic trading system for the S&P 500 Index (SPX) using technical indicators, backtesting, and parameter optimization.

## Features

- **Multiple Technical Indicators**: RSI, MACD, EMA, Bollinger Bands, ATR, and more
- **Advanced Backtesting**: Realistic simulation with transaction costs and slippage
- **Parameter Optimization**: Find the best indicator combinations automatically
- **Risk Management**: Position sizing, stop-loss, and take-profit mechanisms
- **Comprehensive Reporting**: Detailed performance metrics and visualizations
- **Walk-Forward Analysis**: Validate strategy robustness over time

## Installation

1. Clone or download this repository:
```bash
cd spx_trading_system
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Note: TA-Lib requires additional system-level installation:
- **Linux**: `sudo apt-get install ta-lib`
- **macOS**: `brew install ta-lib`
- **Windows**: Download from [TA-Lib website](https://www.ta-lib.org/hdr_dw.html)

## Quick Start

### Basic Backtest
Run a simple backtest with default parameters:
```bash
python main.py --mode backtest --timeframe 5m --report
```

### Parameter Optimization
Find the best performing indicators:
```bash
python main.py --mode optimize --timeframe 5m
```

### Full Analysis
Run complete analysis pipeline (optimization + backtest + reporting):
```bash
python main.py --mode full --timeframe 5m --start-date 2023-07-30 --end-date 2025-07-30
```

## Usage

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --mode              Operation mode: backtest, optimize, walk-forward, full (default: backtest)
  --timeframe         Trading timeframe: 5m, 10m (default: 5m)
  --start-date        Start date in YYYY-MM-DD format (default: 2023-07-30)
  --end-date          End date in YYYY-MM-DD format (default: 2025-07-30)
  --report            Generate full HTML/PDF report with charts
```

### Examples

1. **Run backtest for 10-minute timeframe**:
```bash
python main.py --mode backtest --timeframe 10m --report
```

2. **Optimize parameters for specific date range**:
```bash
python main.py --mode optimize --start-date 2024-01-01 --end-date 2024-12-31
```

3. **Walk-forward analysis**:
```bash
python main.py --mode walk-forward --timeframe 5m
```

## Configuration

Edit `config/config.py` to customize:

- **Trading parameters**: Initial capital, commission, slippage
- **Risk management**: Risk per trade, maximum drawdown
- **Indicator parameters**: Periods, thresholds, multipliers
- **Performance targets**: Win rate, Sharpe ratio, return targets

### Key Configuration Options

```python
TRADING_CONFIG = {
    'symbol': '^GSPC',           # S&P 500 Index symbol
    'initial_capital': 100000,    # Starting capital
    'commission': 0.001,          # 0.1% commission
    'slippage': 0.0005           # 0.05% slippage
}

RISK_CONFIG = {
    'risk_per_trade': 0.02,      # 2% risk per trade
    'max_drawdown': 0.20         # 20% maximum drawdown
}
```

## Project Structure

```
spx_trading_system/
├── config/
│   ├── __init__.py
│   └── config.py            # Configuration settings
├── src/
│   ├── __init__.py
│   ├── data_handler.py      # Data fetching and management
│   ├── indicators.py        # Technical indicators
│   ├── strategy.py          # Trading strategy logic
│   ├── backtest.py          # Backtesting engine
│   ├── visualization.py     # Charts and reporting
│   └── optimizer.py         # Parameter optimization
├── data/                    # Historical data cache
├── logs/                    # System logs
├── reports/                 # Generated reports
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Performance Metrics

The system calculates comprehensive performance metrics:

- **Returns**: Total return, annual return, expected value per trade
- **Risk Metrics**: Sharpe ratio, maximum drawdown, Calmar ratio
- **Trade Statistics**: Win rate, profit factor, average trade duration
- **Risk-Adjusted Returns**: Recovery factor, risk per trade

### Success Criteria

The system evaluates strategies against these targets:
- Win Rate > 50%
- Profit Factor > 1.5
- Sharpe Ratio > 1.0
- Annual Return > 10%
- Maximum Drawdown < 20%

## Technical Indicators

### Available Indicators

1. **RSI (Relative Strength Index)**: Momentum oscillator
2. **MACD (Moving Average Convergence Divergence)**: Trend following
3. **EMA (Exponential Moving Average)**: Trend identification
4. **Bollinger Bands**: Volatility and mean reversion
5. **ATR (Average True Range)**: Volatility measurement
6. **Stochastic Oscillator**: Momentum indicator
7. **Volume Indicators**: OBV, VWAP, MFI

### Signal Generation

The system combines multiple indicators to generate high-probability signals:
- Requires at least 2 indicators to confirm
- Filters signals by trading hours
- Applies risk management rules

## Reports

Generated reports include:

1. **Performance Summary**: Key metrics and statistics
2. **Equity Curve**: Portfolio value over time
3. **Drawdown Analysis**: Risk visualization
4. **Trade Analysis**: Win/loss distribution, duration analysis
5. **Interactive Charts**: Zoomable price charts with signals

Reports are saved in the `reports/` directory with timestamps.

## Data

The system uses Yahoo Finance for historical data:
- Automatically caches data to reduce API calls
- Handles intraday data limitations
- Simulates intraday data when not available

## Important Notes

1. **Backtesting Limitations**: Past performance doesn't guarantee future results
2. **Data Quality**: Yahoo Finance data may have limitations for intraday timeframes
3. **Transaction Costs**: Ensure realistic commission and slippage settings
4. **Risk Management**: Always use appropriate position sizing and stop-losses

## Troubleshooting

### Common Issues

1. **TA-Lib Installation Error**:
   - Ensure TA-Lib is installed at system level before pip install
   - Use Anaconda: `conda install -c conda-forge ta-lib`

2. **Insufficient Data**:
   - Yahoo Finance limits intraday data to recent periods
   - System will use daily data simulation for older dates

3. **Memory Issues**:
   - Reduce optimization parameter ranges
   - Use larger timeframes (10m instead of 5m)

## Future Enhancements

- [ ] Real-time trading integration
- [ ] Machine learning models
- [ ] More asset classes
- [ ] Advanced order types
- [ ] Portfolio optimization
- [ ] Risk parity allocation

## License

This project is for educational and research purposes only. Use at your own risk.

## Disclaimer

**IMPORTANT**: This software is for educational purposes only. Trading financial instruments carries a high level of risk and may not be suitable for all investors. Past performance is not indicative of future results. Always do your own research and consider consulting with a financial advisor.