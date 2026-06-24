"""
Interactive Brokers Live Trading Bot
Implements Triple_Optimized strategy with real-time execution
"""
import asyncio
import nest_asyncio
import pandas as pd
import numpy as np
from datetime import datetime, time
import logging
import os
import sys
from typing import Dict, List, Optional, Tuple
import signal
import json

# Allow nested event loops (for Jupyter compatibility)
nest_asyncio.apply()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ib_insync import IB, Stock, Index, Future, Contract, MarketOrder, LimitOrder, StopOrder
from ib_insync import util

from ib_config import (IB_CONFIG, CONTRACT_CONFIG, POSITION_CONFIG, 
                      RISK_CONFIG, NOTIFICATION_CONFIG, DATA_CONFIG, 
                      LOGGING_CONFIG, STRATEGY_OVERRIDE)
from src.indicators_simple import TechnicalIndicators
from src.strategy import TradingStrategy

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['log_level']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['log_file']),
        logging.StreamHandler() if LOGGING_CONFIG['enable_console_log'] else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)


class IBLiveTrader:
    """
    Live trading bot for Interactive Brokers
    """
    
    def __init__(self):
        self.ib = IB()
        self.connected = False
        self.running = False
        
        # Initialize components
        self.indicators = TechnicalIndicators()
        self.strategy = TradingStrategy(
            capital=100000,  # Will be updated with real account value
            risk_per_trade=POSITION_CONFIG['risk_per_trade']
        )
        
        # Data storage
        self.bars_df = pd.DataFrame()
        self.current_position = None
        self.daily_trades = 0
        self.daily_pnl = 0
        self.last_trade_time = None
        
        # Contracts
        self.data_contract = None
        self.trade_contract = None
        
        # Orders
        self.pending_orders = {}
        self.active_orders = {}
        
        # Strategy parameters (Triple_Optimized)
        self.strategy_params = {
            'RSI': {'periods': [9], 'oversold': [25], 'overbought': [75]},
            'MACD': {'fast': [8], 'slow': [21], 'signal': [5]},
            'EMA': {'short_periods': [5], 'long_periods': [20]}
        }
        
        # Apply overrides if enabled
        if STRATEGY_OVERRIDE['enabled']:
            self.min_confirmations = STRATEGY_OVERRIDE['min_confirmations']
        else:
            self.min_confirmations = 1
            
    async def connect(self):
        """Connect to IB Gateway/TWS"""
        try:
            await self.ib.connectAsync(
                host=IB_CONFIG['host'],
                port=IB_CONFIG['port'],
                clientId=IB_CONFIG['client_id']
            )
            self.connected = True
            logger.info(f"Connected to IB on {IB_CONFIG['host']}:{IB_CONFIG['port']}")
            
            # Set up contracts
            await self._setup_contracts()
            
            # Get account info
            await self._update_account_info()
            
            # Subscribe to events
            self._setup_event_handlers()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to IB: {e}")
            return False
    
    async def _setup_contracts(self):
        """Set up data and trading contracts"""
        # Data contract (SPX index for signals)
        self.data_contract = Index(
            symbol=CONTRACT_CONFIG['symbol'],
            exchange=CONTRACT_CONFIG['exchange'],
            currency=CONTRACT_CONFIG['currency']
        )
        
        # Trading contract (SPY ETF or ES futures)
        if CONTRACT_CONFIG['tradeable_sec_type'] == 'STK':
            self.trade_contract = Stock(
                symbol=CONTRACT_CONFIG['tradeable_symbol'],
                exchange=CONTRACT_CONFIG['tradeable_exchange'],
                currency=CONTRACT_CONFIG['tradeable_currency']
            )
        elif CONTRACT_CONFIG['tradeable_sec_type'] == 'FUT':
            # For futures, you'd need to specify the exact contract
            # This is a simplified example
            self.trade_contract = Future(
                symbol=CONTRACT_CONFIG['tradeable_symbol'],
                exchange=CONTRACT_CONFIG['tradeable_exchange'],
                currency=CONTRACT_CONFIG['tradeable_currency']
            )
        
        # Qualify contracts
        await self.ib.qualifyContractsAsync(self.data_contract, self.trade_contract)
        logger.info(f"Contracts qualified: Data={self.data_contract}, Trade={self.trade_contract}")
    
    async def _update_account_info(self):
        """Update account information"""
        account_values = await self.ib.accountValuesAsync()
        for av in account_values:
            if av.tag == 'NetLiquidation':
                self.strategy.capital = float(av.value)
                logger.info(f"Account Net Liquidation: ${av.value}")
            elif av.tag == 'AvailableFunds':
                logger.info(f"Available Funds: ${av.value}")
    
    def _setup_event_handlers(self):
        """Set up IB event handlers"""
        self.ib.orderStatusEvent += self._on_order_status
        self.ib.execDetailsEvent += self._on_execution
        self.ib.errorEvent += self._on_error
        self.ib.positionEvent += self._on_position_update
    
    def _on_order_status(self, trade):
        """Handle order status updates"""
        logger.info(f"Order Status: {trade.order.orderId} - {trade.orderStatus.status}")
        
        if trade.orderStatus.status == 'Filled':
            self._handle_filled_order(trade)
        elif trade.orderStatus.status in ['Cancelled', 'ApiCancelled']:
            self._handle_cancelled_order(trade)
    
    def _on_execution(self, trade, fill):
        """Handle trade executions"""
        logger.info(f"Execution: {fill.contract.symbol} {fill.execution.side} "
                   f"{fill.execution.shares} @ {fill.execution.price}")
        
        # Log to trade file
        self._log_trade(fill)
        
        # Send notification
        self._send_notification(
            f"Trade Executed: {fill.execution.side} {fill.execution.shares} "
            f"{fill.contract.symbol} @ ${fill.execution.price:.2f}"
        )
    
    def _on_error(self, reqId, errorCode, errorString, contract):
        """Handle IB errors"""
        if errorCode not in [2104, 2106, 2158]:  # Ignore market data farm messages
            logger.error(f"IB Error {errorCode}: {errorString}")
    
    def _on_position_update(self, position):
        """Handle position updates"""
        if position.contract == self.trade_contract:
            logger.info(f"Position Update: {position.position} @ {position.avgCost}")
    
    async def start_trading(self):
        """Start the trading bot"""
        if not self.connected:
            logger.error("Not connected to IB")
            return
        
        self.running = True
        logger.info("Starting live trading bot...")
        
        # Request real-time bars
        self.bars = await self.ib.reqRealTimeBarsAsync(
            self.data_contract,
            barSize=5,  # 5 second bars
            whatToShow='TRADES',
            useRTH=True
        )
        
        # Get historical data for indicators
        await self._load_historical_data()
        
        # Main trading loop
        while self.running:
            try:
                await self._trading_loop()
                await asyncio.sleep(DATA_CONFIG['update_frequency'])
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _load_historical_data(self):
        """Load historical data for indicator calculation"""
        bars = await self.ib.reqHistoricalDataAsync(
            self.data_contract,
            endDateTime='',
            durationStr='2 D',
            barSizeSetting=DATA_CONFIG['bar_size'],
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )
        
        # Convert to DataFrame
        self.bars_df = util.df(bars)
        self.bars_df.set_index('date', inplace=True)
        
        # Rename columns to match our format
        self.bars_df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True)
        
        logger.info(f"Loaded {len(self.bars_df)} historical bars")
    
    async def _trading_loop(self):
        """Main trading loop"""
        current_time = datetime.now()
        
        # Check if market is open
        if not self._is_market_open(current_time):
            return
        
        # Check daily stop loss
        if self._check_daily_stop_loss():
            logger.warning("Daily stop loss hit, stopping trading for today")
            await self._close_all_positions()
            self.running = False
            return
        
        # Update bars with latest data
        if hasattr(self, 'bars') and self.bars:
            latest_bar = self.bars[-1]
            new_row = pd.DataFrame({
                'Open': [latest_bar.open],
                'High': [latest_bar.high],
                'Low': [latest_bar.low],
                'Close': [latest_bar.close],
                'Volume': [latest_bar.volume]
            }, index=[latest_bar.time])
            
            self.bars_df = pd.concat([self.bars_df, new_row])
            self.bars_df = self.bars_df.tail(DATA_CONFIG['lookback_periods'])
        
        # Calculate indicators
        data_with_indicators = self.indicators.calculate_all_indicators(
            self.bars_df.copy(), 
            self.strategy_params
        )
        
        # Generate signals
        signals = self._generate_signals(data_with_indicators)
        
        # Check for force close time
        if current_time.time() >= datetime.strptime(RISK_CONFIG['force_close_time'], '%H:%M').time():
            await self._close_all_positions()
            return
        
        # Execute trades based on signals
        await self._execute_signals(signals, data_with_indicators)
    
    def _generate_signals(self, data: pd.DataFrame) -> Dict:
        """Generate trading signals"""
        # Get latest values
        latest = data.iloc[-1]
        
        # Initialize signal
        signal = {
            'action': 0,  # 0: hold, 1: buy, -1: sell
            'strength': 0,
            'stop_loss': 0,
            'take_profit': 0
        }
        
        # Count confirmations
        long_signals = 0
        short_signals = 0
        
        # RSI signals
        if 'RSI_9' in data.columns:
            if latest['RSI_9'] < 25:  # Oversold
                long_signals += 1
            elif latest['RSI_9'] > 75:  # Overbought
                short_signals += 1
        
        # MACD signals
        if 'MACD_8_21_5' in data.columns:
            if latest['MACD_8_21_5'] > latest['MACD_8_21_5_signal']:
                if data['MACD_8_21_5'].iloc[-2] <= data['MACD_8_21_5_signal'].iloc[-2]:
                    long_signals += 1
            elif latest['MACD_8_21_5'] < latest['MACD_8_21_5_signal']:
                if data['MACD_8_21_5'].iloc[-2] >= data['MACD_8_21_5_signal'].iloc[-2]:
                    short_signals += 1
        
        # EMA crossover signals
        if 'EMA_5' in data.columns and 'EMA_20' in data.columns:
            if latest['EMA_5'] > latest['EMA_20']:
                if data['EMA_5'].iloc[-2] <= data['EMA_20'].iloc[-2]:
                    long_signals += 1
            elif latest['EMA_5'] < latest['EMA_20']:
                if data['EMA_5'].iloc[-2] >= data['EMA_20'].iloc[-2]:
                    short_signals += 1
        
        # Determine action based on confirmations
        if long_signals >= self.min_confirmations and self.current_position is None:
            signal['action'] = 1
            signal['strength'] = long_signals
            
            # Calculate stop loss and take profit
            atr = latest.get('ATR_14', latest['Close'] * 0.01)
            signal['stop_loss'] = latest['Close'] - (atr * 1.0 * STRATEGY_OVERRIDE['stop_loss_multiplier'])
            signal['take_profit'] = latest['Close'] + (atr * 4.0 * STRATEGY_OVERRIDE['take_profit_multiplier'])
            
        elif short_signals >= self.min_confirmations and self.current_position is None:
            signal['action'] = -1
            signal['strength'] = short_signals
            
            # Calculate stop loss and take profit
            atr = latest.get('ATR_14', latest['Close'] * 0.01)
            signal['stop_loss'] = latest['Close'] + (atr * 1.0 * STRATEGY_OVERRIDE['stop_loss_multiplier'])
            signal['take_profit'] = latest['Close'] - (atr * 4.0 * STRATEGY_OVERRIDE['take_profit_multiplier'])
        
        return signal
    
    async def _execute_signals(self, signal: Dict, data: pd.DataFrame):
        """Execute trading signals"""
        if signal['action'] == 0:
            return
        
        # Check if we've hit max daily trades
        if self.daily_trades >= POSITION_CONFIG['max_daily_trades']:
            logger.info("Max daily trades reached")
            return
        
        # Get current price
        ticker = await self.ib.reqTickersAsync(self.trade_contract)
        if not ticker:
            logger.error("Could not get current price")
            return
        
        current_price = ticker[0].marketPrice()
        
        # Calculate position size
        position_size = self._calculate_position_size(
            current_price, 
            signal['stop_loss']
        )
        
        if position_size == 0:
            logger.info("Position size is 0, skipping trade")
            return
        
        # Create orders
        if signal['action'] == 1:  # Buy
            await self._place_buy_order(position_size, current_price, signal)
        elif signal['action'] == -1:  # Sell
            await self._place_sell_order(position_size, current_price, signal)
    
    def _calculate_position_size(self, price: float, stop_loss: float) -> int:
        """Calculate position size based on risk"""
        if POSITION_CONFIG['position_sizing_method'] == 'fixed':
            return min(POSITION_CONFIG['max_position_size'], 100)
        else:
            # Risk-based sizing
            risk_amount = self.strategy.capital * POSITION_CONFIG['risk_per_trade']
            risk_per_share = abs(price - stop_loss)
            
            if risk_per_share > 0:
                shares = int(risk_amount / risk_per_share)
                return min(shares, POSITION_CONFIG['max_position_size'])
            else:
                return POSITION_CONFIG['max_position_size']
    
    async def _place_buy_order(self, quantity: int, price: float, signal: Dict):
        """Place buy order with stop loss and take profit"""
        try:
            # Main order
            main_order = MarketOrder('BUY', quantity)
            main_trade = await self.ib.placeOrderAsync(self.trade_contract, main_order)
            
            logger.info(f"Placed BUY order for {quantity} shares")
            
            # Store position info
            self.current_position = {
                'side': 'BUY',
                'quantity': quantity,
                'entry_price': price,
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'entry_time': datetime.now()
            }
            
            # Wait for fill
            await asyncio.sleep(1)
            
            # Place stop loss order
            stop_order = StopOrder('SELL', quantity, signal['stop_loss'])
            stop_trade = await self.ib.placeOrderAsync(self.trade_contract, stop_order)
            
            # Place take profit order
            tp_order = LimitOrder('SELL', quantity, signal['take_profit'])
            tp_trade = await self.ib.placeOrderAsync(self.trade_contract, tp_order)
            
            # Store order references
            self.active_orders = {
                'main': main_trade,
                'stop_loss': stop_trade,
                'take_profit': tp_trade
            }
            
            self.daily_trades += 1
            self.last_trade_time = datetime.now()
            
            # Send notification
            self._send_notification(
                f"BUY Signal Executed\n"
                f"Quantity: {quantity}\n"
                f"Entry: ${price:.2f}\n"
                f"Stop Loss: ${signal['stop_loss']:.2f}\n"
                f"Take Profit: ${signal['take_profit']:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Error placing buy order: {e}")
    
    async def _place_sell_order(self, quantity: int, price: float, signal: Dict):
        """Place sell order with stop loss and take profit"""
        try:
            # Main order
            main_order = MarketOrder('SELL', quantity)
            main_trade = await self.ib.placeOrderAsync(self.trade_contract, main_order)
            
            logger.info(f"Placed SELL order for {quantity} shares")
            
            # Store position info
            self.current_position = {
                'side': 'SELL',
                'quantity': quantity,
                'entry_price': price,
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'entry_time': datetime.now()
            }
            
            # Wait for fill
            await asyncio.sleep(1)
            
            # Place stop loss order
            stop_order = StopOrder('BUY', quantity, signal['stop_loss'])
            stop_trade = await self.ib.placeOrderAsync(self.trade_contract, stop_order)
            
            # Place take profit order
            tp_order = LimitOrder('BUY', quantity, signal['take_profit'])
            tp_trade = await self.ib.placeOrderAsync(self.trade_contract, tp_order)
            
            # Store order references
            self.active_orders = {
                'main': main_trade,
                'stop_loss': stop_trade,
                'take_profit': tp_trade
            }
            
            self.daily_trades += 1
            self.last_trade_time = datetime.now()
            
            # Send notification
            self._send_notification(
                f"SELL Signal Executed\n"
                f"Quantity: {quantity}\n"
                f"Entry: ${price:.2f}\n"
                f"Stop Loss: ${signal['stop_loss']:.2f}\n"
                f"Take Profit: ${signal['take_profit']:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Error placing sell order: {e}")
    
    def _handle_filled_order(self, trade):
        """Handle filled orders"""
        # Check if it's a closing order
        if self.current_position and trade.order.action != self.current_position['side']:
            # Position closed
            fill_price = trade.orderStatus.avgFillPrice
            pnl = self._calculate_pnl(fill_price)
            
            self.daily_pnl += pnl
            
            logger.info(f"Position closed at ${fill_price:.2f}, P&L: ${pnl:.2f}")
            
            # Cancel remaining orders
            self._cancel_remaining_orders()
            
            # Clear position
            self.current_position = None
            
            # Send notification
            self._send_notification(
                f"Position Closed\n"
                f"Exit Price: ${fill_price:.2f}\n"
                f"P&L: ${pnl:.2f}\n"
                f"Daily P&L: ${self.daily_pnl:.2f}"
            )
    
    def _calculate_pnl(self, exit_price: float) -> float:
        """Calculate P&L for current position"""
        if not self.current_position:
            return 0
        
        entry = self.current_position['entry_price']
        quantity = self.current_position['quantity']
        
        if self.current_position['side'] == 'BUY':
            return (exit_price - entry) * quantity
        else:
            return (entry - exit_price) * quantity
    
    def _cancel_remaining_orders(self):
        """Cancel all remaining orders"""
        for order_type, trade in self.active_orders.items():
            if trade.orderStatus.status not in ['Filled', 'Cancelled']:
                self.ib.cancelOrder(trade.order)
                logger.info(f"Cancelled {order_type} order")
    
    async def _close_all_positions(self):
        """Close all open positions"""
        positions = await self.ib.positionsAsync()
        
        for position in positions:
            if position.contract == self.trade_contract and position.position != 0:
                # Create closing order
                action = 'SELL' if position.position > 0 else 'BUY'
                quantity = abs(position.position)
                
                close_order = MarketOrder(action, quantity)
                await self.ib.placeOrderAsync(self.trade_contract, close_order)
                
                logger.info(f"Closing position: {action} {quantity} shares")
    
    def _is_market_open(self, current_time: datetime) -> bool:
        """Check if market is open"""
        # US market hours (EST)
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        # Check weekday (0 = Monday, 4 = Friday)
        if current_time.weekday() > 4:
            return False
        
        # Check time
        current_time_only = current_time.time()
        return market_open <= current_time_only <= market_close
    
    def _check_daily_stop_loss(self) -> bool:
        """Check if daily stop loss is hit"""
        max_loss = self.strategy.capital * RISK_CONFIG['max_daily_loss']
        return self.daily_pnl <= -max_loss
    
    def _log_trade(self, fill):
        """Log trade to CSV file"""
        trade_data = {
            'timestamp': datetime.now(),
            'symbol': fill.contract.symbol,
            'action': fill.execution.side,
            'quantity': fill.execution.shares,
            'price': fill.execution.price,
            'commission': fill.commissionReport.commission if fill.commissionReport else 0
        }
        
        # Append to CSV
        df = pd.DataFrame([trade_data])
        df.to_csv(LOGGING_CONFIG['trade_log_file'], mode='a', header=False, index=False)
    
    def _send_notification(self, message: str):
        """Send notification via configured channels"""
        logger.info(f"Notification: {message}")
        
        # Telegram notification
        if NOTIFICATION_CONFIG['telegram_enabled']:
            # Implement telegram notification
            pass
        
        # Email notification
        if NOTIFICATION_CONFIG['email_enabled']:
            # Implement email notification
            pass
    
    def _handle_cancelled_order(self, trade):
        """Handle cancelled orders"""
        logger.info(f"Order cancelled: {trade.order.orderId}")
    
    async def stop_trading(self):
        """Stop the trading bot"""
        logger.info("Stopping trading bot...")
        
        self.running = False
        
        # Close all positions
        await self._close_all_positions()
        
        # Cancel all orders
        self.ib.cancelAllOrders()
        
        # Disconnect
        if self.connected:
            self.ib.disconnect()
            self.connected = False
        
        logger.info("Trading bot stopped")
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.daily_trades = 0
        self.daily_pnl = 0
        logger.info("Daily stats reset")


async def main():
    """Main function to run the trading bot"""
    trader = IBLiveTrader()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        asyncio.create_task(trader.stop_trading())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Connect to IB
        if await trader.connect():
            logger.info("Successfully connected to IB")
            
            # Start trading
            await trader.start_trading()
        else:
            logger.error("Failed to connect to IB")
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await trader.stop_trading()


if __name__ == "__main__":
    asyncio.run(main())