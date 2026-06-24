"""
Alpaca Webhook Server for TradingView VWAP Strategy
100% FREE automated trading!
"""
from flask import Flask, request, jsonify
import alpaca_trade_api as tradeapi
import json
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Alpaca API credentials (set these as environment variables)
API_KEY = os.getenv('ALPACA_API_KEY', 'your_api_key_here')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', 'your_secret_key_here')
BASE_URL = 'https://paper-api.alpaca.markets'  # Use paper trading first!

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

# Configuration
SYMBOL = 'SPY'  # Trade SPY ETF instead of SPX
POSITION_SIZE = 100  # Number of shares
MAX_POSITIONS = 1  # Only one position at a time

@app.route('/webhook/tradingview', methods=['POST'])
def handle_webhook():
    """Handle incoming webhook from TradingView"""
    try:
        # Parse the alert message
        data = request.get_json()
        logger.info(f"Received webhook: {data}")
        
        # Expected format: {"action": "buy"} or {"action": "sell"}
        action = data.get('action', '').lower()
        
        if action not in ['buy', 'sell', 'close']:
            return jsonify({'error': 'Invalid action'}), 400
        
        # Get current position
        try:
            position = api.get_position(SYMBOL)
            has_position = True
            current_qty = int(position.qty)
        except:
            has_position = False
            current_qty = 0
        
        # Execute trade based on action
        if action == 'buy' and not has_position:
            # Place buy order
            order = api.submit_order(
                symbol=SYMBOL,
                qty=POSITION_SIZE,
                side='buy',
                type='market',
                time_in_force='day'
            )
            logger.info(f"BUY order placed: {order}")
            return jsonify({
                'status': 'success',
                'action': 'buy',
                'order_id': order.id,
                'qty': POSITION_SIZE
            })
            
        elif action == 'sell' and not has_position:
            # Place sell order (short)
            order = api.submit_order(
                symbol=SYMBOL,
                qty=POSITION_SIZE,
                side='sell',
                type='market',
                time_in_force='day'
            )
            logger.info(f"SELL order placed: {order}")
            return jsonify({
                'status': 'success',
                'action': 'sell',
                'order_id': order.id,
                'qty': POSITION_SIZE
            })
            
        elif action == 'close' and has_position:
            # Close position
            order = api.close_position(SYMBOL)
            logger.info(f"Position closed: {order}")
            return jsonify({
                'status': 'success',
                'action': 'close',
                'qty': current_qty
            })
        else:
            return jsonify({
                'status': 'skipped',
                'reason': 'Already in position or no position to close'
            })
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Check account status"""
    try:
        account = api.get_account()
        positions = api.list_positions()
        
        return jsonify({
            'status': 'running',
            'account': {
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash)
            },
            'positions': [
                {
                    'symbol': p.symbol,
                    'qty': int(p.qty),
                    'side': p.side,
                    'avg_entry_price': float(p.avg_entry_price),
                    'current_price': float(p.current_price),
                    'unrealized_pl': float(p.unrealized_pl)
                }
                for p in positions
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Alpaca webhook server is running!',
        'symbol': SYMBOL,
        'position_size': POSITION_SIZE
    })

if __name__ == '__main__':
    print("""
    🦙 Alpaca Webhook Server for VWAP Strategy
    ==========================================
    
    1. Set up your Alpaca account at: https://alpaca.markets
    2. Get your API keys from the dashboard
    3. Set environment variables:
       export ALPACA_API_KEY='your_key'
       export ALPACA_SECRET_KEY='your_secret'
    
    4. In TradingView alerts, set webhook URL to:
       http://your-server:5000/webhook/tradingview
    
    5. Alert message format:
       {"action": "buy"}   - For buy signals
       {"action": "sell"}  - For sell signals
       {"action": "close"} - To close positions
    
    Server running on http://localhost:5000
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=True)