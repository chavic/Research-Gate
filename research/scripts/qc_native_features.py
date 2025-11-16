from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
import pandas as pd


@dataclass
class PriceWindow:
    symbol: str
    closes: pd.Series
    volumes: pd.Series | None = None


def multi_horizon_roc(price: pd.Series, windows: Sequence[int]) -> pd.DataFrame:
    frame = {}
    for window in windows:
        frame[f"roc_{window}h"] = price.pct_change(window)
    return pd.DataFrame(frame)


def atr_percent(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 24) -> pd.Series:
    true_range = pd.concat(
        [
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = true_range.rolling(window).mean()
    return (atr / close).rename("atr_percent")


def realized_vol(returns: pd.Series, window: int, annualize: bool = False) -> pd.Series:
    vol = returns.rolling(window).std()
    if annualize:
        vol = vol * np.sqrt(window)
    return vol.rename(f"realized_vol_{window}")


def normalized_momentum(price: pd.Series, window: int, vol_window: int) -> pd.Series:
    momentum = price.pct_change(window)
    vol = realized_vol(momentum, vol_window)
    factor = momentum / vol.replace(0, np.nan)
    return factor.rename(f"normalized_mom_{window}_{vol_window}")


def liquidity_metrics(price: pd.Series, volume: pd.Series, lookback: int = 10) -> pd.Series:
    dollar_vol = price * volume
    med_dv = dollar_vol.rolling(lookback).median()
    price_range = price.rolling(lookback).apply(lambda s: (s.max() - s.min()) / s.mean() if s.mean() else np.nan)
    score = med_dv / price_range.replace(0, np.nan)
    return score.rename(f"liquidity_score_{lookback}")


def cross_asset_beta(
    target_returns: pd.Series,
    factor_returns: Mapping[str, pd.Series],
    window: int = 168,
) -> pd.DataFrame:
    aligned = pd.concat([target_returns] + list(factor_returns.values()), axis=1, join="inner").dropna()
    aligned.columns = ["target"] + list(factor_returns.keys())

    betas = []
    residuals = []
    for end in range(window, len(aligned) + 1):
        sub = aligned.iloc[end - window : end]
        X = sub.iloc[:, 1:]
        y = sub.iloc[:, 0]
        coef, *_ = np.linalg.lstsq(X.values, y.values, rcond=None)
        betas.append(pd.Series(coef, index=X.columns, name=sub.index[-1]))
        residuals.append((y - X.dot(coef))[-1])

    betas_df = pd.DataFrame(betas)
    residual_series = pd.Series(residuals, index=betas_df.index, name="beta_residual")
    return pd.concat([betas_df, residual_series], axis=1)


def regime_flags(
    btc_returns: pd.Series,
    macro_series: Mapping[str, pd.Series],
    windows: Sequence[int] = (24, 168),
) -> pd.DataFrame:
    features = {}
    for name, series in macro_series.items():
        aligned = pd.concat([btc_returns, series], axis=1, join="inner").dropna()
        ratio = aligned.iloc[:, 0] / aligned.iloc[:, 1].replace(0, np.nan)
        for window in windows:
            features[f"{name}_ratio_{window}h"] = ratio.rolling(window).mean()
    return pd.DataFrame(features)


__all__ = [
    "PriceWindow",
    "multi_horizon_roc",
    "atr_percent",
    "realized_vol",
    "normalized_momentum",
    "liquidity_metrics",
    "cross_asset_beta",
    "regime_flags",
]
