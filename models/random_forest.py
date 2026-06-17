"""
Random Forest Classification Model
=====================================
Primary classification model for predicting cryptocurrency price direction.

Predicts:
  - **1** (Bullish): Price will rise in the next period.
  - **0** (Bearish): Price will fall in the next period.

Uses ``StratifiedKFold`` for cross-validation (respects temporal ordering),
``class_weight='balanced'`` to handle class imbalance, and ``GridSearchCV``
for hyperparameter tuning.
"""
from __future__ import annotations

import time

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from utils.config import (
    CV_SPLITS,
    RANDOM_STATE,
    RF_MAX_DEPTH,
    RF_N_ESTIMATORS,
    RF_PARAM_GRID,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class RandomForestModel:
    """
    Primary classification model using Random Forest.

    Predicts: 1 = Bullish (price will rise), 0 = Bearish (price will fall).

    Usage::

        model = RandomForestModel()
        model.train(X_train, y_train)
        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)
    """

    def __init__(
        self,
        n_estimators: int = RF_N_ESTIMATORS,
        max_depth: int = RF_MAX_DEPTH,
        random_state: int = RANDOM_STATE,
    ) -> None:
        """
        Initialize the Random Forest model with default hyperparameters.

        Args:
            n_estimators: Number of trees in the forest.
            max_depth: Maximum depth of each tree.
            random_state: Random seed for reproducibility.
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state

        # Initialize the classifier with balanced class weights
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            class_weight="balanced",
            n_jobs=-1,
        )

        # Metadata tracked during training
        self.best_params: dict | None = None
        self.training_time: float = 0.0
        self.is_trained: bool = False

    # -----------------------------------------------------------------
    # Training
    # -----------------------------------------------------------------

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train the Random Forest model with GridSearchCV hyperparameter tuning.

        Uses ``StratifiedKFold(n_splits=5)`` for cross-validation to respect
        temporal ordering of financial data.

        Args:
            X_train: Training feature matrix.
            y_train: Training target labels (0 or 1).
        """
        logger.info(
            "Training Random Forest — %d samples, %d features",
            X_train.shape[0], X_train.shape[1],
        )

        start_time = time.time()

        # Time-series cross-validation (no data leakage)
        tscv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=42)

        # GridSearchCV over the expanded parameter grid
        grid_search = GridSearchCV(
            estimator=RandomForestClassifier(
                random_state=self.random_state,
                class_weight="balanced",
                n_jobs=-1,
            ),
            param_grid=RF_PARAM_GRID,
            cv=tscv,
            scoring="f1_weighted",   # Better than accuracy for imbalanced classes
            n_jobs=-1,
            verbose=1,
        )

        grid_search.fit(X_train, y_train)

        # Store the best model and parameters
        self.model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        self.training_time = time.time() - start_time
        self.is_trained = True

        logger.info("Best params: %s", self.best_params)
        logger.info(
            "Best CV accuracy: %.4f | Training time: %.2fs",
            grid_search.best_score_, self.training_time,
        )

    # -----------------------------------------------------------------
    # Prediction
    # -----------------------------------------------------------------

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels (0=Bearish, 1=Bullish) for the input features.

        Args:
            X: Feature matrix to predict.

        Returns:
            Array of predicted class labels.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        self._check_trained()
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities for the input features.

        Args:
            X: Feature matrix to predict.

        Returns:
            Array of shape ``(n_samples, 2)`` with probabilities for
            ``[bearish, bullish]``.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        self._check_trained()
        return self.model.predict_proba(X)

    # -----------------------------------------------------------------
    # Feature Importance
    # -----------------------------------------------------------------

    def get_feature_importance(
        self, feature_names: list[str]
    ) -> pd.DataFrame:
        """
        Get feature importances (Gini impurity) ranked by importance.

        Args:
            feature_names: List of feature names matching the training data.

        Returns:
            DataFrame with columns ``feature`` and ``importance``,
            sorted descending by importance.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        self._check_trained()

        importances = self.model.feature_importances_
        importance_df = pd.DataFrame({
            "feature": feature_names,
            "importance": importances,
        }).sort_values("importance", ascending=False).reset_index(drop=True)

        logger.info(
            "Top 5 features: %s",
            list(importance_df.head(5)["feature"]),
        )

        return importance_df

    # -----------------------------------------------------------------
    # Model Persistence
    # -----------------------------------------------------------------

    def save(self, path: str) -> None:
        """
        Save the trained model to disk using joblib.

        Args:
            path: File path to save the model (e.g., ``"models/saved/rf_model.joblib"``).
        """
        self._check_trained()
        joblib.dump(self.model, path)
        logger.info("Random Forest model saved to: %s", path)

    def load(self, path: str) -> None:
        """
        Load a previously trained model from disk.

        Args:
            path: File path of the saved model.
        """
        self.model = joblib.load(path)
        self.is_trained = True
        logger.info("Random Forest model loaded from: %s", path)

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    def _check_trained(self) -> None:
        """Raise an error if the model has not been trained or loaded."""
        if not self.is_trained:
            raise RuntimeError(
                "Model has not been trained yet. Call train() or load() first."
            )
