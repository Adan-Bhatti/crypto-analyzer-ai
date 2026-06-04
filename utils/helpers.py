"""
Shared Utility / Helper Functions
===================================
Common utility functions used across the project for formatting,
timestamp conversions, and data validation helpers.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd


# =============================================================================
# Price & Number Formatting
# =============================================================================

def format_price(value: float) -> str:
    """
    Format a numeric value as a US-dollar price string.

    Args:
        value: The price value to format.

    Returns:
        A string like ``$12,345.67``.
    """
    return f"${value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a decimal ratio or percentage value as a display string.

    Args:
        value: The value to format. Values ≤ 1.0 are treated as ratios
               (multiplied by 100); values > 1.0 are treated as already-percentages.
        decimals: Number of decimal places.

    Returns:
        A string like ``+3.42%`` or ``-1.10%``.
    """
    # If the value looks like a ratio (e.g. 0.03), convert to percentage
    pct = value * 100 if abs(value) <= 1.0 else value
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.{decimals}f}%"


def format_large_number(value: float) -> str:
    """
    Format large numbers with K/M/B suffixes for compact display.

    Args:
        value: The number to format.

    Returns:
        A string like ``1.23B``, ``456.7M``, or ``12.3K``.
    """
    abs_val = abs(value)
    sign = "-" if value < 0 else ""

    if abs_val >= 1_000_000_000:
        return f"{sign}{abs_val / 1_000_000_000:.2f}B"
    elif abs_val >= 1_000_000:
        return f"{sign}{abs_val / 1_000_000:.2f}M"
    elif abs_val >= 1_000:
        return f"{sign}{abs_val / 1_000:.2f}K"
    else:
        return f"{sign}{abs_val:.2f}"


# =============================================================================
# Timestamp Helpers
# =============================================================================

def ms_to_datetime(ms_timestamp: int) -> datetime:
    """
    Convert a millisecond Unix timestamp to a UTC ``datetime`` object.

    Args:
        ms_timestamp: Unix timestamp in milliseconds (Binance format).

    Returns:
        A timezone-aware ``datetime`` in UTC.
    """
    return datetime.fromtimestamp(ms_timestamp / 1000, tz=timezone.utc)


def datetime_to_str(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object as a human-readable string.

    Args:
        dt: The datetime to format.
        fmt: The strftime format string.

    Returns:
        Formatted date string.
    """
    return dt.strftime(fmt)


def get_current_utc() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


# =============================================================================
# Data Validation Helpers
# =============================================================================

def validate_dataframe_columns(
    df: pd.DataFrame,
    required: list[str],
    case_insensitive: bool = True,
) -> bool:
    """
    Check whether a DataFrame contains all required columns.

    Args:
        df: The DataFrame to validate.
        required: List of required column names.
        case_insensitive: If True, compare column names in lowercase.

    Returns:
        True if all required columns are present, False otherwise.
    """
    if case_insensitive:
        existing = {col.lower() for col in df.columns}
        return all(col.lower() in existing for col in required)
    return all(col in df.columns for col in required)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lowercase and strip whitespace from all DataFrame column names.

    Args:
        df: Input DataFrame.

    Returns:
        DataFrame with normalized column names.
    """
    df = df.copy()
    df.columns = [col.strip().lower() for col in df.columns]
    return df


def safe_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely retrieve a value from a dictionary with a default fallback.

    Args:
        data: The dictionary to look up.
        key: The key to retrieve.
        default: Fallback value if the key is missing.

    Returns:
        The value for ``key``, or ``default`` if not found.
    """
    return data.get(key, default)
