# region imports
from AlgorithmImports import *
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from research.scripts.data_loader import DataLoader, DataRequestSpec
from research.scripts.feature_store import FeatureRegistry, FeatureSpec
from research.scripts.signals import SignalModel
from research.scripts.portfolio import FixedFractionAllocator
from research.scripts.risk import RiskGuard
from research.scripts.execution import ImmediatePlanner, ChildOrder


@dataclass
class PositionState:
    entry_price: float = 0.0
    stop_price: float = 0.0
    side: str | None = None


class KrakenMinuteAdapter:
    """Thin wrapper capturing the data request spec we use for BTCUSD."""

    def __init__(self, algorithm: QCAlgorithm, start: datetime, end: datetime) -> None:
        self.algorithm = algorithm
        self.loader = DataLoader()
        self.spec = DataRequestSpec(
            symbol="BTCUSD",
            market=Market.Kraken,
            security_type="Crypto",
            resolution="Minute",
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            fill_forward=True,
            normalization_mode="Raw",
            extended_hours=False,
            additional_params={"comment": "default research adapter"},
        )

    def subscribe(self) -> Symbol:
        self.loader.register(self.spec)
        return self.algorithm.AddCrypto(
            self.spec.symbol,
            Resolution.Minute,
            self.spec.market,
        ).Symbol


class SimpleFeatureEngine:
    """Placeholder feature engine that surfaces the latest close price."""

    def __init__(self) -> None:
        self.registry = FeatureRegistry()
        spec = FeatureSpec(
            name="close_price",
            inputs=("close",),
            window=1,
            description="Latest close price from minute bar",
        )
        self.registry.register(spec, lambda bar: bar.Close)

    def compute(self, bar: TradeBar) -> dict[str, float]:
        return {"close_price": float(bar.Close)}


class RandomLongSignal(SignalModel):
    """Recreates the prior random-entry logic under the SignalModel contract."""

    def __init__(self, probability: float = 0.3, seed: int = 42) -> None:
        self.random = random.Random(seed)
        self.probability = probability

    def score(self, features: dict[str, float]) -> tuple[float, float]:
        edge = 1.0 if self.random.random() < self.probability else 0.0
        confidence = 0.5 if edge > 0 else 0.0
        return edge, confidence


class TrailingStopGuard(RiskGuard):
    """Tracks trailing stops and exposes helper methods for the algorithm."""

    def __init__(self, state: PositionState, stop_loss_pct: float) -> None:
        super().__init__()
        self.state = state
        self.stop_loss_pct = stop_loss_pct

    def register_entry(self, price: float) -> None:
        self.state.entry_price = price
        self.state.stop_price = price * (1 - self.stop_loss_pct)
        self.state.side = "long"

    def update_trailing(self, price: float) -> None:
        if self.state.side == "long":
            trailing = price * (1 - self.stop_loss_pct)
            self.state.stop_price = max(self.state.stop_price, trailing)

    def should_exit(self, price: float) -> bool:
        return self.state.side == "long" and price <= self.state.stop_price

    def reset(self) -> None:
        self.state.entry_price = 0.0
        self.state.stop_price = 0.0
        self.state.side = None

    def evaluate(self, targets: dict[str, float], context: dict[str, float]) -> dict[str, float]:
        price = context.get("price")
        if price is not None:
            self.update_trailing(price)
        return super().evaluate(targets, context)
# endregion

class SleepySkyBlueAlligator(QCAlgorithm):
    """Randomised long-only BTC strategy with a trailing stop mechanism."""

    def Initialize(self) -> None:
        self.SetStartDate(2024, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100000)

        self.position_state = PositionState()
        self.stop_loss_pct = 0.03
        self.min_trade_interval = timedelta(minutes=5)
        self.last_trade_time = self.StartDate

        self.market_adapter = KrakenMinuteAdapter(self, self.StartDate, self.EndDate)
        self.btc_symbol = self.market_adapter.subscribe()

        self.feature_engine = SimpleFeatureEngine()
        self.signal_model = RandomLongSignal(probability=0.3, seed=42)
        self.allocator = FixedFractionAllocator(fraction=0.95)
        self.risk_guard = TrailingStopGuard(self.position_state, self.stop_loss_pct)
        self.execution_planner = ImmediatePlanner()

        self.trade_count = 0
        self.winning_trades = 0

    def OnData(self, data: Slice) -> None:
        if self.IsWarmingUp:
            return

        if self.btc_symbol not in data or data[self.btc_symbol] is None:
            return

        bar = data[self.btc_symbol]
        price = float(bar.Close)

        self.risk_guard.update_trailing(price)

        if self.risk_guard.should_exit(price):
            self._exit_position(price, "Stop loss hit")
            return

        if self.position_state.side is not None:
            return

        if not self._can_trade():
            return

        features = self.feature_engine.compute(bar)
        score, _ = self.signal_model.score(features)
        if score <= 0:
            return

        scores = {str(self.btc_symbol): score}
        context = {"price": price}
        allocation = self.allocator.compute(scores, context)
        safe_targets = self.risk_guard.evaluate(allocation.weights, context)
        if not safe_targets:
            return

        orders = self.execution_planner.plan(safe_targets, {"timestamp": self.Time.isoformat()})
        self._route_orders(orders, price)

    def _exit_position(self, price: float, reason: str) -> None:
        if self.position_state.side is None:
            return

        pnl_pct = (price - self.position_state.entry_price) / self.position_state.entry_price
        if pnl_pct > 0:
            self.winning_trades += 1

        self.Liquidate(self.btc_symbol, reason)

        self.risk_guard.reset()

    def OnEndOfAlgorithm(self) -> None:
        total_return = (self.Portfolio.TotalPortfolioValue - 100000) / 100000 * 100
        win_rate = (self.winning_trades / self.trade_count) * 100 if self.trade_count > 0 else 0.0

        self.Log(f"Final Results - Return: {total_return:.2f}% | Win Rate: {win_rate:.1f}% | Trades: {self.trade_count}")

    def _route_orders(self, orders: list[ChildOrder], price: float) -> None:
        for order in orders:
            if order.symbol != str(self.btc_symbol):
                continue

            if self.Portfolio.Cash <= 0:
                return

            self.SetHoldings(self.btc_symbol, order.quantity)
            self.risk_guard.register_entry(price)
            self.last_trade_time = self.Time
            self.trade_count += 1
            return

    def _can_trade(self) -> bool:
        return self.Time - self.last_trade_time >= self.min_trade_interval
 
