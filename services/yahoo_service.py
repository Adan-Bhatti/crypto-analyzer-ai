"""
Yahoo Finance Service Module
==============================
Fallback data source using the ``yfinance`` library when Binance
is unavailable. Provides historical OHLCV data and live prices.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

from utils.config import YAHOO_TICKERS
from utils.logger import get_logger

logger = get_logger(__name__)


class YahooFinanceService:
    """
    Fallback data source using yfinance.

    Cryptocurrency tickers use the ``-USD`` suffix (e.g., ``BTC-USD``).

    Usage::

        service = YahooFinanceService()
        df = service.get_historical("BTC-USD", period="1y")
        price = service.get_live_price("BTC-USD")
    """

    CRYPTO_SUFFIX: str = "-USD"

    # -----------------------------------------------------------------
    # Historical OHLCV Data
    # -----------------------------------------------------------------

    def get_historical(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data from Yahoo Finance.

        Args:
            symbol: Yahoo Finance ticker (e.g., ``"BTC-USD"``) or Binance-style
                    symbol (e.g., ``"BTCUSDT"`` — will be auto-mapped).
            period: Data period. Supported values: ``"1mo"``, ``"3mo"``,
                    ``"6mo"``, ``"1y"``, ``"2y"``, ``"5y"``, ``"max"``.
            interval: Data interval. Supported: ``"1d"``, ``"1h"``, ``"1wk"``.

        Returns:
            DataFrame with columns: ``date``, ``open``, ``high``,
            ``low``, ``close``, ``volume``.

        Raises:
            ValueError: If the symbol cannot be resolved or data is empty.
        """
        # Auto-map Binance symbol to Yahoo ticker if needed
        yahoo_ticker = self._resolve_ticker(symbol)

        logger.info(
            "Fetching Yahoo Finance data: %s (period=%s, interval=%s)",
            yahoo_ticker, period, interval,
        )

        try:
            ticker = yf.Ticker(yahoo_ticker)
            df = ticker.history(period=period, interval=interval)
        except Exception as exc:
            logger.error("yfinance download failed for %s: %s", yahoo_ticker, exc)
            raise ValueError(f"Yahoo Finance data fetch failed: {exc}") from exc

        if df.empty:
            raise ValueError(f"No data returned from Yahoo Finance for {yahoo_ticker}")

        # Normalize the DataFrame to match our standard format
        df = self._normalize_yahoo_df(df)

        logger.info("Yahoo Finance: fetched %d rows for %s", len(df), yahoo_ticker)
        return df

    # -----------------------------------------------------------------
    # Live Price
    # -----------------------------------------------------------------

    def get_live_price(self, symbol: str) -> float:
        """
        Get the current market price from Yahoo Finance.

        Args:
            symbol: Yahoo Finance ticker or Binance-style symbol.

        Returns:
            Current price as a float.

        Raises:
            ValueError: If the price cannot be fetched.
        """
        yahoo_ticker = self._resolve_ticker(symbol)

        try:
            ticker = yf.Ticker(yahoo_ticker)
            # Use fast_info for quicker access
            price = ticker.fast_info.get("lastPrice", None)
            if price is None:
                # Fallback: use the last Close from history
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
                else:
                    raise ValueError("Unable to fetch live price")

            price = float(price)
            logger.info("Yahoo live price for %s: %.2f", yahoo_ticker, price)
            return price
        except Exception as exc:
            logger.error("Failed to get live price for %s: %s", yahoo_ticker, exc)
            raise ValueError(f"Yahoo Finance live price failed: {exc}") from exc

    # -----------------------------------------------------------------
    # Coin Info
    # -----------------------------------------------------------------

    def get_info(self, symbol: str) -> dict:
        """
        Get metadata / summary information for a cryptocurrency.

        Args:
            symbol: Yahoo Finance ticker or Binance-style symbol.

        Returns:
            Dictionary with available info fields (name, market cap, etc.).
        """
        yahoo_ticker = self._resolve_ticker(symbol)

        try:
            ticker = yf.Ticker(yahoo_ticker)
            info = ticker.info or {}
            logger.info("Fetched info for %s (%d fields)", yahoo_ticker, len(info))
            return info
        except Exception as exc:
            logger.warning("Failed to fetch info for %s: %s", yahoo_ticker, exc)
            return {}

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _resolve_ticker(symbol: str) -> str:
        """
        Convert a Binance-style symbol to a Yahoo Finance ticker.

        If the symbol is already in Yahoo format (contains '-'), return as-is.

        Args:
            symbol: Symbol string (e.g., ``"BTCUSDT"`` or ``"BTC-USD"``).

        Returns:
            Yahoo Finance ticker string.
        """
        # Already a Yahoo ticker
        if "-" in symbol:
            return symbol

        # Look up in the mapping
        if symbol in YAHOO_TICKERS:
            return YAHOO_TICKERS[symbol]

        # Attempt to strip USDT suffix and add -USD
        if symbol.endswith("USDT"):
            base = symbol.replace("USDT", "")
            return f"{base}-USD"

        return symbol

    @staticmethod
    def _normalize_yahoo_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize a yfinance DataFrame to the standard OHLCV format.

        Yahoo Finance returns a DataFrame with the date as the index
        and columns ``Open, High, Low, Close, Volume``. This converts
        it to our lowercase-column, date-as-column format.

        Args:
            df: Raw yfinance DataFrame.

        Returns:
            Normalized DataFrame.
        """
        df = df.reset_index()

        # Rename columns to lowercase standard
        column_map = {
            "Date": "date",
            "Datetime": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }

        df = df.rename(columns=column_map)

        # Keep only the columns we need
        keep_cols = ["date", "open", "high", "low", "close", "volume"]
        available = [c for c in keep_cols if c in df.columns]
        df = df[available]

        # Ensure date column is datetime with UTC
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
            df = df.sort_values("date", ascending=True).reset_index(drop=True)

        return df
