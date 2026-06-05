"""
Data Cleaning Module
=====================
Provides a ``DataCleaner`` class that handles:
  - Duplicate removal
  - Missing value imputation (forward-fill by default)
  - Outlier removal via z-score filtering
  - Column normalization (renaming, type casting)
  - OHLCV validity checks
  - A unified ``clean()`` pipeline that chains all steps.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from utils.helpers import normalize_column_names
from utils.logger import get_logger

logger = get_logger(__name__)


class DataCleaner:
    """
    Cleans raw OHLCV cryptocurrency data for downstream feature engineering.

    Usage::

        cleaner = DataCleaner()
        clean_df = cleaner.clean(raw_df)
    """

    # -----------------------------------------------------------------
    # Duplicate Removal
    # -----------------------------------------------------------------

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate rows from the DataFrame.

        Args:
            df: Input DataFrame (may contain duplicates).

        Returns:
            DataFrame with duplicates removed.
        """
        initial_len = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        removed = initial_len - len(df)

        if removed > 0:
            logger.info("Removed %d duplicate rows", removed)

        return df

    # -----------------------------------------------------------------
    # Missing Value Handling
    # -----------------------------------------------------------------

    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: str = "ffill",
    ) -> pd.DataFrame:
        """
        Handle missing values in the DataFrame.

        Supported strategies:
          - ``"ffill"``: Forward-fill (propagate last valid value).
          - ``"bfill"``: Backward-fill.
          - ``"mean"``: Fill with column mean (numeric columns only).
          - ``"drop"``: Drop rows with any missing values.

        Args:
            df: Input DataFrame.
            strategy: The imputation strategy to use.

        Returns:
            DataFrame with missing values handled.
        """
        missing_before = df.isnull().sum().sum()

        if strategy == "ffill":
            df = df.ffill()
            # Handle any remaining NaNs at the start with backward-fill
            df = df.bfill()
        elif strategy == "bfill":
            df = df.bfill()
            df = df.ffill()
        elif strategy == "mean":
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        elif strategy == "drop":
            df = df.dropna().reset_index(drop=True)
        else:
            logger.warning("Unknown strategy '%s', defaulting to ffill", strategy)
            df = df.ffill().bfill()

        missing_after = df.isnull().sum().sum()
        logger.info(
            "Missing values: %d before -> %d after (strategy=%s)",
            missing_before, missing_after, strategy,
        )

        return df

    # -----------------------------------------------------------------
    # Outlier Removal
    # -----------------------------------------------------------------

    def remove_outliers(
        self,
        df: pd.DataFrame,
        z_threshold: float = 3.0,
    ) -> pd.DataFrame:
        """
        Remove rows where any numeric column has a z-score exceeding the threshold.

        This prevents extreme data points from distorting model training while
        preserving genuine market volatility patterns.

        Args:
            df: Input DataFrame.
            z_threshold: Maximum allowed absolute z-score. Rows exceeding
                         this in any numeric column are removed.

        Returns:
            DataFrame with outlier rows removed.
        """
        initial_len = len(df)

        # Only compute z-scores on numeric OHLCV columns
        numeric_cols = ["open", "high", "low", "close", "volume"]
        available_cols = [c for c in numeric_cols if c in df.columns]

        if not available_cols:
            logger.warning("No numeric OHLCV columns found for outlier removal")
            return df

        # Compute z-scores (suppress warning for zero-std columns)
        z_scores = np.abs(stats.zscore(df[available_cols], nan_policy="omit"))

        # Keep rows where ALL z-scores are within the threshold
        mask = (z_scores < z_threshold).all(axis=1)
        df = df.loc[mask].reset_index(drop=True)

        removed = initial_len - len(df)
        if removed > 0:
            logger.info(
                "Removed %d outlier rows (z-threshold=%.1f)", removed, z_threshold
            )

        return df

    # -----------------------------------------------------------------
    # Column Normalization
    # -----------------------------------------------------------------

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names to lowercase and cast OHLCV columns to float.

        Args:
            df: Input DataFrame.

        Returns:
            DataFrame with normalized column names and numeric types.
        """
        df = normalize_column_names(df)

        # Ensure numeric types for OHLCV columns
        numeric_cols = ["open", "high", "low", "close", "volume"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        logger.info("Column names normalized and numeric types enforced")
        return df

    # -----------------------------------------------------------------
    # OHLCV Validation
    # -----------------------------------------------------------------

    def validate_ohlcv(self, df: pd.DataFrame) -> bool:
        """
        Validate that the DataFrame contains logically consistent OHLCV data.

        Checks:
          - All required columns exist.
          - ``High >= Low`` for every row.
          - ``Open`` and ``Close`` are between ``Low`` and ``High``.
          - ``Volume >= 0`` for every row.

        Args:
            df: Input DataFrame.

        Returns:
            True if all validations pass, False otherwise.
        """
        required = ["open", "high", "low", "close", "volume"]

        # Check columns exist
        missing = [c for c in required if c not in df.columns]
        if missing:
            logger.error("OHLCV validation failed — missing columns: %s", missing)
            return False

        # High >= Low
        invalid_hl = (df["high"] < df["low"]).sum()
        if invalid_hl > 0:
            logger.warning("%d rows have High < Low", invalid_hl)

        # Volume >= 0
        negative_vol = (df["volume"] < 0).sum()
        if negative_vol > 0:
            logger.warning("%d rows have negative volume", negative_vol)

        is_valid = invalid_hl == 0 and negative_vol == 0
        logger.info("OHLCV validation: %s", "PASSED" if is_valid else "WARNINGS")
        return is_valid

    # -----------------------------------------------------------------
    # Full Cleaning Pipeline
    # -----------------------------------------------------------------

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run the complete cleaning pipeline in order:
          1. Normalize column names and types.
          2. Remove duplicates.
          3. Handle missing values (forward-fill).
          4. Remove outliers (z-score > 3.0).
          5. Validate OHLCV consistency.

        Args:
            df: Raw input DataFrame.

        Returns:
            Cleaned DataFrame ready for feature engineering.
        """
        logger.info("Starting full cleaning pipeline (%d rows)", len(df))

        df = self.normalize_columns(df)
        df = self.remove_duplicates(df)
        df = self.handle_missing_values(df, strategy="ffill")
        df = self.remove_outliers(df, z_threshold=3.0)
        self.validate_ohlcv(df)

        logger.info("Cleaning pipeline complete — %d rows remaining", len(df))
        return df
