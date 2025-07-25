from ib_insync import IB, Stock, Option, MarketOrder, LimitOrder
import datetime
import time
import os

# Configuration
IB_HOST = '127.0.0.1'  # Localhost (default for TWS/Gateway)
IB_PORT = 7497          # 7497 for paper trading, 7496 for live
CLIENT_ID = 1           # Any integer (should be unique per client)

# Trading parameters
SYMBOL = 'SPX'
EXCHANGE = 'SMART'
CURRENCY = 'USD'

# Target time to place orders (21:50 = 9:50pm local time)
TARGET_HOUR = 21
TARGET_MINUTE = 50

# Strategy parameters
COMBO_NET_CREDIT = 0.15  # Target net credit for the spread
STOP_LOSS = -1.0         # Stop loss per spread
MAX_RETRIES = 2          # Error handling retries

LOG_FILE = 'trades.log'
STOP_FILE = 'STOP'


def log_trade(message):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.datetime.now()}: {message}\n")


def connect_ib():
    ib = IB()
    ib.connect(IB_HOST, IB_PORT, clientId=CLIENT_ID)
    if ib.isConnected():
        print('Connected to Interactive Brokers!')
    else:
        print('Failed to connect to Interactive Brokers.')
    return ib


def fetch_spx_data(ib):
    spx = Stock(SYMBOL, EXCHANGE, CURRENCY)
    ticker = ib.reqMktData(spx, '', False, False)
    ib.sleep(2)  # Wait for data to populate
    print(f"SPX Last Price: {ticker.last}")
    print(f"SPX Bid: {ticker.bid}, Ask: {ticker.ask}")
    return ticker


def wait_until_target_time():
    now = datetime.datetime.now()
    target = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)
    if now > target:
        # If it's already past the target time today, wait until tomorrow
        target += datetime.timedelta(days=1)
    print(f"Waiting until {target.strftime('%Y-%m-%d %H:%M:%S')} to place orders...")
    while datetime.datetime.now() < target:
        if os.path.exists(STOP_FILE):
            print("Manual STOP file detected. Exiting.")
            log_trade("Manual STOP file detected. Exiting.")
            exit(0)
        time.sleep(10)  # Sleep in 10-second intervals


def get_0dte_expiry():
    return datetime.datetime.now().strftime('%Y%m%d')


def select_put_spread_strikes(ib, spx_price):
    # Example: short OTM put (e.g., 1% below spot), long farther OTM put (e.g., 2% below spot)
    short_strike = round(spx_price * 0.99 / 5) * 5
    long_strike = round(spx_price * 0.98 / 5) * 5
    expiry = get_0dte_expiry()
    short_put = Option(SYMBOL, expiry, short_strike, 'P', EXCHANGE)
    long_put = Option(SYMBOL, expiry, long_strike, 'P', EXCHANGE)
    return short_put, long_put


def calculate_max_contracts(ib, short_put, long_put):
    # Stub: Use all available capital (replace with real margin/capital calculation)
    # For now, return 1 contract for safety
    return 1


def place_put_spread(ib, short_put, long_put, contracts):
    # Request market data for both options
    short_ticker = ib.reqMktData(short_put, '', False, False)
    long_ticker = ib.reqMktData(long_put, '', False, False)
    ib.sleep(2)
    # Calculate mid price for the spread
    net_credit = (short_ticker.bid + short_ticker.ask)/2 - (long_ticker.bid + long_ticker.ask)/2
    print(f"Calculated net credit for spread: {net_credit}")
    log_trade(f"Calculated net credit for spread: {net_credit}")
    if net_credit < COMBO_NET_CREDIT:
        print(f"Net credit {net_credit} is less than target {COMBO_NET_CREDIT}. Not trading.")
        log_trade(f"Net credit {net_credit} is less than target {COMBO_NET_CREDIT}. Not trading.")
        return
    # Place limit order for the spread (stub)
    print(f"Would place limit order to sell {contracts} put spread(s) at net credit {net_credit}")
    log_trade(f"Would place limit order to sell {contracts} put spread(s) at net credit {net_credit}")
    # TODO: Implement actual combo order placement


def main():
    ib = connect_ib()
    ticker = fetch_spx_data(ib)
    wait_until_target_time()
    spx_price = ticker.last
    short_put, long_put = select_put_spread_strikes(ib, spx_price)
    contracts = calculate_max_contracts(ib, short_put, long_put)
    retries = 0
    while retries <= MAX_RETRIES:
        try:
            place_put_spread(ib, short_put, long_put, contracts)
            break
        except Exception as e:
            print(f"Error placing order: {e}")
            log_trade(f"Error placing order: {e}")
            retries += 1
            if retries > MAX_RETRIES:
                print("Max retries reached. Aborting.")
                log_trade("Max retries reached. Aborting.")
    ib.disconnect()

if __name__ == '__main__':
    main() 