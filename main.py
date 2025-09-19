# region imports
from AlgorithmImports import *
import random
import numpy as np
from datetime import datetime, timedelta
# endregion

class SleepySkyBlueAlligator(QCAlgorithm):
    """
    BTC Trading System with Kraken Integration
    - Random buy/sell decisions with deterministic seed
    - 3% Stop Loss Risk Management (best performing strategy from risk analysis)
    - Proper Kraken fee modeling
    - Real-time position tracking and risk management
    """

    def initialize(self):
        """Initialize the algorithm"""
        # Basic setup
        self.set_start_date(2024, 1, 1)
        self.set_end_date(2024, 12, 31)
        self.set_cash(100000)  # $100k starting capital

        # Add BTC/USD symbol (Kraken format)
        self.btc_symbol = self.add_crypto("BTCUSD", Resolution.MINUTE, Market.KRAKEN)

        # Trading parameters
        self.deterministic_seed = 42  # Fixed seed for reproducible randomness
        random.seed(self.deterministic_seed)
        np.random.seed(self.deterministic_seed)

        # Risk management parameters (from risk analysis results)
        self.stop_loss_pct = 0.03  # 3% stop loss (best performing strategy)
        self.position_size = 0.95  # Use 95% of available capital

        # Kraken fee structure (maker/taker fees)
        self.kraken_maker_fee = 0.0016  # 0.16% maker fee
        self.kraken_taker_fee = 0.0026  # 0.26% taker fee
        self.current_fee_rate = self.kraken_taker_fee  # Default to taker

        # State tracking
        self.entry_price = 0
        self.stop_loss_price = 0
        self.position_side = None  # 'long', 'short', or None
        self.last_trade_time = None
        self.min_trade_interval = timedelta(minutes=5)  # Minimum time between trades

        # Performance tracking
        self.trade_count = 0
        self.winning_trades = 0
        self.total_fees_paid = 0

        # Schedule risk management check every minute
        self.schedule.on(
            self.date_rules.every_day(),
            self.time_rules.every(timedelta(minutes=1)),
            self.check_risk_management
        )
        

    def on_data(self, data: Slice):
        """Main data processing and trading logic"""
        if not data.contains_key(self.btc_symbol):
            return

        current_price = data[self.btc_symbol].price
        current_time = self.time

        # Skip if too soon since last trade
        if (self.last_trade_time and
            current_time - self.last_trade_time < self.min_trade_interval):
            return

        # Generate random trading decision
        if self.should_trade():
            self.execute_trade(current_price, current_time)

    def should_trade(self) -> bool:
        """Generate random trading decision with deterministic seed"""
        # Reset seed periodically to maintain determinism
        if self.trade_count % 100 == 0:
            random.seed(self.deterministic_seed + self.trade_count)

        # Random decision: 30% chance to trade when not in position
        if self.position_side is None:
            return random.random() < 0.3

        return False

    def execute_trade(self, price: float, timestamp: datetime):
        """Execute buy or sell trade based on random decision"""
        # Random decision: 50% long, 50% short
        is_long = random.random() < 0.5

        if is_long:
            self.enter_long_position(price, timestamp)
        else:
            self.enter_short_position(price, timestamp)

    def enter_long_position(self, price: float, timestamp: datetime):
        """Enter long position with risk management"""
        if self.cash <= 0:
            return

        # Calculate position size
        available_cash = self.cash * self.position_size
        position_value = available_cash / (1 + self.current_fee_rate)  # Account for fees

        # Set stop loss
        self.entry_price = price
        self.stop_loss_price = price * (1 - self.stop_loss_pct)
        self.position_side = 'long'
        self.last_trade_time = timestamp

        # Execute buy order
        self.set_holdings(self.btc_symbol, self.position_size)

        # Calculate and track fees
        fee_paid = position_value * self.current_fee_rate
        self.total_fees_paid += fee_paid

        self.trade_count += 1
        self.log(f"LONG Entry #{self.trade_count}: ${price:,.2f} | Stop: ${self.stop_loss_price:,.2f} | Fee: ${fee_paid:.2f}")

    def enter_short_position(self, price: float, timestamp: datetime):
        """Enter short position with risk management"""
        if self.portfolio[self.btc_symbol].quantity >= 0:
            return

        # For short positions, we'll use a different approach
        # Since QuantConnect doesn't directly support shorting crypto, we'll simulate it
        # by going to cash and tracking the short position manually

        # Set stop loss (for short: stop loss is above entry price)
        self.entry_price = price
        self.stop_loss_price = price * (1 + self.stop_loss_pct)
        self.position_side = 'short'
        self.last_trade_time = timestamp

        # Go to cash (simulating short position)
        self.set_holdings(self.btc_symbol, 0)

        # Calculate and track fees
        position_value = self.portfolio.total_portfolio_value * self.position_size
        fee_paid = position_value * self.current_fee_rate
        self.total_fees_paid += fee_paid

        self.trade_count += 1
        self.log(f"SHORT Entry #{self.trade_count}: ${price:,.2f} | Stop: ${self.stop_loss_price:,.2f} | Fee: ${fee_paid:.2f}")

    def check_risk_management(self):
        """Check stop loss and other risk management rules"""
        if self.position_side is None:
            return

        current_price = self.securities[self.btc_symbol].price

        if self.position_side == 'long':
            if current_price <= self.stop_loss_price:
                self.exit_position(current_price, "Stop Loss Hit")

        elif self.position_side == 'short':
            if current_price >= self.stop_loss_price:
                self.exit_position(current_price, "Stop Loss Hit")

    def exit_position(self, price: float, reason: str):
        """Exit current position"""
        if self.position_side is None:
            return

        # Calculate P&L
        if self.position_side == 'long':
            pnl_pct = (price - self.entry_price) / self.entry_price
        else:  # short
            pnl_pct = (self.entry_price - price) / self.entry_price

        # Track win/loss
        if pnl_pct > 0:
            self.winning_trades += 1

        # Calculate fees for exit
        position_value = self.portfolio.total_portfolio_value * self.position_size
        exit_fee = position_value * self.current_fee_rate
        self.total_fees_paid += exit_fee

        # Exit position
        self.set_holdings(self.btc_symbol, 0)

        # Log trade result
        win_rate = (self.winning_trades / self.trade_count) * 100 if self.trade_count > 0 else 0
        self.log(f"EXIT #{self.trade_count}: {reason} | P&L: {pnl_pct*100:+.2f}% | Win Rate: {win_rate:.1f}% | Total Fees: ${self.total_fees_paid:.2f}")

        # Reset position tracking
        self.position_side = None
        self.entry_price = 0
        self.stop_loss_price = 0

    def on_end_of_algorithm(self):
        """Final performance summary"""
        total_return = (self.portfolio.total_portfolio_value - 100000) / 100000 * 100
        win_rate = (self.winning_trades / self.trade_count) * 100 if self.trade_count > 0 else 0

        # Log final performance summary
        self.log(f"ALGORITHM COMPLETE - Total Return: {total_return:+.2f}% | Win Rate: {win_rate:.1f}% | Total Trades: {self.trade_count} | Total Fees: ${self.total_fees_paid:.2f}")
 