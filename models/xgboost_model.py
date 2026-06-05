"""
XGBoost Classification Model
==============================
Gradient-boosted tree classifier for predicting cryptocurrency price direction.

Predicts:
  - **1** (Bullish): Price will rise in the next period.
  - **0** (Bearish): Price will fall in the next period.

Uses ``TimeSeriesSplit`` for cross-validation, ``scale_pos_weight`` to handle
class imbalance, and ``GridSearchCV`` for hyperparameter tuning.

XGBoost typically outperforms Random Forest on tabular financial data due to:
  - Sequential boosting (each tree corrects the previous one's errors)
  - Built-in L1/L2 regularization (reduces overfitting)
  - Handles missing values natively
"""
from __future__ import annotations

import time

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from xgboost import XGBClassifier

from utils.config import (
    CV_SPLITS,
    RANDOM_STATE,
    XGB_LEARNING_RATE,
    XGB_MAX_DEPTH,
    XGB_N_ESTIMATORS,
    XGB_PARAM_GRID,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class XGBoostModel:
    """
    Primary gradient-boosted tree classifier using XGBoost.

    Predicts: 1 = Bullish (price will rise), 0 = Bearish (price will fall).

    Usage::

        model = XGBoostModel()
        model.train(X_train, y_train)
        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)
    """

    def __init__(
        self,
        n_estimators: int = XGB_N_ESTIMATORS,
        max_depth: int = XGB_MAX_DEPTH,
        learning_rate: float = XGB_LEARNING_RATE,
        random_state: int = RANDOM_STATE,
    ) -> None:
        """
        Initialize the XGBoost model with default hyperparameters.

        Args:
            n_estimators: Number of boosting rounds.
            max_depth: Maximum depth of each tree.
            learning_rate: Step size shrinkage (eta) to prevent overfitting.
            random_state: Random seed for reproducibility.
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state

        # Initialize the base classifier
        self.model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            use_label_encoder=False,
            eval_metric="logloss",
            n_jobs=-1,
            verbosity=0,
        )

        # Metadata tracked during training
        self.best_params: dict | None = None
        self.training_time: float = 0.0
        self.is_trained: bool = False
        self._scale_pos_weight: float = 1.0

    # -----------------------------------------------------------------
    # Training
    # -----------------------------------------------------------------

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train the XGBoost model with GridSearchCV hyperparameter tuning.

        Computes ``scale_pos_weight`` from the class distribution to handle
        imbalanced crypto data. Uses ``TimeSeriesSplit`` for cross-validation.

        Args:
            X_train: Training feature matrix.
            y_train: Training target labels (0 or 1).
        """
        logger.info(
            "Training XGBoost — %d samples, %d features",
            X_train.shape[0], X_train.shape[1],
        )

        start_time = time.time()

        # Compute scale_pos_weight to handle class imbalance
        # = count(negative) / count(positive)
        neg_count = int(np.sum(y_train == 0))
        pos_count = int(np.sum(y_train == 1))
        self._scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
        logger.info(
            "Class distribution — Bearish: %d, Bullish: %d, scale_pos_weight: %.3f",
            neg_count, pos_count, self._scale_pos_weight,
        )

        # Time-series cross-validation (no data leakage)
        tscv = TimeSeriesSplit(n_splits=CV_SPLITS)

        # GridSearchCV over the expanded parameter grid
        grid_search = GridSearchCV(
            estimator=XGBClassifier(
                random_state=self.random_state,
                scale_pos_weight=self._scale_pos_weight,
                use_label_encoder=False,
                eval_metric="logloss",
                n_jobs=-1,
                verbosity=0,
            ),
            param_grid=XGB_PARAM_GRID,
            cv=tscv,
            scoring="f1_weighted",
            n_jobs=-1,
            verbose=1,
        )

        grid_search.fit(X_train, y_train)

        # Store the best model and parameters
        self.model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        self.training_time = time.time() - start_time
        self.is_trained = True

        logger.info("XGBoost best params: %s", self.best_params)
        logger.info(
            "Best CV f1_weighted: %.4f | Training time: %.2fs",
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
        Get feature importances (gain-based) ranked by importance.

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
            "XGBoost Top 5 features: %s",
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
            path: File path to save the model (e.g., ``"models/saved/xgb_model.joblib"``).
        """
        self._check_trained()
        joblib.dump(self.model, path)
        logger.info("XGBoost model saved to: %s", path)

    def load(self, path: str) -> None:
        """
        Load a previously trained model from disk.

        Args:
            path: File path of the saved model.
        """
        self.model = joblib.load(path)
        self.is_trained = True
        logger.info("XGBoost model loaded from: %s", path)

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    def _check_trained(self) -> None:
        """Raise an error if the model has not been trained or loaded."""
        if not self.is_trained:
            raise RuntimeError(
                "XGBoost model has not been trained yet. Call train() or load() first."
            )
