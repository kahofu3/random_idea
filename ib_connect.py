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
    # If no price data, exit
    if ticker.last is None and ticker.bid is None and ticker.ask is None:
        print("No SPX market data available. Exiting.")
        log_trade("No SPX market data available. Exiting.")
        ib.disconnect()
        exit(1)
    # Monitor for price changes for 15 seconds
    initial = (ticker.last, ticker.bid, ticker.ask)
    changed = False
    for _ in range(15):  # Check every second for 15 seconds
        ib.sleep(1)
        if (ticker.last, ticker.bid, ticker.ask) != initial:
            changed = True
            break
    if not changed:
        print("No SPX market activity detected in 15 seconds.")
        log_trade("No SPX market activity detected in 15 seconds.")
        answer = input("No SPX market activity detected. Do you want to quit? (y/n): ").strip().lower()
        if answer == 'y':
            print("Exiting as requested by user.")
            log_trade("User chose to exit due to no market activity.")
            ib.disconnect()
            exit(0)
        else:
            print("Continuing as requested by user.")
            log_trade("User chose to continue despite no market activity.")
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


def fetch_put_chain(ib, expiry):
    # Fetch the full SPX put options chain for 0DTE expiry
    spx = Stock(SYMBOL, EXCHANGE, CURRENCY)
    chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)
    strikes = []
    for chain in chains:
        if chain.tradingClass == SYMBOL and expiry in chain.expirations:
            strikes = sorted([float(s) for s in chain.strikes if float(s) < 10000])
            break
    puts = [Option(SYMBOL, expiry, strike, 'P', EXCHANGE) for strike in strikes]
    return puts


def get_mid_price(ib, option):
    ticker = ib.reqMktData(option, '', False, False)
    ib.sleep(0.5)
    if ticker.bid is not None and ticker.ask is not None:
        return (ticker.bid + ticker.ask) / 2
    return None


def select_farthest_put_spread(ib, puts):
    # Try all possible OTM put spreads, farthest OTM first
    best_pair = None
    for i in range(len(puts) - 1, 0, -1):
        for j in range(i - 1, -1, -1):
            short_put = puts[j]
            long_put = puts[i]
            short_mid = get_mid_price(ib, short_put)
            long_mid = get_mid_price(ib, long_put)
            if short_mid is None or long_mid is None:
                continue
            net_credit = short_mid - long_mid
            if net_credit >= COMBO_NET_CREDIT:
                best_pair = (short_put, long_put, net_credit)
                # Since we're going from farthest OTM, take the first that matches
                return best_pair
    return None


def calculate_max_contracts(ib, short_put, long_put):
    # Stub: Use all available capital (replace with real margin/capital calculation)
    # For now, return 1 contract for safety
    return 1


def place_put_spread(ib, short_put, long_put, contracts, net_credit):
    print(f"Would place limit order to sell {contracts} put spread(s) at net credit {net_credit}")
    log_trade(f"Would place limit order to sell {contracts} put spread(s) at net credit {net_credit}")
    # TODO: Implement actual combo order placement


def check_spx_options_activity(ib, puts, wait_seconds=10):
    """
    Check if any SPX put options in the list have trading activity (price or volume change).
    Returns True if activity is detected, False otherwise.
    """
    tickers = [ib.reqMktData(opt, '', False, False) for opt in puts]
    ib.sleep(1)
    initial = [(t.last, t.bid, t.ask, t.volume) for t in tickers]
    for _ in range(wait_seconds):
        ib.sleep(1)
        for idx, t in enumerate(tickers):
            if (t.last, t.bid, t.ask, t.volume) != initial[idx]:
                return True  # Activity detected
    return False  # No activity detected


def main():
    ib = connect_ib()
    ticker = fetch_spx_data(ib)
    wait_until_target_time()
    expiry = get_0dte_expiry()
    puts = fetch_put_chain(ib, expiry)
    if not check_spx_options_activity(ib, puts, wait_seconds=10):
        print("No SPX options trading activity detected. Exiting.")
        log_trade("No SPX options trading activity detected. Exiting.")
        ib.disconnect()
        exit(0)
    result = select_farthest_put_spread(ib, puts)
    if result:
        short_put, long_put, net_credit = result
        contracts = calculate_max_contracts(ib, short_put, long_put)
        retries = 0
        while retries <= MAX_RETRIES:
            try:
                place_put_spread(ib, short_put, long_put, contracts, net_credit)
                break
            except Exception as e:
                print(f"Error placing order: {e}")
                log_trade(f"Error placing order: {e}")
                retries += 1
                if retries > MAX_RETRIES:
                    print("Max retries reached. Aborting.")
                    log_trade("Max retries reached. Aborting.")
    else:
        print("No suitable put spread found with net credit >= 0.15.")
        log_trade("No suitable put spread found with net credit >= 0.15.")
    ib.disconnect()

if __name__ == '__main__':
    main() 