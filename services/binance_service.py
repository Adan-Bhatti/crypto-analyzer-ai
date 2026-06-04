"""
Binance Service Module
=======================
Fetches OHLCV candlestick data and market information from
the Binance public REST API (no API key required).

Includes exponential backoff retry logic for rate-limit handling.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

import pandas as pd
import requests

from utils.config import (
    BACKOFF_FACTOR,
    BINANCE_BASE_URL,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
)
from utils.helpers import ms_to_datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class BinanceService:
    """
    Fetches OHLCV candlestick data from Binance public REST API.

    All endpoints used are public and do not require authentication.

    Usage::

        service = BinanceService()
        df = service.get_klines("BTCUSDT", interval="1d", limit=500)
        price = service.get_ticker_price("BTCUSDT")
    """

    BASE_URL: str = BINANCE_BASE_URL

    # -----------------------------------------------------------------
    # Klines (Candlestick) Data
    # -----------------------------------------------------------------

    def get_klines(
        self,
        symbol: str,
        interval: str = "1d",
        limit: int = 500,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV candlestick data from Binance.

        Args:
            symbol: Trading pair symbol (e.g., ``"BTCUSDT"``).
            interval: Candlestick interval. Supported values:
                      ``1m``, ``5m``, ``15m``, ``1h``, ``4h``, ``1d``, ``1w``.
            limit: Number of candles to fetch (max 1000).

        Returns:
            DataFrame with columns: ``date``, ``open``, ``high``,
            ``low``, ``close``, ``volume``.

        Raises:
            requests.exceptions.RequestException: On API failure after retries.
        """
        url = f"{self.BASE_URL}/klines"
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": min(limit, 1000),  # Binance max is 1000
        }

        logger.info("Fetching klines: %s %s (limit=%d)", symbol, interval, limit)

        data = self._request_with_retry(url, params)

        # Parse the Binance klines response format
        # Each entry: [open_time, open, high, low, close, volume, close_time, ...]
        rows = []
        for candle in data:
            rows.append({
                "date": ms_to_datetime(int(candle[0])),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
            })

        df = pd.DataFrame(rows)
        df = df.sort_values("date", ascending=True).reset_index(drop=True)

        logger.info("Fetched %d candles from Binance", len(df))
        return df

    # -----------------------------------------------------------------
    # Ticker Price
    # -----------------------------------------------------------------

    def get_ticker_price(self, symbol: str) -> float:
        """
        Get the current market price for a symbol.

        Args:
            symbol: Trading pair symbol (e.g., ``"BTCUSDT"``).

        Returns:
            Current price as a float.

        Raises:
            requests.exceptions.RequestException: On API failure.
        """
        url = f"{self.BASE_URL}/ticker/price"
        params = {"symbol": symbol.upper()}

        data = self._request_with_retry(url, params)
        price = float(data["price"])

        logger.info("Current price for %s: %.2f", symbol, price)
        return price

    # -----------------------------------------------------------------
    # 24-Hour Statistics
    # -----------------------------------------------------------------

    def get_24hr_stats(self, symbol: str) -> dict:
        """
        Get 24-hour rolling statistics for a symbol.

        Args:
            symbol: Trading pair symbol (e.g., ``"BTCUSDT"``).

        Returns:
            Dictionary with keys: ``price_change``, ``price_change_pct``,
            ``high``, ``low``, ``volume``, ``last_price``, ``open_price``.
        """
        url = f"{self.BASE_URL}/ticker/24hr"
        params = {"symbol": symbol.upper()}

        data = self._request_with_retry(url, params)

        stats = {
            "price_change": float(data.get("priceChange", 0)),
            "price_change_pct": float(data.get("priceChangePercent", 0)),
            "high": float(data.get("highPrice", 0)),
            "low": float(data.get("lowPrice", 0)),
            "volume": float(data.get("volume", 0)),
            "last_price": float(data.get("lastPrice", 0)),
            "open_price": float(data.get("openPrice", 0)),
            "timestamp": datetime.now(tz=timezone.utc),
        }

        logger.info("24hr stats for %s: change=%.2f%%", symbol, stats["price_change_pct"])
        return stats

    # -----------------------------------------------------------------
    # Supported Symbols
    # -----------------------------------------------------------------

    def get_supported_symbols(self) -> list[str]:
        """
        Get a list of all trading symbols available on Binance.

        Returns:
            List of symbol strings (e.g., ``["BTCUSDT", "ETHUSDT", ...]``).
        """
        url = f"{self.BASE_URL}/exchangeInfo"

        try:
            data = self._request_with_retry(url, {})
            symbols = [s["symbol"] for s in data.get("symbols", [])]
            logger.info("Fetched %d supported symbols from Binance", len(symbols))
            return symbols
        except Exception as exc:
            logger.error("Failed to fetch supported symbols: %s", exc)
            return []

    # -----------------------------------------------------------------
    # Private: Retry Logic with Exponential Backoff
    # -----------------------------------------------------------------

    def _request_with_retry(
        self,
        url: str,
        params: dict,
    ) -> dict | list:
        """
        Make an HTTP GET request with exponential backoff retry logic.

        Args:
            url: The API endpoint URL.
            params: Query parameters.

        Returns:
            Parsed JSON response (dict or list).

        Raises:
            requests.exceptions.RequestException: After all retries are exhausted.
        """
        last_exception: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(
                    url, params=params, timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as exc:
                last_exception = exc
                wait_time = BACKOFF_FACTOR * (2 ** (attempt - 1))

                logger.warning(
                    "Binance API request failed (attempt %d/%d): %s. "
                    "Retrying in %.1fs...",
                    attempt, MAX_RETRIES, exc, wait_time,
                )

                if attempt < MAX_RETRIES:
                    time.sleep(wait_time)

        # All retries exhausted
        logger.error(
            "Binance API request failed after %d retries: %s",
            MAX_RETRIES, last_exception,
        )
        raise last_exception  # type: ignore[misc]
