"""
Data Loader Module
====================
Handles loading OHLCV cryptocurrency data from three sources:
  1. Local CSV files (user upload or sample dataset).
  2. Binance public REST API (primary live source).
  3. Yahoo Finance via ``yfinance`` (fallback).

Includes automatic fallback logic and minimum-row validation.
"""
from __future__ import annotations

import pandas as pd

from utils.config import (
    MIN_DATA_ROWS,
    REQUIRED_COLUMNS,
    YAHOO_MAX_PERIOD,
    YAHOO_TICKERS,
)
from utils.helpers import normalize_column_names
from utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Custom Exceptions
# =============================================================================

class InsufficientDataError(Exception):
    """Raised when the loaded dataset has fewer rows than ``MIN_DATA_ROWS``."""
    pass


class DataLoadError(Exception):
    """Raised when all data-loading strategies fail."""
    pass


# =============================================================================
# DataLoader Class
# =============================================================================

class DataLoader:
    """
    Unified data loader supporting CSV files, Binance API, and Yahoo Finance.

    Usage::

        loader = DataLoader()
        df = loader.load_csv("data/sample/btc_sample.csv")
        df = loader.load_with_fallback("BTCUSDT")
    """

    # -----------------------------------------------------------------
    # CSV Loading
    # -----------------------------------------------------------------

    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        Load OHLCV data from a local CSV file.

        Args:
            filepath: Path to the CSV file.

        Returns:
            Cleaned DataFrame sorted ascending by date.

        Raises:
            FileNotFoundError: If the file does not exist.
            InsufficientDataError: If the dataset has fewer than ``MIN_DATA_ROWS`` rows.
            ValueError: If required OHLCV columns are missing.
        """
        logger.info("Loading CSV from: %s", filepath)

        try:
            df = pd.read_csv(filepath)
        except FileNotFoundError:
            logger.error("CSV file not found: %s", filepath)
            raise

        # Normalize column names to lowercase
        df = normalize_column_names(df)

        # Validate required columns exist
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            # Try common alternative names
            col_map = self._detect_column_mapping(df)
            if col_map:
                df = df.rename(columns=col_map)
                logger.info("Mapped CSV columns: %s", col_map)
            else:
                raise ValueError(
                    f"CSV is missing required columns: {missing}. "
                    f"Expected: {REQUIRED_COLUMNS}"
                )

        # Parse dates and sort ascending
        df = self._parse_and_sort_dates(df)

        # Validate minimum row count
        self._validate_row_count(df)

        logger.info("CSV loaded successfully — %d rows", len(df))
        return df

    # -----------------------------------------------------------------
    # Binance API Loading
    # -----------------------------------------------------------------

    def load_from_binance(
        self,
        symbol: str,
        interval: str = "1d",
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV candlestick data from the Binance public REST API.

        Args:
            symbol: Trading pair symbol (e.g., ``"BTCUSDT"``).
            interval: Candlestick interval (e.g., ``"1d"``, ``"1h"``).
            limit: Number of candles to fetch (max 1000).

        Returns:
            DataFrame with columns: date, open, high, low, close, volume.

        Raises:
            DataLoadError: If the Binance API request fails.
        """
        # Lazy import to avoid circular dependency at module level
        from services.binance_service import BinanceService

        logger.info("Loading from Binance: %s (%s, limit=%d)", symbol, interval, limit)

        try:
            service = BinanceService()
            df = service.get_klines(symbol=symbol, interval=interval, limit=limit)
            self._validate_row_count(df)
            logger.info("Binance data loaded — %d rows", len(df))
            return df
        except Exception as exc:
            logger.warning("Binance API failed for %s: %s", symbol, exc)
            raise DataLoadError(f"Binance API error: {exc}") from exc

    def load_max_history(
        self,
        ticker: str,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetch the maximum available historical OHLCV data from Yahoo Finance.

        Uses ``period="max"`` to retrieve every available daily candle
        (BTC goes back to 2014-09-17 — over 4,000 candles).

        Args:
            ticker: Yahoo Finance ticker (e.g., ``"BTC-USD"``).
            interval: Data interval (default ``"1d"`` for daily).

        Returns:
            DataFrame with columns: date, open, high, low, close, volume.

        Raises:
            DataLoadError: If yfinance returns empty data.
        """
        from services.yahoo_service import YahooFinanceService

        logger.info("Loading MAX history from Yahoo Finance: %s (%s)", ticker, interval)

        try:
            service = YahooFinanceService()
            df = service.get_historical(
                symbol=ticker,
                period=YAHOO_MAX_PERIOD,
                interval=interval,
            )
            self._validate_row_count(df)
            logger.info(
                "Yahoo Finance MAX history loaded — %d rows (%.1f years)",
                len(df),
                len(df) / 365.0,
            )
            return df
        except Exception as exc:
            logger.warning("Yahoo Finance MAX failed for %s: %s", ticker, exc)
            raise DataLoadError(f"Yahoo Finance MAX error: {exc}") from exc

    # -----------------------------------------------------------------
    # Yahoo Finance Loading
    # -----------------------------------------------------------------

    def load_from_yahoo(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data from Yahoo Finance via ``yfinance``.

        Args:
            ticker: Yahoo Finance ticker (e.g., ``"BTC-USD"``).
            period: Data period (e.g., ``"1y"``, ``"2y"``, ``"max"``).
            interval: Data interval (e.g., ``"1d"``, ``"1h"``).

        Returns:
            DataFrame with columns: date, open, high, low, close, volume.

        Raises:
            DataLoadError: If yfinance returns empty data.
        """
        from services.yahoo_service import YahooFinanceService

        logger.info("Loading from Yahoo Finance: %s (%s, %s)", ticker, period, interval)

        try:
            service = YahooFinanceService()
            df = service.get_historical(symbol=ticker, period=period, interval=interval)
            self._validate_row_count(df)
            logger.info("Yahoo Finance data loaded — %d rows", len(df))
            return df
        except Exception as exc:
            logger.warning("Yahoo Finance failed for %s: %s", ticker, exc)
            raise DataLoadError(f"Yahoo Finance error: {exc}") from exc

    # -----------------------------------------------------------------
    # Fallback Loading (Binance → Yahoo)
    # -----------------------------------------------------------------

    def load_with_fallback(self, symbol: str) -> pd.DataFrame:
        """
        Load maximum historical data for a symbol.

        Strategy:
          1. Yahoo Finance ``period="max"`` — full history (up to 10+ years)
          2. Binance API ``limit=1000`` — most recent 1000 candles (fallback)

        Args:
            symbol: Binance trading pair symbol (e.g., ``"BTCUSDT"``).

        Returns:
            DataFrame with OHLCV data from whichever source gives the most data.

        Raises:
            DataLoadError: If all sources fail.
        """
        # Try Yahoo Finance first — gives maximum history
        yahoo_ticker = YAHOO_TICKERS.get(symbol)
        if yahoo_ticker:
            try:
                return self.load_max_history(yahoo_ticker)
            except (DataLoadError, Exception) as yahoo_err:
                logger.warning(
                    "Yahoo Finance MAX failed for %s, falling back to Binance. Error: %s",
                    symbol, yahoo_err,
                )

        # Fallback to Binance with max limit
        try:
            return self.load_from_binance(symbol, limit=1000)
        except (DataLoadError, Exception) as binance_err:
            raise DataLoadError(
                f"All data sources failed for {symbol}. "
                f"Last error: {binance_err}. "
                "Check your internet connection or provide a CSV file."
            ) from binance_err

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _parse_and_sort_dates(df: pd.DataFrame) -> pd.DataFrame:
        """Parse the 'date' column to datetime and sort ascending."""
        # Handle various date column names
        date_col = "date"
        if date_col not in df.columns:
            # Check for timestamp alternative
            for alt in ["timestamp", "datetime", "time"]:
                if alt in df.columns:
                    df = df.rename(columns={alt: "date"})
                    break

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
            df = df.sort_values("date", ascending=True).reset_index(drop=True)

        return df

    @staticmethod
    def _detect_column_mapping(df: pd.DataFrame) -> dict[str, str] | None:
        """
        Attempt to map non-standard column names to expected OHLCV format.

        Returns:
            A column-rename dictionary, or None if mapping fails.
        """
        cols_lower = {c.lower(): c for c in df.columns}
        mapping: dict[str, str] = {}

        # Common alternative column names
        alternatives = {
            "date": ["timestamp", "datetime", "time", "date/time"],
            "open": ["open_price", "opening"],
            "high": ["high_price", "highest"],
            "low": ["low_price", "lowest"],
            "close": ["close_price", "closing", "adj close"],
            "volume": ["vol", "volume_traded"],
        }

        for target, alts in alternatives.items():
            if target in cols_lower:
                # Column already exists (case-insensitive)
                if cols_lower[target] != target:
                    mapping[cols_lower[target]] = target
            else:
                for alt in alts:
                    if alt in cols_lower:
                        mapping[cols_lower[alt]] = target
                        break

        # Only return mapping if we can cover all required columns
        current_cols = set(df.columns) | set(mapping.values())
        current_cols_lower = {c.lower() for c in current_cols}
        if all(req in current_cols_lower for req in REQUIRED_COLUMNS):
            return mapping if mapping else None

        return None

    @staticmethod
    def _validate_row_count(df: pd.DataFrame) -> None:
        """Raise ``InsufficientDataError`` if the DataFrame is too small."""
        if len(df) < MIN_DATA_ROWS:
            raise InsufficientDataError(
                f"Dataset has only {len(df)} rows, "
                f"minimum required is {MIN_DATA_ROWS}."
            )
