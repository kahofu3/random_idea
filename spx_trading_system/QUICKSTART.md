# SPX Trading System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

**Note**: TA-Lib requires system installation first:
- Ubuntu/Debian: `sudo apt-get install ta-lib`
- macOS: `brew install ta-lib`
- Windows: Download from [ta-lib.org](https://ta-lib.org)

### Step 2: Test Installation

```bash
python test_system.py
```

You should see all modules load successfully.

### Step 3: Run Your First Backtest

```bash
# Simple backtest with default parameters
python main.py --mode backtest --timeframe 5m --report
```

This will:
- Download S&P 500 historical data
- Calculate technical indicators
- Run trading simulation
- Generate a report in the `reports/` folder

## 📊 Common Commands

### 1. Basic Backtest (Quick Test)
```bash
python main.py --mode backtest --timeframe 5m
```

### 2. Find Best Parameters
```bash
python main.py --mode optimize --timeframe 5m
```

### 3. Full Analysis (Recommended)
```bash
python main.py --mode full --timeframe 5m --report
```

### 4. Custom Date Range
```bash
python main.py --mode backtest --start-date 2024-01-01 --end-date 2024-12-31 --report
```

## 📈 Understanding Results

After running a backtest, you'll see:

```
============================================================
BACKTEST SUMMARY
============================================================

Trade Statistics:
  Total Trades: 156
  Winning Trades: 89
  Losing Trades: 67
  Win Rate: 57.05%

Returns:
  Total P&L: $12,450.00
  Total Return: 12.45%
  Annual Return: 14.82%
  Expected Value per Trade: $79.81 (0.08%)

Risk Metrics:
  Sharpe Ratio: 1.45
  Profit Factor: 1.82
  Max Drawdown: 8.45%
  Calmar Ratio: 1.75

Performance Targets:
  Win Rate Target Met: ✓
  Profit Factor Target Met: ✓
  Sharpe Ratio Target Met: ✓
  Annual Return Target Met: ✓
  Max Drawdown Target Met: ✓
============================================================
```

## 📁 Output Files

Check the `reports/` folder for:
- `report.txt` - Detailed text report
- `equity_curve.png` - Portfolio value over time
- `drawdown.png` - Risk visualization
- `trade_analysis.png` - Trade statistics
- `interactive_chart.html` - Interactive price chart with signals

## ⚙️ Customize Settings

Edit `config/config.py` to adjust:
- Initial capital (default: $100,000)
- Risk per trade (default: 2%)
- Commission & slippage
- Indicator parameters

## 🎯 Best Practices

1. **Start Simple**: Run basic backtest first
2. **Optimize Carefully**: Use optimization to find good parameters
3. **Validate Results**: Check if results meet performance targets
4. **Risk Management**: Never risk more than 2% per trade

## ❓ Troubleshooting

### "No data available"
- Yahoo Finance has limited intraday history
- Try using recent dates or daily timeframe

### "Import error"
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check TA-Lib system installation

### "Too few trades"
- Adjust indicator parameters in `config/config.py`
- Try different timeframes (5m vs 10m)

## 🚦 Next Steps

1. Run optimization to find best indicators:
   ```bash
   python main.py --mode optimize
   ```

2. Test different timeframes:
   ```bash
   python main.py --mode backtest --timeframe 10m --report
   ```

3. Run walk-forward analysis:
   ```bash
   python main.py --mode walk-forward
   ```

## 📚 Learn More

- Read the full [README.md](README.md) for detailed documentation
- Check `config/config.py` for all configurable parameters
- Review generated reports to understand strategy performance

---

**Remember**: This is for educational purposes. Always paper trade before using real money!