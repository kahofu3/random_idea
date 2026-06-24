"""
Alpaca Quick Setup for VWAP Strategy
Run this to set up everything automatically!
"""
import os
import subprocess
import sys

print("""
🦙 Welcome to Alpaca VWAP Bot Setup!
====================================

This will set up automated trading for your VWAP strategy.
Let's get started...
""")

# Step 1: Check Python version
print("✓ Checking Python version...")
if sys.version_info < (3, 7):
    print("❌ Python 3.7+ required. Please upgrade.")
    sys.exit(1)
print(f"  Found Python {sys.version.split()[0]}")

# Step 2: Install required packages
print("\n✓ Installing required packages...")
packages = ['alpaca-trade-api', 'flask', 'python-dotenv']
for package in packages:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
print("  All packages installed!")

# Step 3: Create .env file
print("\n✓ Setting up configuration...")
print("\n" + "="*50)
print("IMPORTANT: Enter your Alpaca API credentials")
print("="*50)

api_key = input("Enter your Alpaca API Key ID: ").strip()
secret_key = input("Enter your Alpaca Secret Key: ").strip()

use_paper = input("\nUse paper trading? (yes/no) [yes]: ").strip().lower()
if use_paper != 'no':
    base_url = "https://paper-api.alpaca.markets"
    print("✓ Using PAPER trading (safe mode)")
else:
    base_url = "https://api.alpaca.markets"
    print("⚠️  Using LIVE trading (real money)")

# Save to .env file
with open('.env', 'w') as f:
    f.write(f"ALPACA_API_KEY={api_key}\n")
    f.write(f"ALPACA_SECRET_KEY={secret_key}\n")
    f.write(f"ALPACA_BASE_URL={base_url}\n")

print("✓ Configuration saved to .env file")

# Step 4: Test connection
print("\n✓ Testing Alpaca connection...")
try:
    import alpaca_trade_api as tradeapi
    from dotenv import load_dotenv
    
    load_dotenv()
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        os.getenv('ALPACA_BASE_URL'),
        api_version='v2'
    )
    
    account = api.get_account()
    print(f"  Connected successfully!")
    print(f"  Account Status: {account.status}")
    print(f"  Buying Power: ${float(account.buying_power):,.2f}")
    print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("   Please check your API keys and try again.")
    sys.exit(1)

# Step 5: Create the webhook server
print("\n✓ Creating webhook server...")
webhook_code = '''#!/usr/bin/env python3
"""
Alpaca VWAP Trading Bot
Auto-trades based on TradingView alerts
"""
from flask import Flask, request, jsonify
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import logging
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Alpaca
api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    os.getenv('ALPACA_BASE_URL'),
    api_version='v2'
)

# Configuration
SYMBOL = 'SPY'  # Trade SPY ETF
POSITION_SIZE = 10  # Start with 10 shares
MAX_POSITION = 100  # Maximum 100 shares

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle TradingView webhooks"""
    try:
        data = request.get_json()
        action = data.get('action', '').lower()
        
        logger.info(f"Received signal: {action}")
        
        # Get current position
        try:
            position = api.get_position(SYMBOL)
            current_qty = int(position.qty)
            logger.info(f"Current position: {current_qty} shares")
        except:
            current_qty = 0
            logger.info("No current position")
        
        # Execute trade
        if action == 'buy' and current_qty <= 0:
            # Buy signal - go long
            if current_qty < 0:
                # Close short first
                api.close_position(SYMBOL)
                logger.info("Closed short position")
            
            # Place buy order
            order = api.submit_order(
                symbol=SYMBOL,
                qty=POSITION_SIZE,
                side='buy',
                type='market',
                time_in_force='day'
            )
            logger.info(f"✅ BUY order placed: {POSITION_SIZE} shares of {SYMBOL}")
            
            return jsonify({
                'status': 'success',
                'action': 'buy',
                'qty': POSITION_SIZE,
                'order_id': order.id
            })
            
        elif action == 'sell' and current_qty >= 0:
            # Sell signal - go short
            if current_qty > 0:
                # Close long first
                api.close_position(SYMBOL)
                logger.info("Closed long position")
            
            # Place sell order
            order = api.submit_order(
                symbol=SYMBOL,
                qty=POSITION_SIZE,
                side='sell',
                type='market',
                time_in_force='day'
            )
            logger.info(f"✅ SELL order placed: {POSITION_SIZE} shares of {SYMBOL}")
            
            return jsonify({
                'status': 'success',
                'action': 'sell',
                'qty': POSITION_SIZE,
                'order_id': order.id
            })
            
        else:
            logger.info("Signal ignored - already in position")
            return jsonify({
                'status': 'ignored',
                'reason': 'Already in correct position'
            })
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Check bot status"""
    try:
        account = api.get_account()
        positions = api.list_positions()
        
        return jsonify({
            'status': 'running',
            'account': {
                'status': account.status,
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value)
            },
            'positions': [
                {
                    'symbol': p.symbol,
                    'qty': int(p.qty),
                    'side': p.side,
                    'profit_loss': float(p.unrealized_pl),
                    'profit_loss_pct': float(p.unrealized_plpc) * 100
                }
                for p in positions
            ],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return """
    <h1>🦙 Alpaca VWAP Trading Bot</h1>
    <p>Status: Running</p>
    <p>Check <a href="/status">/status</a> for account info</p>
    """

if __name__ == '__main__':
    print("""
    🦙 Alpaca VWAP Trading Bot Started!
    ==================================
    
    Webhook URL: http://localhost:5000/webhook
    Status URL: http://localhost:5000/status
    
    Waiting for TradingView signals...
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
'''

with open('alpaca_bot.py', 'w') as f:
    f.write(webhook_code)

print("✓ Created alpaca_bot.py")

# Step 6: Create start script
start_script = '''#!/bin/bash
echo "🦙 Starting Alpaca VWAP Bot..."
python3 alpaca_bot.py
'''

with open('start_bot.sh', 'w') as f:
    f.write(start_script)

os.chmod('start_bot.sh', 0o755)
print("✓ Created start_bot.sh")

# Done!
print("\n" + "="*50)
print("✅ SETUP COMPLETE!")
print("="*50)

print("""
Next Steps:
-----------
1. Start the bot:
   ./start_bot.sh
   
2. For public webhook access, use ngrok:
   ngrok http 5000
   
3. In TradingView, set alert webhook to:
   http://localhost:5000/webhook
   (or your ngrok URL)
   
4. Alert message format:
   {"action": "buy"} or {"action": "sell"}

5. Test status at:
   http://localhost:5000/status

Happy automated trading! 🚀
""")