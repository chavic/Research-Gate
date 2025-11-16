# region imports
from AlgorithmImports import *
# endregion
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd

from . import utils

DEFAULT_LOG_DIR = Path("data") / "execution" / "raw"
OUTPUT_FILE = Path("data") / "execution" / "execution_metrics.parquet"


def _standardize_frame(df: pd.DataFrame, column_map: Mapping[str, str] | None = None) -> pd.DataFrame:
    rename_map = {
        # timestamp
        "time": "timestamp",
        "fill_time": "timestamp",
        "fillTime": "timestamp",
        "created_time": "timestamp",
        # symbol
        "ticker": "symbol",
        "asset": "symbol",
        # prices
        "fillPrice": "fill_price",
        "price": "fill_price",
        "execution_price": "fill_price",
        "expectedPrice": "expected_price",
        "benchmark_price": "expected_price",
        "limit_price": "expected_price",
        "order_price": "expected_price",
        # latency
        "latency": "latency_ms",
        "latencyMs": "latency_ms",
        "response_time_ms": "latency_ms",
        "order_response_time": "latency_ms",
        # fill rate
        "fillRatio": "fill_rate",
        "fill_ratio": "fill_rate",
    }
    if column_map:
        rename_map.update(column_map)

    df = df.rename(columns=rename_map)

    required = {"timestamp", "symbol", "fill_price"}
    if not required.issubset(df.columns):
        missing = ", ".join(sorted(required - set(df.columns)))
        raise ValueError(f"Execution log missing required columns: {missing}")

    if "expected_price" not in df.columns:
        df["expected_price"] = df["fill_price"]

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp", "fill_price", "expected_price"])

    if "quantity" in df.columns and "filled_quantity" in df.columns and "fill_rate" not in df.columns:
        df["fill_rate"] = (df["filled_quantity"] / df["quantity"]).clip(upper=1).astype(float)

    if "latency_ms" in df.columns:
        df["latency_ms"] = pd.to_numeric(df["latency_ms"], errors="coerce")

    df["fill_price"] = pd.to_numeric(df["fill_price"], errors="coerce")
    df["expected_price"] = pd.to_numeric(df["expected_price"], errors="coerce")
    df = df.set_index("timestamp").sort_index()
    return df


def _compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["slippage_bps"] = ((df["fill_price"] - df["expected_price"]) / df["expected_price"]) * 10_000
    out_cols = ["symbol", "slippage_bps"]

    if "latency_ms" in df.columns:
        out_cols.append("latency_ms")
    if "fill_rate" in df.columns:
        out_cols.append("fill_rate")

    metrics = df[out_cols]
    metrics = metrics[~metrics.index.duplicated(keep="last")]
    return metrics


def run_pipeline(
    log_sources: Iterable[Path] | None = None,
    out_file: Path | None = None,
    overwrite: bool = False,
    column_map: Mapping[str, str] | None = None,
) -> Path | None:
    """
    Aggregate local execution logs into a standardized metrics file.

    Parameters
    ----------
    log_sources : iterable of Path or None
        If provided, iterate over specific files/directories. When None, default to
        `data/execution/raw/` and read all `.csv` / `.parquet` files.
    out_file : Path or None
        Path to the aggregated metrics file (defaults to
        `data/execution/execution_metrics.parquet`).
    overwrite : bool
        If False and the output file already exists, the pipeline skips aggregation.
    column_map : dict
        Optional override for column renaming.
    """

    out_file = out_file or OUTPUT_FILE
    if out_file.exists() and not overwrite:
        return out_file

    if log_sources is None:
        log_sources = []
        if DEFAULT_LOG_DIR.exists():
            log_sources = list(DEFAULT_LOG_DIR.glob("**/*"))
        else:
            raise FileNotFoundError(
                "No log sources provided and default directory data/execution/raw/ does not exist."
            )

    files: list[Path] = []
    for path in log_sources:
        if path.is_dir():
            files.extend(path.glob("**/*.parquet"))
            files.extend(path.glob("**/*.csv"))
        elif path.suffix.lower() in {".csv", ".parquet"}:
            files.append(path)

    if not files:
        raise FileNotFoundError("No execution log files found for aggregation.")

    frames: list[pd.DataFrame] = []
    for file_path in files:
        if file_path.suffix.lower() == ".parquet":
            df = pd.read_parquet(file_path)
        else:
            df = pd.read_csv(file_path)
        try:
            normalized = _standardize_frame(df, column_map=column_map)
        except ValueError:
            continue
        frames.append(normalized)

    if not frames:
        return None

    combined = utils.merge_frames(frames)
    if combined.empty:
        return None

    metrics = _compute_metrics(combined)
    utils.write_time_series(metrics, out_file)
    return out_file

