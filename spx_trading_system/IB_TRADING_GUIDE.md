# Interactive Brokers SPX Trading System Guide

## 🚀 Complete Setup Guide for Live Trading

### Table of Contents
1. [Prerequisites](#prerequisites)
2. [IB Account Setup](#ib-account-setup)
3. [System Installation](#system-installation)
4. [Configuration](#configuration)
5. [Running the Bot](#running-the-bot)
6. [Monitoring & Safety](#monitoring--safety)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.8 or higher
- Interactive Brokers account (paper or live)
- IB Gateway or Trader Workstation (TWS)
- Stable internet connection

### System Requirements
- RAM: 4GB minimum
- Storage: 1GB free space
- OS: Windows, macOS, or Linux

---

## IB Account Setup

### 1. Create IB Account
- Go to [Interactive Brokers](https://www.interactivebrokers.com)
- Open a paper trading account first (free)
- Get your account credentials

### 2. Download IB Gateway
- Download from: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
- Install IB Gateway (lighter than TWS)
- Or use TWS if you prefer the full interface

### 3. Configure API Access
1. Open IB Gateway/TWS
2. Go to: **Configure → Settings → API → Settings**
3. Enable these settings:
   - ✅ Enable ActiveX and Socket Clients
   - ✅ Download open orders on connection
   - ✅ Include market data in historical data requests
4. Configure Trusted IPs:
   - Add: `127.0.0.1`
5. Set Socket Port:
   - Paper Trading: `7497`
   - Live Trading: `7496`
6. Apply and restart IB Gateway

### 4. Paper Trading Setup
**ALWAYS TEST WITH PAPER TRADING FIRST!**
- Login to IB Gateway with your paper trading credentials
- Paper account usually starts with "DU" (e.g., DU1234567)

---

## System Installation

### 1. Clone/Download the Trading System
```bash
# If you have the files in spx_trading_system directory
cd spx_trading_system
```

### 2. Run Setup Script
```bash
# Make setup script executable
chmod +x setup_ib_trading.py

# Run setup
python3 setup_ib_trading.py
```

This will:
- Check Python version
- Create necessary directories
- Install dependencies
- Create .env file
- Test IB connection

### 3. Manual Installation (if setup fails)
```bash
# Install IB trading requirements
pip install ib_insync nest_asyncio python-dotenv

# Create directories
mkdir -p logs data reports

# Copy environment template
cp .env.example .env
```

---

## Configuration

### 1. Edit .env File
Open `.env` file and configure:

```env
# IB Connection (MUST CONFIGURE)
IB_HOST=127.0.0.1
IB_PORT=7497  # 7497 for paper, 7496 for live
IB_CLIENT_ID=1
IB_ACCOUNT=DU1234567  # Your paper account number
IB_TRADING_MODE=paper  # Start with 'paper'!

# Trading Settings
TRADEABLE_SYMBOL=SPY  # Trade SPY ETF (liquid, tracks S&P 500)
TRADEABLE_SEC_TYPE=STK
MAX_POSITION_SIZE=100  # Start small!
RISK_PER_TRADE=0.01  # 1% risk to start

# Safety Settings
MAX_DAILY_LOSS=0.02  # Stop at 2% loss
MAX_DAILY_TRADES=3  # Limit trades per day
FORCE_CLOSE_TIME=15:55  # Close before market close
```

### 2. Configure Notifications (Optional)
```env
# Telegram Alerts
TELEGRAM_ENABLED=true
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Email Alerts
EMAIL_ENABLED=true
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=alerts@gmail.com
EMAIL_PASSWORD=app_specific_password
```

---

## Running the Bot

### 1. Pre-flight Checklist
- [ ] IB Gateway is running and logged in
- [ ] .env file is configured
- [ ] Using PAPER account first
- [ ] Market is open (9:30 AM - 4:00 PM EST)

### 2. Start the Bot

**Option 1: Using run script**
```bash
# Unix/Mac
./run_trader.sh

# Windows
run_trader.bat
```

**Option 2: Direct Python**
```bash
python3 ib_live_trader.py
```

### 3. What to Expect
```
2024-XX-XX 09:30:00 - INFO - Connected to IB on 127.0.0.1:7497
2024-XX-XX 09:30:01 - INFO - Account Net Liquidation: $100,000
2024-XX-XX 09:30:02 - INFO - Loaded 234 historical bars
2024-XX-XX 09:30:03 - INFO - Starting live trading bot...
2024-XX-XX 09:35:15 - INFO - BUY Signal Generated (3 confirmations)
2024-XX-XX 09:35:16 - INFO - Placed BUY order for 100 shares
```

---

## Monitoring & Safety

### 1. Real-time Monitoring
- **Log File**: `logs/ib_trading.log`
- **Trade History**: `logs/trades.csv`
- Watch for:
  - Connection status
  - Signal generation
  - Order execution
  - P&L updates

### 2. Safety Features
The bot includes multiple safety mechanisms:
- **Daily Loss Limit**: Stops trading if daily loss exceeds limit
- **Max Position Size**: Prevents over-leveraging
- **Force Close Time**: Closes all positions before market close
- **Trade Frequency Limit**: Prevents overtrading

### 3. Emergency Stop
To stop the bot immediately:
- Press `Ctrl+C` (Unix/Mac)
- Press `Ctrl+Break` (Windows)
- Or close the terminal

The bot will:
1. Cancel all pending orders
2. Close all open positions
3. Disconnect safely

### 4. Monitor Performance
Check daily performance:
```bash
# View today's trades
tail -f logs/trades.csv

# View real-time logs
tail -f logs/ib_trading.log

# Check for errors
grep ERROR logs/ib_trading.log
```

---

## Trading Strategy Details

### Triple_Optimized Strategy
The bot uses the winning strategy from backtesting:
- **RSI(9)**: Oversold < 25, Overbought > 75
- **MACD(8,21,5)**: Fast/slow crossovers
- **EMA(5,20)**: Short/long crossovers

### Entry Conditions
- Requires 1+ indicator confirmations
- No existing position
- Within trading hours
- Daily loss limit not exceeded

### Exit Conditions
- Stop Loss: 1x ATR (≈1%)
- Take Profit: 4x ATR (≈4%)
- End of Day: Force close at 3:55 PM

---

## Troubleshooting

### Common Issues

#### 1. Cannot Connect to IB
```
Error: Cannot connect to IB Gateway
```
**Solution**:
- Ensure IB Gateway is running
- Check port number (7497 for paper)
- Verify API is enabled
- Check firewall settings

#### 2. No Market Data
```
Error: No market data received
```
**Solution**:
- Ensure market data subscriptions are active
- Check if market is open
- Verify symbol is correct (SPY)

#### 3. Orders Rejected
```
Error: Order rejected - insufficient buying power
```
**Solution**:
- Check account balance
- Reduce position size
- Verify margin requirements

#### 4. Strategy Not Generating Signals
**Check**:
- Market volatility (needs movement)
- Indicator values in logs
- Timeframe (5-min bars)

### Debug Mode
For detailed debugging:
```bash
# Edit .env
LOG_LEVEL=DEBUG

# Run with debug output
python3 ib_live_trader.py > debug.log 2>&1
```

---

## Best Practices

### 1. Start Small
- Begin with paper trading
- Use small position sizes
- Increase gradually with success

### 2. Daily Routine
- Check IB Gateway connection
- Review previous day's trades
- Ensure adequate capital
- Monitor throughout the day

### 3. Risk Management
- Never increase risk parameters during drawdown
- Keep detailed records
- Review performance weekly
- Adjust strategy based on results

### 4. Going Live
When ready for live trading:
1. Run paper trading for at least 1 month
2. Achieve consistent profitability
3. Start with 1/10th normal position size
4. Gradually increase over 3-6 months

---

## Important Disclaimers

⚠️ **RISK WARNING**: Trading involves substantial risk of loss. Past performance does not guarantee future results.

⚠️ **PAPER TRADE FIRST**: Always test thoroughly with paper trading before risking real money.

⚠️ **NO WARRANTY**: This software is provided "as is" without warranty. You are responsible for all trading decisions.

⚠️ **MONITOR ACTIVELY**: Automated trading requires active monitoring. Do not leave unattended.

---

## Support & Resources

### Logs Location
- Trading Log: `logs/ib_trading.log`
- Trade History: `logs/trades.csv`
- Error Log: Check for ERROR in main log

### IB Resources
- [IB API Documentation](https://interactivebrokers.github.io/tws-api/)
- [IB Gateway User Guide](https://www.interactivebrokers.com/en/trading/tws-guide.php)
- [ib_insync Documentation](https://ib-insync.readthedocs.io/)

### Strategy Customization
To modify the strategy, edit:
- `ib_live_trader.py`: Line 79-87 (strategy parameters)
- `.env`: Strategy override settings

---

## Quick Start Checklist

1. [ ] Install IB Gateway
2. [ ] Configure API access
3. [ ] Run `python3 setup_ib_trading.py`
4. [ ] Edit `.env` with your credentials
5. [ ] Start IB Gateway (paper account)
6. [ ] Run `./run_trader.sh`
7. [ ] Monitor `logs/ib_trading.log`
8. [ ] Let it run for a full day
9. [ ] Review results in `logs/trades.csv`
10. [ ] Adjust and repeat

Good luck with your trading! Remember: **ALWAYS START WITH PAPER TRADING!** 🚀