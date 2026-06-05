"""
Feature Engineering Module
===========================
Generates technical indicators and derived features from raw OHLCV data.

Features created:
  - SMA (Simple Moving Average) — windows: 7, 14, 21
  - EMA (Exponential Moving Average) — windows: 12, 26
  - RSI (Relative Strength Index) — window: 14
  - MACD + MACD Signal + MACD Diff — windows: 12, 26, 9
  - Bollinger Bands (upper, lower, middle) — window: 20
  - ATR (Average True Range) — window: 14
  - OBV (On-Balance Volume)
  - Stochastic Oscillator (%K, %D) — window: 14
  - Williams %R — lookback: 14
  - Volume Change % — 1-period pct_change on Volume
  - Daily Returns — 1-period pct_change on Close
  - Rolling Volatility — 14-period std of daily returns
  - Price Momentum — 5-period Close diff
  - Lag Features — close_lag_1, close_lag_3, close_lag_5, close_lag_7
  - Rolling Return Features — return_7d, return_14d, return_21d
  - Target Label — 1 if next Close > current Close, else 0
"""
from __future__ import annotations

import pandas as pd
import ta

from utils.config import (
    ATR_WINDOW,
    BOLLINGER_WINDOW,
    EMA_WINDOWS,
    LAG_PERIODS,
    MACD_FAST,
    MACD_SIGNAL,
    MACD_SLOW,
    MOMENTUM_WINDOW,
    ROLL_RETURN_WINDOWS,
    RSI_WINDOW,
    SMA_WINDOWS,
    STOCH_WINDOW,
    VOLATILITY_WINDOW,
    WILLIAMS_LBPERIOD,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class FeatureEngineer:
    """
    Creates technical analysis features from OHLCV data.

    All methods accept and return a DataFrame, making them chainable.
    Use ``engineer_all()`` to apply every feature in a single call.

    Usage::

        fe = FeatureEngineer()
        featured_df = fe.engineer_all(clean_df)
    """

    # -----------------------------------------------------------------
    # Simple Moving Averages
    # -----------------------------------------------------------------

    def add_sma(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Simple Moving Average columns for configured windows.

        Creates columns: ``sma_7``, ``sma_14``, ``sma_21``.

        Args:
            df: DataFrame with a ``close`` column.

        Returns:
            DataFrame with SMA columns appended.
        """
        for window in SMA_WINDOWS:
            col_name = f"sma_{window}"
            df[col_name] = ta.trend.sma_indicator(df["close"], window=window)
            logger.debug("Added %s", col_name)

        return df

    # -----------------------------------------------------------------
    # Exponential Moving Averages
    # -----------------------------------------------------------------

    def add_ema(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Exponential Moving Average columns for configured windows.

        Creates columns: ``ema_12``, ``ema_26``.

        Args:
            df: DataFrame with a ``close`` column.

        Returns:
            DataFrame with EMA columns appended.
        """
        for window in EMA_WINDOWS:
            col_name = f"ema_{window}"
            df[col_name] = ta.trend.ema_indicator(df["close"], window=window)
            logger.debug("Added %s", col_name)

        return df

    # -----------------------------------------------------------------
    # Relative Strength Index
    # -----------------------------------------------------------------

    def add_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add RSI (Relative Strength Index) column.

        Creates column: ``rsi_14``.

        Args:
            df: DataFrame with a ``close`` column.

        Returns:
            DataFrame with RSI column appended.
        """
        col_name = f"rsi_{RSI_WINDOW}"
        df[col_name] = ta.momentum.rsi(df["close"], window=RSI_WINDOW)
        logger.debug("Added %s", col_name)

        return df

    # -----------------------------------------------------------------
    # MACD (Moving Average Convergence Divergence)
    # -----------------------------------------------------------------

    def add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add MACD and MACD Signal Line columns.

        Creates columns: ``macd``, ``macd_signal``, ``macd_diff``.

        Args:
            df: DataFrame with a ``close`` column.

        Returns:
            DataFrame with MACD columns appended.
        """
        # MACD line (fast EMA - slow EMA)
        df["macd"] = ta.trend.macd(
            df["close"], window_slow=MACD_SLOW, window_fast=MACD_FAST
        )
        # Signal line (EMA of MACD)
        df["macd_signal"] = ta.trend.macd_signal(
            df["close"],
            window_slow=MACD_SLOW,
            window_fast=MACD_FAST,
            window_sign=MACD_SIGNAL,
        )
        # MACD histogram (MACD - Signal)
        df["macd_diff"] = ta.trend.macd_diff(
            df["close"],
            window_slow=MACD_SLOW,
            window_fast=MACD_FAST,
            window_sign=MACD_SIGNAL,
        )

        logger.debug("Added MACD, MACD Signal, MACD Diff")
        return df

    # -----------------------------------------------------------------
    # Bollinger Bands
    # -----------------------------------------------------------------

    def add_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Bollinger Band upper and lower boundary columns.

        Creates columns: ``bb_upper``, ``bb_lower``, ``bb_middle``.

        Args:
            df: DataFrame with a ``close`` column.

        Returns:
            DataFrame with Bollinger Band columns appended.
        """
        bb = ta.volatility.BollingerBands(
            close=df["close"], window=BOLLINGER_WINDOW, window_dev=2
        )

        df["bb_upper"] = bb.bollinger_hband()
        df["bb_lower"] = bb.bollinger_lband()
        df["bb_middle"] = bb.bollinger_mavg()

        logger.debug("Added Bollinger Bands (upper, lower, middle)")
        return df

    # -----------------------------------------------------------------
    # Volume Features
    # -----------------------------------------------------------------

    def add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume-derived features.

        Creates column: ``volume_change`` (1-period percentage change of volume).

        Args:
            df: DataFrame with a ``volume`` column.

        Returns:
            DataFrame with volume feature columns appended.
        """
        df["volume_change"] = df["volume"].pct_change()
        logger.debug("Added volume_change")

        return df

    # -----------------------------------------------------------------
    # Volatility & Returns
    # -----------------------------------------------------------------

    def add_volatility(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add daily returns, rolling volatility, and price momentum features.

        Creates columns:
          - ``daily_return``: 1-period percentage change of Close.
          - ``volatility_14``: 14-period rolling standard deviation of daily returns.
          - ``daily_return_std``: Same as ``volatility_14`` (alias for clustering).
          - ``price_momentum``: 5-period difference of Close.

        Args:
            df: DataFrame with a ``close`` column.

        Returns:
            DataFrame with volatility and momentum columns appended.
        """
        # Daily returns
        df["daily_return"] = df["close"].pct_change()

        # Rolling volatility (std of daily returns over the configured window)
        df["volatility_14"] = df["daily_return"].rolling(
            window=VOLATILITY_WINDOW
        ).std()

        # Alias for clustering feature compatibility
        df["daily_return_std"] = df["volatility_14"]

        # Price momentum (absolute difference over the configured window)
        df["price_momentum"] = df["close"].diff(MOMENTUM_WINDOW)

        logger.debug("Added daily_return, volatility_14, daily_return_std, price_momentum")
        return df

    # -----------------------------------------------------------------
    # ATR — Average True Range
    # -----------------------------------------------------------------

    def add_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Average True Range (ATR) column.

        ATR measures market volatility using High, Low, and Close.
        Creates column: ``atr_14``.

        Args:
            df: DataFrame with ``high``, ``low``, ``close`` columns.

        Returns:
            DataFrame with ATR column appended.
        """
        col_name = f"atr_{ATR_WINDOW}"
        df[col_name] = ta.volatility.average_true_range(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=ATR_WINDOW,
        )
        logger.debug("Added %s", col_name)
        return df

    # -----------------------------------------------------------------
    # OBV — On-Balance Volume
    # -----------------------------------------------------------------

    def add_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add On-Balance Volume (OBV) column.

        OBV uses volume flow to predict changes in price.
        Creates column: ``obv``.

        Args:
            df: DataFrame with ``close`` and ``volume`` columns.

        Returns:
            DataFrame with OBV column appended.
        """
        df["obv"] = ta.volume.on_balance_volume(
            close=df["close"],
            volume=df["volume"],
        )
        logger.debug("Added OBV")
        return df

    # -----------------------------------------------------------------
    # Stochastic Oscillator
    # -----------------------------------------------------------------

    def add_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Stochastic Oscillator (%K and %D) columns.

        Identifies overbought/oversold conditions.
        Creates columns: ``stoch_k``, ``stoch_d``.

        Args:
            df: DataFrame with ``high``, ``low``, ``close`` columns.

        Returns:
            DataFrame with Stochastic columns appended.
        """
        stoch = ta.momentum.StochasticOscillator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=STOCH_WINDOW,
            smooth_window=3,
        )
        df["stoch_k"] = stoch.stoch()
        df["stoch_d"] = stoch.stoch_signal()
        logger.debug("Added stoch_k, stoch_d")
        return df

    # -----------------------------------------------------------------
    # Williams %R
    # -----------------------------------------------------------------

    def add_williams_r(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Williams %R momentum column.

        Ranges from -100 to 0; values above -20 indicate overbought,
        values below -80 indicate oversold.
        Creates column: ``williams_r``.

        Args:
            df: DataFrame with ``high``, ``low``, ``close`` columns.

        Returns:
            DataFrame with Williams %R column appended.
        """
        df["williams_r"] = ta.momentum.williams_r(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            lbp=WILLIAMS_LBPERIOD,
        )
        logger.debug("Added williams_r")
        return df

    # -----------------------------------------------------------------
    # Lag Features
    # -----------------------------------------------------------------

    def add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add lagged close price features.

        Creates columns: ``close_lag_1``, ``close_lag_3``, ``close_lag_5``,
        ``close_lag_7``.

        Args:
            df: DataFrame with a ``close`` column.

        Returns:
            DataFrame with lag columns appended.
        """
        for lag in LAG_PERIODS:
            col_name = f"close_lag_{lag}"
            df[col_name] = df["close"].shift(lag)
            logger.debug("Added %s", col_name)
        return df

    # -----------------------------------------------------------------
    # Rolling Return Features
    # -----------------------------------------------------------------

    def add_rolling_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add rolling cumulative return features.

        Creates columns: ``return_7d``, ``return_14d``, ``return_21d``
        — percentage returns over each rolling window.

        Args:
            df: DataFrame with a ``close`` column.

        Returns:
            DataFrame with rolling return columns appended.
        """
        for window in ROLL_RETURN_WINDOWS:
            col_name = f"return_{window}d"
            df[col_name] = df["close"].pct_change(window)
            logger.debug("Added %s", col_name)
        return df

    # -----------------------------------------------------------------
    # Target Label
    # -----------------------------------------------------------------

    def add_target_label(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add the binary target label for supervised learning.

        Label logic:
          - **1** (Bullish): next period's Close > current Close.
          - **0** (Bearish): next period's Close ≤ current Close.

        Creates column: ``target``.

        Args:
            df: DataFrame with a ``close`` column.

        Returns:
            DataFrame with ``target`` column appended.
        """
        # Shift close by -1 to get the next period's close
        df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

        logger.debug("Added target label (1=Bullish, 0=Bearish)")
        return df

    # -----------------------------------------------------------------
    # Full Feature Engineering Pipeline
    # -----------------------------------------------------------------

    def engineer_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering steps in sequence and drop NaN rows.

        Execution order:
          1. SMA → 2. EMA → 3. RSI → 4. MACD → 5. Bollinger Bands
          → 6. ATR → 7. OBV → 8. Stochastic → 9. Williams %R
          → 10. Volume Features → 11. Volatility/Momentum
          → 12. Lag Features → 13. Rolling Returns → 14. Target Label.

        After feature generation, rows with NaN values (from rolling windows)
        are dropped, except for the last row's target NaN.

        Args:
            df: Cleaned OHLCV DataFrame.

        Returns:
            Feature-engineered DataFrame ready for model training.
        """
        logger.info("Starting feature engineering (%d rows)", len(df))

        df = self.add_sma(df)
        df = self.add_ema(df)
        df = self.add_rsi(df)
        df = self.add_macd(df)
        df = self.add_bollinger_bands(df)
        df = self.add_atr(df)
        df = self.add_obv(df)
        df = self.add_stochastic(df)
        df = self.add_williams_r(df)
        df = self.add_volume_features(df)
        df = self.add_volatility(df)
        df = self.add_lag_features(df)
        df = self.add_rolling_returns(df)
        df = self.add_target_label(df)

        # Drop rows with NaN from rolling-window indicators (first N rows)
        initial_len = len(df)
        df = df.dropna(subset=[
            col for col in df.columns if col != "target"
        ]).reset_index(drop=True)

        logger.info(
            "Feature engineering complete — %d features, %d rows "
            "(dropped %d NaN rows from rolling windows)",
            len(df.columns), len(df), initial_len - len(df),
        )

        return df
