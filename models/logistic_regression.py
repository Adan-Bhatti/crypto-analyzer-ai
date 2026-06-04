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
from sklearn.preprocessing import StandardScaler

from utils.config import LR_C, LR_MAX_ITER, RANDOM_STATE
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

        self.model = LogisticRegression(
            C=C,
            max_iter=max_iter,
            random_state=RANDOM_STATE,
            class_weight="balanced",
            solver="lbfgs",
        )

        # Metadata tracked during training
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

        self.model.fit(X_scaled, y_train)

        self.training_time = time.time() - start_time
        self.is_trained = True

        logger.info(
            "Logistic Regression trained in %.2fs (C=%.2f, max_iter=%d)",
            self.training_time, self.C, self.max_iter,
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
