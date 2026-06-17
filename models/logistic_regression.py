"""
Logistic Regression Baseline Model
=====================================
Baseline classifier for comparison with the Random Forest model.
Uses ``StandardScaler`` before fitting to normalize feature magnitudes.
"""
from __future__ import annotations

import time

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler

from utils.config import CV_SPLITS, LR_C, LR_MAX_ITER, LR_PARAM_GRID, RANDOM_STATE
from utils.logger import get_logger

logger = get_logger(__name__)


class LogisticRegressionModel:
    """
    Baseline classifier using Logistic Regression with StandardScaler.

    Serves as a comparison point against Random Forest — useful for
    demonstrating the trade-offs between interpretability and accuracy.

    Usage::

        model = LogisticRegressionModel()
        model.train(X_train, y_train)
        predictions = model.predict(X_test)
    """

    def __init__(
        self,
        C: float = LR_C,
        max_iter: int = LR_MAX_ITER,
    ) -> None:
        """
        Initialize the Logistic Regression model.

        Args:
            C: Inverse of regularization strength. Smaller values =
               stronger regularization.
            max_iter: Maximum number of iterations for the solver.
        """
        self.C = C
        self.max_iter = max_iter

        # StandardScaler is applied before fitting (critical for LR performance)
        self.scaler = StandardScaler()

        # Base estimator; will be replaced by GridSearchCV best estimator
        self.model = LogisticRegression(
            C=C,
            max_iter=max_iter,
            random_state=RANDOM_STATE,
            class_weight="balanced",
            solver="lbfgs",
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
        Train the Logistic Regression model.

        Applies ``StandardScaler`` to the training data before fitting.

        Args:
            X_train: Training feature matrix.
            y_train: Training target labels (0 or 1).
        """
        logger.info(
            "Training Logistic Regression — %d samples, %d features",
            X_train.shape[0], X_train.shape[1],
        )

        start_time = time.time()

        # Scale features (important for convergence)
        X_scaled = self.scaler.fit_transform(X_train)

        # Time-series cross-validation (no data leakage)
        tscv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=42)

        # GridSearchCV to find optimal C, solver, and max_iter
        grid_search = GridSearchCV(
            estimator=LogisticRegression(
                random_state=RANDOM_STATE,
                class_weight="balanced",
            ),
            param_grid=LR_PARAM_GRID,
            cv=tscv,
            scoring="f1_weighted",
            n_jobs=-1,
            verbose=1,
        )

        grid_search.fit(X_scaled, y_train)

        self.model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        self.training_time = time.time() - start_time
        self.is_trained = True

        logger.info(
            "Logistic Regression best params: %s | CV f1_weighted: %.4f | Time: %.2fs",
            self.best_params, grid_search.best_score_, self.training_time,
        )

    # -----------------------------------------------------------------
    # Prediction
    # -----------------------------------------------------------------

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels (0=Bearish, 1=Bullish).

        Args:
            X: Feature matrix (will be scaled using the fitted scaler).

        Returns:
            Array of predicted class labels.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        self._check_trained()
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.

        Args:
            X: Feature matrix (will be scaled using the fitted scaler).

        Returns:
            Array of shape ``(n_samples, 2)`` with probabilities for
            ``[bearish, bullish]``.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        self._check_trained()
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    # -----------------------------------------------------------------
    # Model Persistence
    # -----------------------------------------------------------------

    def save(self, path: str) -> None:
        """
        Save the trained model and scaler to disk.

        Args:
            path: File path to save the model.
        """
        self._check_trained()
        # Save both the model and scaler together
        joblib.dump({"model": self.model, "scaler": self.scaler}, path)
        logger.info("Logistic Regression model saved to: %s", path)

    def load(self, path: str) -> None:
        """
        Load a previously trained model and scaler from disk.

        Args:
            path: File path of the saved model.
        """
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.is_trained = True
        logger.info("Logistic Regression model loaded from: %s", path)

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    def _check_trained(self) -> None:
        """Raise an error if the model has not been trained or loaded."""
        if not self.is_trained:
            raise RuntimeError(
                "Model has not been trained yet. Call train() or load() first."
            )
