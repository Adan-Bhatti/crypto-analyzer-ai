"""
Feature Selection Module
=========================
Provides correlation-based and importance-based feature selection
to reduce dimensionality and improve model performance.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)


class FeatureSelector:
    """
    Selects the most relevant features for model training using
    correlation analysis and feature importance scores.

    Usage::

        selector = FeatureSelector()
        selected = selector.select_by_correlation(df, target_col="target")
        selected = selector.select_by_importance(df, importances, top_n=15)
    """

    # -----------------------------------------------------------------
    # Correlation-Based Selection
    # -----------------------------------------------------------------

    def select_by_correlation(
        self,
        df: pd.DataFrame,
        target_col: str = "target",
        threshold: float = 0.05,
        max_inter_correlation: float = 0.90,
    ) -> list[str]:
        """
        Select features that have meaningful correlation with the target
        and remove highly inter-correlated redundant features.

        Steps:
          1. Compute absolute correlation of each feature with the target.
          2. Keep features above the ``threshold``.
          3. Among kept features, remove one of any pair with inter-correlation
             exceeding ``max_inter_correlation``.

        Args:
            df: DataFrame with features and the target column.
            target_col: Name of the target column.
            threshold: Minimum absolute correlation with target to keep a feature.
            max_inter_correlation: Maximum allowed pairwise correlation between
                                   retained features.

        Returns:
            List of selected feature names.
        """
        logger.info(
            "Running correlation-based selection (threshold=%.2f, "
            "max_inter_corr=%.2f)",
            threshold, max_inter_correlation,
        )

        # Only consider numeric columns
        numeric_df = df.select_dtypes(include=[np.number])

        if target_col not in numeric_df.columns:
            logger.warning("Target column '%s' not found; returning all features", target_col)
            return [c for c in numeric_df.columns if c != target_col]

        # Step 1: Correlation with target
        corr_with_target = numeric_df.corr()[target_col].drop(target_col).abs()
        above_threshold = corr_with_target[corr_with_target >= threshold]
        selected = list(above_threshold.sort_values(ascending=False).index)

        logger.info(
            "%d features above correlation threshold %.2f",
            len(selected), threshold,
        )

        # Step 2: Remove highly inter-correlated features
        selected = self._remove_inter_correlated(
            df[selected], max_inter_correlation
        )

        logger.info("Final selected features: %d", len(selected))
        return selected

    # -----------------------------------------------------------------
    # Importance-Based Selection
    # -----------------------------------------------------------------

    def select_by_importance(
        self,
        feature_names: list[str],
        importances: np.ndarray,
        top_n: int = 15,
    ) -> list[str]:
        """
        Select the top-N features based on model-derived importance scores
        (e.g., Random Forest Gini importance).

        Args:
            feature_names: List of feature names corresponding to the importances.
            importances: Array of importance scores (same length as ``feature_names``).
            top_n: Number of top features to select.

        Returns:
            List of top-N feature names sorted by importance (descending).
        """
        if len(feature_names) != len(importances):
            raise ValueError(
                f"Length mismatch: {len(feature_names)} names vs "
                f"{len(importances)} importances"
            )

        importance_df = pd.DataFrame({
            "feature": feature_names,
            "importance": importances,
        }).sort_values("importance", ascending=False)

        selected = list(importance_df.head(top_n)["feature"])
        logger.info("Top %d features by importance: %s", top_n, selected)

        return selected

    # -----------------------------------------------------------------
    # Combined Selection
    # -----------------------------------------------------------------

    def select_features(
        self,
        df: pd.DataFrame,
        target_col: str = "target",
        importances: np.ndarray | None = None,
        top_n: int = 15,
    ) -> list[str]:
        """
        Combine correlation-based and importance-based selection.

        If importances are provided, uses the intersection of both methods.
        Otherwise, falls back to correlation-based selection only.

        Args:
            df: Feature DataFrame with target column.
            target_col: Name of the target column.
            importances: Optional array of feature importances.
            top_n: Number of top features for importance-based selection.

        Returns:
            List of selected feature names.
        """
        # Get correlation-based selection
        corr_features = set(self.select_by_correlation(df, target_col))

        if importances is not None:
            feature_cols = [c for c in df.columns if c != target_col]
            imp_features = set(
                self.select_by_importance(feature_cols, importances, top_n)
            )
            # Use union to be inclusive
            combined = list(corr_features | imp_features)
            logger.info(
                "Combined selection: %d (corr=%d, imp=%d, union=%d)",
                len(combined), len(corr_features), len(imp_features), len(combined),
            )
            return combined

        return list(corr_features)

    # -----------------------------------------------------------------
    # Correlation Matrix Computation
    # -----------------------------------------------------------------

    def get_correlation_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute and return the Pearson correlation matrix for numeric columns.

        Args:
            df: Input DataFrame.

        Returns:
            Correlation matrix as a DataFrame.
        """
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr()

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _remove_inter_correlated(
        df: pd.DataFrame,
        max_corr: float,
    ) -> list[str]:
        """
        Remove one of each pair of features that are highly correlated
        with each other, keeping the first occurrence.

        Args:
            df: DataFrame containing only the candidate features.
            max_corr: Maximum allowed pairwise correlation.

        Returns:
            List of feature names with redundant features removed.
        """
        corr_matrix = df.corr().abs()
        upper_tri = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )

        # Find columns to drop (exceeding max_corr with any other column)
        to_drop = set()
        for column in upper_tri.columns:
            high_corr = upper_tri.index[upper_tri[column] > max_corr].tolist()
            to_drop.update(high_corr)

        remaining = [c for c in df.columns if c not in to_drop]

        if to_drop:
            logger.info(
                "Removed %d inter-correlated features: %s",
                len(to_drop), list(to_drop),
            )

        return remaining
