"""
Crypto Pipeline Module
========================
Orchestrates the end-to-end data → prediction pipeline:
  1. Data loading (API or CSV)
  2. Data cleaning
  3. Feature engineering
  4. Model training (Random Forest + Logistic Regression)
  5. Prediction
  6. Risk classification (K-Means)
  7. Recommendation (Intelligent Agent)

Provides ``PipelineResult``, ``PredictionResult``, and ``RiskResult``
dataclasses for structured output.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from agent.recommendation_agent import RecommendationAgent, RecommendationResult
from data.cleaner import DataCleaner
from data.feature_engineer import FeatureEngineer
from data.loader import DataLoader
from models.kmeans_clustering import KMeansRiskClassifier
from models.logistic_regression import LogisticRegressionModel
from models.model_manager import ModelManager
from models.random_forest import RandomForestModel
from models.xgboost_model import XGBoostModel
from utils.config import CLUSTERING_FEATURES, TEST_SIZE
from utils.evaluator import EvaluationMetrics, ModelEvaluator
from utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Result Dataclasses
# =============================================================================

@dataclass
class PredictionResult:
    """Container for prediction outputs."""

    prediction: int                    # 1 = Bullish, 0 = Bearish
    bullish_prob: float                # Probability of bullish outcome
    bearish_prob: float                # Probability of bearish outcome
    rf_prediction: int = 0             # Random Forest prediction
    lr_prediction: int = 0             # Logistic Regression prediction
    xgb_prediction: int = 0            # XGBoost prediction
    rf_proba: np.ndarray = field(default_factory=lambda: np.array([]))
    lr_proba: np.ndarray = field(default_factory=lambda: np.array([]))
    xgb_proba: np.ndarray = field(default_factory=lambda: np.array([]))
    feature_importance: pd.DataFrame = field(default_factory=pd.DataFrame)


@dataclass
class RiskResult:
    """Container for risk classification outputs."""

    risk_level: str                    # "Low", "Medium", "High"
    cluster_id: int = 0
    silhouette_score: float = 0.0
    risk_distribution: dict = field(default_factory=dict)
    cluster_centers: pd.DataFrame = field(default_factory=pd.DataFrame)
    inertias: list[float] = field(default_factory=list)


@dataclass
class PipelineResult:
    """Container for the full pipeline output."""

    raw_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    engineered_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    prediction: PredictionResult | None = None
    risk: RiskResult | None = None
    recommendation: RecommendationResult | None = None
    evaluation_metrics: dict = field(default_factory=dict)
    pipeline_duration_sec: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# =============================================================================
# CryptoPipeline Class
# =============================================================================

class CryptoPipeline:
    """
    Orchestrates end-to-end: data loading → cleaning → feature engineering
    → model training → prediction → risk classification → recommendation.

    Usage::

        pipeline = CryptoPipeline()
        result = pipeline.run_full_pipeline(symbol="BTCUSDT")
    """

    def __init__(self) -> None:
        """Initialize all pipeline components."""
        self.loader = DataLoader()
        self.cleaner = DataCleaner()
        self.feature_engineer = FeatureEngineer()
        self.rf_model = RandomForestModel()
        self.lr_model = LogisticRegressionModel()
        self.xgb_model = XGBoostModel()
        self.kmeans = KMeansRiskClassifier()
        self.evaluator = ModelEvaluator()
        self.agent = RecommendationAgent()
        self.model_manager = ModelManager()

        # Pipeline state
        self._status: str = "idle"
        self._feature_names: list[str] = []

    # -----------------------------------------------------------------
    # Full Pipeline
    # -----------------------------------------------------------------

    def run_full_pipeline(
        self,
        symbol: str,
        data_source: str = "api",
        csv_path: str | None = None,
        retrain: bool = False,
    ) -> PipelineResult:
        """
        Run the complete analysis pipeline from data loading to recommendation.

        Args:
            symbol: Cryptocurrency symbol (e.g., ``"BTCUSDT"``).
            data_source: ``"api"`` to fetch from Binance/Yahoo, ``"csv"`` for local file.
            csv_path: Path to CSV file (required when ``data_source="csv"``).
            retrain: If True, retrain models even if saved models exist.

        Returns:
            ``PipelineResult`` with all outputs and metrics.
        """
        start_time = time.time()
        result = PipelineResult()
        self._status = "running"

        try:
            # Step 1: Load data
            logger.info("Pipeline Step 1: Loading data (%s)", data_source)
            if data_source == "csv" and csv_path:
                raw_df = self.loader.load_csv(csv_path)
            else:
                raw_df = self.loader.load_with_fallback(symbol)
            result.raw_df = raw_df

            # Step 2: Clean data
            logger.info("Pipeline Step 2: Cleaning data")
            clean_df = self.cleaner.clean(raw_df)

            # Step 3: Engineer features
            logger.info("Pipeline Step 3: Engineering features")
            engineered_df = self.feature_engineer.engineer_all(clean_df)
            result.engineered_df = engineered_df

            # Step 4: Train/load models + predict
            logger.info("Pipeline Step 4: Training models and predicting")
            prediction_result = self._train_and_predict(engineered_df, retrain)
            result.prediction = prediction_result

            # Step 5: Risk classification
            logger.info("Pipeline Step 5: Risk classification")
            risk_result = self.run_risk_classification(engineered_df)
            result.risk = risk_result

            # Step 6: Generate recommendation
            logger.info("Pipeline Step 6: Generating recommendation")
            current_price = float(engineered_df["close"].iloc[-1])
            model_confidence = result.evaluation_metrics.get("xgb_accuracy", 0.5)

            recommendation = self.agent.generate_recommendation(
                bullish_prob=prediction_result.bullish_prob,
                bearish_prob=prediction_result.bearish_prob,
                risk_level=risk_result.risk_level,
                current_price=current_price,
                model_confidence=model_confidence,
            )
            result.recommendation = recommendation

        except Exception as exc:
            error_msg = f"Pipeline error: {exc}"
            logger.error(error_msg)
            result.errors.append(error_msg)

        finally:
            result.pipeline_duration_sec = time.time() - start_time
            self._status = "complete"
            logger.info("Pipeline finished in %.2fs", result.pipeline_duration_sec)

        return result

    # -----------------------------------------------------------------
    # Prediction Only
    # -----------------------------------------------------------------

    def run_prediction_only(
        self, df: pd.DataFrame
    ) -> PredictionResult:
        """
        Run prediction using already-trained models (skips data loading/cleaning).

        Args:
            df: Feature-engineered DataFrame.

        Returns:
            ``PredictionResult`` with predictions from both models.
        """
        return self._train_and_predict(df, retrain=False)

    # -----------------------------------------------------------------
    # Risk Classification Only
    # -----------------------------------------------------------------

    def run_risk_classification(
        self, df: pd.DataFrame
    ) -> RiskResult:
        """
        Run K-Means risk classification on the provided DataFrame.

        Args:
            df: Feature-engineered DataFrame.

        Returns:
            ``RiskResult`` with risk level, cluster info, and diagnostics.
        """
        try:
            # Check if clustering features exist
            available_features = [f for f in CLUSTERING_FEATURES if f in df.columns]
            if len(available_features) < 2:
                return RiskResult(risk_level="Unknown")

            # Fit the K-Means model
            self.kmeans.fit(df)

            # Predict risk for the most recent data point
            last_row = df.iloc[[-1]]
            risk_labels = self.kmeans.predict_risk(last_row)
            risk_level = risk_labels.iloc[0] if not risk_labels.empty else "Unknown"

            return RiskResult(
                risk_level=risk_level,
                silhouette_score=self.kmeans.silhouette,
                risk_distribution=self.kmeans.get_risk_distribution(),
                cluster_centers=self.kmeans.get_cluster_centers(),
                inertias=self.kmeans.get_elbow_inertias(),
            )

        except Exception as exc:
            logger.error("Risk classification failed: %s", exc)
            return RiskResult(risk_level="Unknown")

    # -----------------------------------------------------------------
    # Pipeline Status
    # -----------------------------------------------------------------

    def get_pipeline_status(self) -> dict:
        """
        Get the current pipeline execution status.

        Returns:
            Dictionary with status details.
        """
        return {
            "status": self._status,
            "rf_trained": self.rf_model.is_trained,
            "lr_trained": self.lr_model.is_trained,
            "xgb_trained": self.xgb_model.is_trained,
            "kmeans_fitted": self.kmeans.is_fitted,
            "feature_count": len(self._feature_names),
        }

    # -----------------------------------------------------------------
    # Private: Train and Predict
    # -----------------------------------------------------------------

    def _train_and_predict(
        self,
        df: pd.DataFrame,
        retrain: bool = False,
    ) -> PredictionResult:
        """
        Train both models (or load saved) and generate predictions.

        Args:
            df: Feature-engineered DataFrame with target column.
            retrain: Force retraining even if saved models exist.

        Returns:
            ``PredictionResult`` with predictions from both models.
        """
        # Prepare features and target
        exclude_cols = ["date", "target", "timestamp"]
        feature_cols = [
            c for c in df.columns
            if c not in exclude_cols and df[c].dtype in ["float64", "int64", "float32"]
        ]
        self._feature_names = feature_cols

        # Split data (drop rows with NaN target for training)
        train_df = df.dropna(subset=["target"]).copy()

        X = train_df[feature_cols].values
        y = train_df["target"].values

        # Time-ordered split: 80% train, 20% test
        split_idx = int(len(X) * (1 - TEST_SIZE))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # --- Train or load Random Forest ---
        if retrain or not self.rf_model.is_trained:
            try:
                if not retrain and self.model_manager.model_exists("random_forest"):
                    self.rf_model.load(
                        self.model_manager._get_model_path("random_forest")
                    )
                else:
                    self.rf_model.train(X_train, y_train)
            except Exception as exc:
                logger.warning("RF load failed, retraining: %s", exc)
                self.rf_model.train(X_train, y_train)

        # --- Train or load Logistic Regression ---
        if retrain or not self.lr_model.is_trained:
            try:
                if not retrain and self.model_manager.model_exists("logistic_regression"):
                    self.lr_model.load(
                        self.model_manager._get_model_path("logistic_regression")
                    )
                else:
                    self.lr_model.train(X_train, y_train)
            except Exception as exc:
                logger.warning("LR load failed, retraining: %s", exc)
                self.lr_model.train(X_train, y_train)

        # --- Train or load XGBoost ---
        if retrain or not self.xgb_model.is_trained:
            try:
                if not retrain and self.model_manager.model_exists("xgboost"):
                    self.xgb_model.load(
                        self.model_manager._get_model_path("xgboost")
                    )
                else:
                    self.xgb_model.train(X_train, y_train)
            except Exception as exc:
                logger.warning("XGB load failed, retraining: %s", exc)
                self.xgb_model.train(X_train, y_train)

        # --- Evaluate on test set ---
        rf_pred = self.rf_model.predict(X_test)
        rf_proba = self.rf_model.predict_proba(X_test)
        lr_pred = self.lr_model.predict(X_test)
        lr_proba = self.lr_model.predict_proba(X_test)
        xgb_pred = self.xgb_model.predict(X_test)
        xgb_proba = self.xgb_model.predict_proba(X_test)

        rf_metrics = self.evaluator.compute_metrics(
            y_test, rf_pred, rf_proba[:, 1]
        )
        lr_metrics = self.evaluator.compute_metrics(
            y_test, lr_pred, lr_proba[:, 1]
        )
        xgb_metrics = self.evaluator.compute_metrics(
            y_test, xgb_pred, xgb_proba[:, 1]
        )

        # Store evaluation metrics for the pipeline result
        self._store_evaluation_metrics(rf_metrics, lr_metrics, xgb_metrics)

        # --- Predict on the latest data point ---
        latest_features = df[feature_cols].iloc[[-1]].values

        rf_latest_pred = self.rf_model.predict(latest_features)[0]
        rf_latest_proba = self.rf_model.predict_proba(latest_features)[0]
        lr_latest_pred = self.lr_model.predict(latest_features)[0]
        lr_latest_proba = self.lr_model.predict_proba(latest_features)[0]
        xgb_latest_pred = self.xgb_model.predict(latest_features)[0]
        xgb_latest_proba = self.xgb_model.predict_proba(latest_features)[0]

        # XGBoost is primary model — bullish prob is index 1
        bullish_prob = float(xgb_latest_proba[1])
        bearish_prob = float(xgb_latest_proba[0])

        # Feature importance from XGBoost (gain-based)
        importance_df = self.xgb_model.get_feature_importance(feature_cols)

        return PredictionResult(
            prediction=int(xgb_latest_pred),
            bullish_prob=bullish_prob,
            bearish_prob=bearish_prob,
            rf_prediction=int(rf_latest_pred),
            lr_prediction=int(lr_latest_pred),
            xgb_prediction=int(xgb_latest_pred),
            rf_proba=rf_latest_proba,
            lr_proba=lr_latest_proba,
            xgb_proba=xgb_latest_proba,
            feature_importance=importance_df,
        )

    def _store_evaluation_metrics(
        self,
        rf_metrics: EvaluationMetrics,
        lr_metrics: EvaluationMetrics,
        xgb_metrics: EvaluationMetrics,
    ) -> None:
        """Store evaluation metrics in a format accessible by the frontend."""
        self._evaluation_metrics = {
            "rf_accuracy": rf_metrics.accuracy,
            "rf_precision": rf_metrics.precision,
            "rf_recall": rf_metrics.recall,
            "rf_f1": rf_metrics.f1_score,
            "rf_roc_auc": rf_metrics.roc_auc,
            "rf_confusion_matrix": rf_metrics.confusion_mat,
            "rf_below_target": rf_metrics.below_target,
            "lr_accuracy": lr_metrics.accuracy,
            "lr_precision": lr_metrics.precision,
            "lr_recall": lr_metrics.recall,
            "lr_f1": lr_metrics.f1_score,
            "lr_roc_auc": lr_metrics.roc_auc,
            "lr_confusion_matrix": lr_metrics.confusion_mat,
            "lr_below_target": lr_metrics.below_target,
            "xgb_accuracy": xgb_metrics.accuracy,
            "xgb_precision": xgb_metrics.precision,
            "xgb_recall": xgb_metrics.recall,
            "xgb_f1": xgb_metrics.f1_score,
            "xgb_roc_auc": xgb_metrics.roc_auc,
            "xgb_confusion_matrix": xgb_metrics.confusion_mat,
            "xgb_below_target": xgb_metrics.below_target,
        }

    @property
    def evaluation_metrics(self) -> dict:
        """Return the most recent evaluation metrics."""
        return getattr(self, "_evaluation_metrics", {})
