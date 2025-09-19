# region imports
from AlgorithmImports import *
import random
from datetime import datetime, timedelta
# endregion

class SleepySkyBlueAlligator(QCAlgorithm):
    """Randomised long-only BTC strategy with a trailing stop mechanism."""

    def Initialize(self) -> None:
        self.SetStartDate(2024, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100000)

        self.btc_symbol = self.AddCrypto("BTCUSD", Resolution.Minute, Market.Kraken).Symbol

        random.seed(42)

        self.stop_loss_pct = 0.03
        self.entry_price = 0.0
        self.stop_loss_price = 0.0
        self.position_side = None
        self.last_trade_time = self.StartDate
        self.min_trade_interval = timedelta(minutes=5)

        self.trade_count = 0
        self.winning_trades = 0

    def OnData(self, data: Slice) -> None:
        if self.IsWarmingUp:
            return

        if self.btc_symbol not in data or data[self.btc_symbol] is None:
            return

        current_price = data[self.btc_symbol].Close
        current_time = self.Time

        if self.position_side == "long":
            self._check_stop_loss(current_price)

        if self.position_side is not None:
            return

        if current_time - self.last_trade_time < self.min_trade_interval:
            return

        if random.random() < 0.3:
            self._enter_long_position(current_price, current_time)

    def _enter_long_position(self, price: float, timestamp: datetime) -> None:
        if self.Portfolio.Cash <= 0:
            return

        self.SetHoldings(self.btc_symbol, 0.95)
        self.entry_price = price
        self.stop_loss_price = price * (1 - self.stop_loss_pct)
        self.position_side = "long"
        self.last_trade_time = timestamp
        self.trade_count += 1

    def _check_stop_loss(self, price: float) -> None:
        if price <= self.stop_loss_price:
            self._exit_position(price, "Stop loss hit")

    def _exit_position(self, price: float, reason: str) -> None:
        if self.position_side is None:
            return

        pnl_pct = (price - self.entry_price) / self.entry_price
        if pnl_pct > 0:
            self.winning_trades += 1

        self.Liquidate(self.btc_symbol, reason)

        self.position_side = None
        self.entry_price = 0.0
        self.stop_loss_price = 0.0

    def OnEndOfAlgorithm(self) -> None:
        total_return = (self.Portfolio.TotalPortfolioValue - 100000) / 100000 * 100
        win_rate = (self.winning_trades / self.trade_count) * 100 if self.trade_count > 0 else 0.0

        self.Log(f"Final Results - Return: {total_return:.2f}% | Win Rate: {win_rate:.1f}% | Trades: {self.trade_count}")
 
