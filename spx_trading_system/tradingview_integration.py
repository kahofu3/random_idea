"""
TradingView Integration for SPX Trading System
Combines TradingView alerts with automated execution
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import pandas as pd
from typing import Dict, Optional

# Import our trading components
from src.indicators_simple import TechnicalIndicators
from src.strategy import TradingStrategy
from ib_live_trader import IBLiveTrader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app for webhook receiver
app = Flask(__name__)

# Global trader instance
trader = None


class TradingViewConnector:
    """
    Connects TradingView alerts to IB trading bot
    """
    
    def __init__(self):
        self.alerts_received = []
        self.active_alerts = {}
        
    def validate_alert(self, alert_data: Dict) -> bool:
        """
        Validate incoming TradingView alert
        """
        required_fields = ['action', 'ticker', 'price']
        
        for field in required_fields:
            if field not in alert_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate action
        if alert_data['action'] not in ['buy', 'sell', 'close']:
            logger.error(f"Invalid action: {alert_data['action']}")
            return False
        
        # Validate ticker (should be SPX or SPY)
        if alert_data['ticker'] not in ['SPX', 'SPY', 'ES']:
            logger.warning(f"Unexpected ticker: {alert_data['ticker']}")
        
        return True
    
    def process_alert(self, alert_data: Dict) -> Dict:
        """
        Process TradingView alert and generate trading signal
        """
        # Log alert
        self.alerts_received.append({
            'timestamp': datetime.now(),
            'data': alert_data
        })
        
        # Create signal for IB trader
        signal = {
            'action': 0,  # 0: hold, 1: buy, -1: sell
            'strength': 3,  # High confidence from TV alert
            'stop_loss': 0,
            'take_profit': 0,
            'source': 'TradingView'
        }
        
        # Convert TV action to our signal format
        if alert_data['action'] == 'buy':
            signal['action'] = 1
            signal['stop_loss'] = alert_data.get('stop_loss', 
                                                 alert_data['price'] * 0.99)
            signal['take_profit'] = alert_data.get('take_profit', 
                                                   alert_data['price'] * 1.04)
        
        elif alert_data['action'] == 'sell':
            signal['action'] = -1
            signal['stop_loss'] = alert_data.get('stop_loss', 
                                                 alert_data['price'] * 1.01)
            signal['take_profit'] = alert_data.get('take_profit', 
                                                   alert_data['price'] * 0.96)
        
        elif alert_data['action'] == 'close':
            signal['action'] = 0  # Close position
            signal['close_all'] = True
        
        return signal


# TradingView Webhook Endpoint
@app.route('/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    """
    Receive alerts from TradingView
    
    Expected JSON format:
    {
        "action": "buy/sell/close",
        "ticker": "SPX",
        "price": 5900.50,
        "stop_loss": 5850.00,  # optional
        "take_profit": 6000.00,  # optional
        "message": "RSI oversold crossover"  # optional
    }
    """
    try:
        # Get JSON data
        alert_data = request.get_json()
        logger.info(f"Received TradingView alert: {alert_data}")
        
        # Initialize connector
        connector = TradingViewConnector()
        
        # Validate alert
        if not connector.validate_alert(alert_data):
            return jsonify({'error': 'Invalid alert format'}), 400
        
        # Process alert
        signal = connector.process_alert(alert_data)
        
        # Execute trade if trader is connected
        if trader and trader.connected:
            # Convert to DataFrame format expected by trader
            mock_data = pd.DataFrame({
                'Close': [alert_data['price']],
                'timestamp': [datetime.now()]
            })
            
            # Execute signal
            trader._execute_signals(signal, mock_data)
            
            return jsonify({
                'status': 'success',
                'signal': signal,
                'message': 'Trade signal sent to IB'
            }), 200
        else:
            logger.warning("IB trader not connected, signal saved for later")
            return jsonify({
                'status': 'queued',
                'signal': signal,
                'message': 'Signal saved, IB not connected'
            }), 202
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """Check system status"""
    return jsonify({
        'status': 'running',
        'ib_connected': trader.connected if trader else False,
        'timestamp': datetime.now().isoformat()
    })


def create_tradingview_alerts():
    """
    Generate TradingView Pine Script alerts for Triple_Optimized strategy
    """
    pine_script = """
//@version=5
indicator("SPX Triple_Optimized Strategy Alerts", overlay=true)

// Triple_Optimized Parameters
rsi_period = 9
rsi_oversold = 25
rsi_overbought = 75
macd_fast = 8
macd_slow = 21
macd_signal = 5
ema_short = 5
ema_long = 20

// Calculate indicators
rsi = ta.rsi(close, rsi_period)
[macd_line, signal_line, hist] = ta.macd(close, macd_fast, macd_slow, macd_signal)
ema_short_val = ta.ema(close, ema_short)
ema_long_val = ta.ema(close, ema_long)

// Signal conditions
rsi_buy = rsi < rsi_oversold
rsi_sell = rsi > rsi_overbought

