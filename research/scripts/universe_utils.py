from __future__ import annotations

from typing import List

import requests


COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"


def fetch_top_marketcap_pairs(limit: int = 50, vs_currency: str = "usd") -> List[str]:
    """
    Retrieve the top crypto symbols by market cap from CoinGecko and convert them to QC USD pairs.

    Parameters
    ----------
    limit : int
        Number of assets to request (max 250 per API call).
    vs_currency : str
        Fiat currency for market cap ranking (default 'usd').
    """

    per_page = 250
    remaining = max(limit, 0)
    page = 1
    tickers: list[str] = []

    while remaining > 0:
        page_size = min(per_page, remaining)
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": page_size,
            "page": page,
            "price_change_percentage": "24h",
        }
        response = requests.get(COINGECKO_MARKETS_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data:
            break

        for entry in data:
            symbol = entry.get("symbol", "")
            if not symbol:
                continue
            pair = f"{symbol.upper()}USD"
            tickers.append(pair)

        if len(data) < page_size:
            break
        remaining -= len(data)
        page += 1

    # Preserve ordering, remove duplicates
    seen = set()
    unique_pairs: list[str] = []
    for pair in tickers:
        if pair not in seen:
            seen.add(pair)
            unique_pairs.append(pair)
    return unique_pairs[:limit]


__all__ = ["fetch_top_marketcap_pairs"]
