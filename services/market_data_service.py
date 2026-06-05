"""
Unified Market Data Service
=============================
Provides a single interface for fetching cryptocurrency market data.
Tries Binance first and automatically falls back to Yahoo Finance
on any error, logging which source was used.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from services.binance_service import BinanceService
from services.yahoo_service import YahooFinanceService
from utils.config import YAHOO_TICKERS
from utils.logger import get_logger

logger = get_logger(__name__)


class MarketDataService:
    """
    Unified data access interface.

    Tries Binance first, falls back to Yahoo Finance on any error.
    Tracks which data source was used via ``self.source_used``.

    Usage::

        mds = MarketDataService()
        df = mds.get_data("BTCUSDT")
        print(mds.source_used)  # "Binance" or "Yahoo Finance"
    """

    def __init__(self) -> None:
        """Initialize both service backends."""
        self.binance = BinanceService()
        self.yahoo = YahooFinanceService()
        self.source_used: str = ""

    # -----------------------------------------------------------------
    # Unified Data Fetch
    # -----------------------------------------------------------------

    def get_data(
        self,
        symbol: str,
        interval: str = "1d",
        limit: int = 500,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data, trying Binance first with Yahoo Finance fallback.

        Args:
            symbol: Binance-style symbol (e.g., ``"BTCUSDT"``).
            interval: Candlestick interval (e.g., ``"1d"``).
            limit: Number of candles to fetch.

        Returns:
            DataFrame with columns: ``date``, ``open``, ``high``,
            ``low``, ``close``, ``volume``.

        Raises:
            RuntimeError: If both data sources fail.
        """
        # --- Attempt Binance ---
        try:
            logger.info("Attempting Binance for %s...", symbol)
            df = self.binance.get_klines(
                symbol=symbol, interval=interval, limit=limit
            )
            self.source_used = "Binance"
            logger.info("Successfully fetched data from Binance (%d rows)", len(df))
            return df

        except Exception as binance_err:
            logger.warning(
                "Binance failed for %s: %s. Falling back to Yahoo Finance.",
                symbol, binance_err,
            )

        # --- Attempt Yahoo Finance ---
        try:
            yahoo_ticker = YAHOO_TICKERS.get(symbol, symbol)
            # Map Binance intervals to Yahoo-compatible periods/intervals
            period = self._limit_to_period(limit, interval)
            yahoo_interval = self._map_interval(interval)

            logger.info(
                "Attempting Yahoo Finance for %s (ticker=%s, period=%s)...",
                symbol, yahoo_ticker, period,
            )
            df = self.yahoo.get_historical(
                symbol=yahoo_ticker, period=period, interval=yahoo_interval
            )
            
            # Yahoo returns data based on predefined periods (e.g. 1mo). 
            # We must truncate it down to the exact requested limit.
            if len(df) > limit:
                df = df.iloc[-limit:].reset_index(drop=True)
                
            self.source_used = "Yahoo Finance"
            logger.info(
                "Successfully fetched data from Yahoo Finance (%d rows)", len(df)
            )
            return df

        except Exception as yahoo_err:
            logger.error(
                "Yahoo Finance also failed for %s: %s", symbol, yahoo_err
            )
            raise RuntimeError(
                f"All data sources failed for {symbol}. "
                f"Binance error: {binance_err}. Yahoo error: {yahoo_err}. "  # noqa: F821
                f"Please check your internet connection or provide a CSV file."
            )

    # -----------------------------------------------------------------
    # Live Price
    # -----------------------------------------------------------------

    def get_live_price(self, symbol: str) -> dict:
        """
        Get the current live price from the first available source.

        Args:
            symbol: Binance-style symbol (e.g., ``"BTCUSDT"``).

        Returns:
            Dictionary with keys: ``price``, ``source``, ``timestamp``.
        """
        # Try Binance first
        try:
            price = self.binance.get_ticker_price(symbol)
            return {
                "price": price,
                "source": "Binance",
                "timestamp": datetime.now(tz=timezone.utc),
            }
        except Exception as exc:
            logger.warning("Binance live price failed: %s", exc)

        # Fallback to Yahoo Finance
        try:
            yahoo_ticker = YAHOO_TICKERS.get(symbol, symbol)
            price = self.yahoo.get_live_price(yahoo_ticker)
            return {
                "price": price,
                "source": "Yahoo Finance",
                "timestamp": datetime.now(tz=timezone.utc),
            }
        except Exception as exc:
            logger.error("All live price sources failed for %s: %s", symbol, exc)
            return {
                "price": 0.0,
                "source": "Unavailable",
                "timestamp": datetime.now(tz=timezone.utc),
            }

    # -----------------------------------------------------------------
    # 24-Hour Stats (Binance-only, graceful fallback)
    # -----------------------------------------------------------------

    def get_24hr_stats(self, symbol: str) -> dict:
        """
        Get 24-hour market statistics. Tries Binance, falls back to Yahoo Finance.

        Args:
            symbol: Binance-style symbol.

        Returns:
            Dictionary with 24hr stats, or empty values on failure.
        """
        try:
            return self.binance.get_24hr_stats(symbol)
        except Exception as exc:
            logger.warning("Binance 24hr stats unavailable for %s: %s. Falling back to Yahoo.", symbol, exc)
            
            try:
                # Use Yahoo Finance historical data to calculate 24-hour stats
                yahoo_ticker = YAHOO_TICKERS.get(symbol, symbol)
                df = self.yahoo.get_historical(yahoo_ticker, period="5d", interval="1d")
                
                if len(df) >= 2:
                    current_day = df.iloc[-1]
                    prev_day = df.iloc[-2]
                    
                    last_price = float(current_day["close"])
                    prev_close = float(prev_day["close"])
                    price_change = last_price - prev_close
                    price_change_pct = (price_change / prev_close * 100) if prev_close != 0 else 0.0
                    
                    return {
                        "price_change": price_change,
                        "price_change_pct": price_change_pct,
                        "high": float(current_day["high"]),
                        "low": float(current_day["low"]),
                        "volume": float(current_day["volume"]),
                        "last_price": last_price,
                        "open_price": float(current_day["open"]),
                        "timestamp": datetime.now(tz=timezone.utc),
                    }
            except Exception as yahoo_exc:
                logger.error("Yahoo Finance 24hr stats also failed for %s: %s", symbol, yahoo_exc)

            # Ultimate fallback if both APIs fail
            return {
                "price_change": 0.0,
                "price_change_pct": 0.0,
                "high": 0.0,
                "low": 0.0,
                "volume": 0.0,
                "last_price": 0.0,
                "open_price": 0.0,
                "timestamp": datetime.now(tz=timezone.utc),
            }

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _limit_to_period(limit: int, interval: str) -> str:
        """
        Convert a Binance-style limit+interval into a Yahoo Finance period string.

        Args:
            limit: Number of candles.
            interval: Binance interval string.

        Returns:
            Yahoo Finance period string (e.g., ``"1y"``, ``"2y"``).
        """
        # Approximate the time span in days
        interval_days = {
            "1m": 1 / 1440,
            "5m": 5 / 1440,
            "15m": 15 / 1440,
            "1h": 1 / 24,
            "4h": 4 / 24,
            "1d": 1,
            "1w": 7,
        }
        days_per_candle = interval_days.get(interval, 1)
        total_days = limit * days_per_candle

        if total_days <= 30:
            return "1mo"
        elif total_days <= 90:
            return "3mo"
        elif total_days <= 180:
            return "6mo"
        elif total_days <= 365:
            return "1y"
        elif total_days <= 730:
            return "2y"
        else:
            return "5y"

    @staticmethod
    def _map_interval(binance_interval: str) -> str:
        """
        Map a Binance interval string to a Yahoo Finance-compatible interval.

        Args:
            binance_interval: Binance interval (e.g., ``"1d"``, ``"1h"``).

        Returns:
            Yahoo Finance interval string.
        """
        mapping = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "4h": "1h",   # Yahoo doesn't support 4h; use 1h
            "1d": "1d",
            "1w": "1wk",
        }
        return mapping.get(binance_interval, "1d")