macd_buy = ta.crossover(macd_line, signal_line)
macd_sell = ta.crossunder(macd_line, signal_line)

ema_buy = ta.crossover(ema_short_val, ema_long_val)
ema_sell = ta.crossunder(ema_short_val, ema_long_val)

// Combined signals (need at least 1 confirmation)
buy_signal = (rsi_buy ? 1 : 0) + (macd_buy ? 1 : 0) + (ema_buy ? 1 : 0) >= 1
sell_signal = (rsi_sell ? 1 : 0) + (macd_sell ? 1 : 0) + (ema_sell ? 1 : 0) >= 1

// Calculate stops
atr = ta.atr(14)
stop_loss_buy = close - atr
take_profit_buy = close + (atr * 4)
stop_loss_sell = close + atr
take_profit_sell = close - (atr * 4)

// Plot signals
plotshape(buy_signal, title="Buy", location=location.belowbar, 
          color=color.green, style=shape.triangleup, size=size.small)
plotshape(sell_signal, title="Sell", location=location.abovebar, 
          color=color.red, style=shape.triangledown, size=size.small)

// Alerts
if buy_signal
    alert_message = '{"action":"buy","ticker":"SPX","price":' + str.tostring(close) + 
                   ',"stop_loss":' + str.tostring(stop_loss_buy) + 
                   ',"take_profit":' + str.tostring(take_profit_buy) + '}'
    alert(alert_message, alert.freq_once_per_bar_close)

if sell_signal
    alert_message = '{"action":"sell","ticker":"SPX","price":' + str.tostring(close) + 
                   ',"stop_loss":' + str.tostring(stop_loss_sell) + 
                   ',"take_profit":' + str.tostring(take_profit_sell) + '}'
    alert(alert_message, alert.freq_once_per_bar_close)

// Visual indicators
plot(ema_short_val, "EMA 5", color=color.blue, linewidth=1)
plot(ema_long_val, "EMA 20", color=color.orange, linewidth=1)

// Info panel
var table infoTable = table.new(position.top_right, 2, 5)
if barstate.islast
    table.cell(infoTable, 0, 0, "RSI", text_color=color.white, bgcolor=color.gray)
    table.cell(infoTable, 1, 0, str.tostring(rsi, "#.##"), 
               text_color=rsi < 25 ? color.green : rsi > 75 ? color.red : color.white)
    
    table.cell(infoTable, 0, 1, "MACD", text_color=color.white, bgcolor=color.gray)
    table.cell(infoTable, 1, 1, macd_line > signal_line ? "Bullish" : "Bearish",
               text_color=macd_line > signal_line ? color.green : color.red)
    
    table.cell(infoTable, 0, 2, "EMA", text_color=color.white, bgcolor=color.gray)
    table.cell(infoTable, 1, 2, ema_short_val > ema_long_val ? "Bullish" : "Bearish",
               text_color=ema_short_val > ema_long_val ? color.green : color.red)
"""
    
    return pine_script


def save_pine_script():
    """Save Pine Script to file"""
    script = create_tradingview_alerts()
    
    with open('tradingview_alerts.pine', 'w') as f:
        f.write(script)
    
    logger.info("Pine Script saved to tradingview_alerts.pine")
    
    # Also save webhook setup instructions
    instructions = """
# TradingView Alert Setup Instructions

## 1. Add the Pine Script to TradingView
- Open TradingView chart
- Click Pine Editor
- Paste the script from `tradingview_alerts.pine`
- Click "Add to Chart"

## 2. Create Alerts
- Right-click on chart → "Add Alert"
- Condition: Select "SPX Triple_Optimized Strategy Alerts"
- Alert name: "SPX Trading Signal"
- Message: Leave as is (script generates JSON)

## 3. Configure Webhook
- In Alert settings, check "Webhook URL"
- Enter: http://YOUR_SERVER:5000/webhook/tradingview
- Replace YOUR_SERVER with your IP or domain

## 4. Start Webhook Server
```bash
python tradingview_integration.py
```

## 5. Test the Connection
- Visit: http://YOUR_SERVER:5000/status
- Should show: {"status": "running", "ib_connected": true/false}

## Security Notes
- Use HTTPS in production (not HTTP)
- Add authentication tokens
- Restrict IP access
- Use a reverse proxy (nginx)

## Alert JSON Format
Alerts will send:
```json
{
    "action": "buy",
    "ticker": "SPX",
    "price": 5900.50,
    "stop_loss": 5850.00,
    "take_profit": 6000.00
}
```
"""
    
    with open('TRADINGVIEW_SETUP.md', 'w') as f:
        f.write(instructions)
    
    logger.info("Setup instructions saved to TRADINGVIEW_SETUP.md")


def main():
    """Run webhook server"""
    global trader
    
    # Initialize IB trader
    trader = IBLiveTrader()
    
    # Save Pine Script and instructions
    save_pine_script()
    
    # Start webhook server
    logger.info("Starting TradingView webhook server on port 5000...")
    logger.info("Webhook URL: http://localhost:5000/webhook/tradingview")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
    main()