"""
Exchange cost modeling helpers.

Provides tiered maker/taker fee schedules for Kraken and Binance spot venues, based on
the latest public schedules (30-day USD volume tiers).
"""

from dataclasses import dataclass
from typing import Sequence

from AlgorithmImports import FeeModel, OrderFee, CashAmount


@dataclass(frozen=True)
class FeeTier:
    volume_threshold: float  # USD 30-day volume
    maker_bps: float
    taker_bps: float


KRAKEN_SPOT_SCHEDULE: Sequence[FeeTier] = (
    FeeTier(50_000, 16, 26),
    FeeTier(100_000, 14, 24),
    FeeTier(250_000, 12, 22),
    FeeTier(500_000, 10, 20),
    FeeTier(1_000_000, 6, 16),
    FeeTier(2_500_000, 4, 14),
    FeeTier(5_000_000, 2, 12),
    FeeTier(10_000_000, 0, 10),
    FeeTier(float("inf"), -2, 8),
)


BINANCE_SPOT_SCHEDULE: Sequence[FeeTier] = (
    FeeTier(1_000_000, 10, 10),
    FeeTier(5_000_000, 9, 10),
    FeeTier(20_000_000, 8, 10),
    FeeTier(100_000_000, 7, 9),
    FeeTier(150_000_000, 6, 9),
    FeeTier(250_000_000, 5, 9),
    FeeTier(500_000_000, 4, 8),
    FeeTier(750_000_000, 3, 8),
    FeeTier(float("inf"), 2, 4),
)


class TieredCryptoFeeModel(FeeModel):
    """Tiered maker/taker crypto fee model for major centralized exchanges."""

    def __init__(
        self,
        venue: str,
        trailing_30d_volume: float = 0.0,
        assume_maker: bool = False,
    ) -> None:
        super().__init__()
        self.venue = venue.lower()
        self.volume = trailing_30d_volume
        self.assume_maker = assume_maker

    def get_schedule(self) -> Sequence[FeeTier]:
        if self.venue == "kraken":
            return KRAKEN_SPOT_SCHEDULE
        if self.venue == "binance":
            return BINANCE_SPOT_SCHEDULE
        raise ValueError(f"Unsupported venue for tiered fees: {self.venue}")

    def _select_rate(self) -> float:
        schedule = self.get_schedule()
        for tier in schedule:
            if self.volume <= tier.volume_threshold:
                bps = tier.maker_bps if self.assume_maker else tier.taker_bps
                return bps / 10_000
        return schedule[-1].taker_bps / 10_000

    def GetOrderFee(self, parameters) -> OrderFee:
        rate = self._select_rate()
        price = parameters.Security.Price
        quantity = parameters.Order.AbsoluteQuantity
        fee = price * quantity * rate
        currency = parameters.Security.QuoteCurrency.Symbol
        return OrderFee(CashAmount(fee, currency))
