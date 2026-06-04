"""
Model Evaluation Module
========================
Provides comprehensive evaluation metrics for classification models:
  - Accuracy, Precision, Recall, F1-Score, ROC-AUC
  - Confusion matrix computation and Plotly visualization
  - Cross-validation with ``TimeSeriesSplit``
  - Classification report generation
  - ROC curve plotting

Also handles automatic re-tuning when accuracy falls below the 80% target.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import TimeSeriesSplit, cross_val_score

from utils.config import CHART_TEMPLATE, CV_SPLITS, MIN_ACCURACY_TARGET, PRIMARY_ACCENT
from utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Result Dataclass
# =============================================================================

@dataclass
class EvaluationMetrics:
    """Container for model evaluation metrics."""

    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    roc_auc: float = 0.0
    confusion_mat: np.ndarray = field(default_factory=lambda: np.zeros((2, 2)))
    below_target: bool = False


# =============================================================================
# ModelEvaluator Class
# =============================================================================

class ModelEvaluator:
    """
    Computes evaluation metrics, confusion matrices, ROC curves,
    and cross-validation scores for classification models.

    Usage::

        evaluator = ModelEvaluator()
        metrics = evaluator.compute_metrics(y_true, y_pred, y_proba)
        fig = evaluator.plot_confusion_matrix(metrics.confusion_mat)
    """

    # -----------------------------------------------------------------
    # Core Metrics Computation
    # -----------------------------------------------------------------

    def compute_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: np.ndarray | None = None,
    ) -> EvaluationMetrics:
        """
        Compute all classification metrics.

        Args:
            y_true: True labels.
            y_pred: Predicted labels.
            y_proba: Predicted probabilities for the positive class (optional).

        Returns:
            ``EvaluationMetrics`` dataclass with all computed metrics.
        """
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        # ROC-AUC requires probability scores
        roc_auc = 0.0
        if y_proba is not None:
            try:
                roc_auc = roc_auc_score(y_true, y_proba)
            except ValueError as exc:
                logger.warning("ROC-AUC computation failed: %s", exc)

        cm = confusion_matrix(y_true, y_pred)

        # Check if below target
        below_target = accuracy < MIN_ACCURACY_TARGET
        if below_target:
            logger.warning(
                "Model accuracy %.4f is below target %.2f — consider re-tuning!",
                accuracy, MIN_ACCURACY_TARGET,
            )

        metrics = EvaluationMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            roc_auc=roc_auc,
            confusion_mat=cm,
            below_target=below_target,
        )

        logger.info(
            "Evaluation — Acc: %.4f | Prec: %.4f | Rec: %.4f | F1: %.4f | AUC: %.4f",
            accuracy, precision, recall, f1, roc_auc,
        )

        return metrics

    # -----------------------------------------------------------------
    # Confusion Matrix
    # -----------------------------------------------------------------

    def compute_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> np.ndarray:
        """
        Compute the confusion matrix.

        Args:
            y_true: True labels.
            y_pred: Predicted labels.

        Returns:
            2×2 confusion matrix as a numpy array.
        """
        return confusion_matrix(y_true, y_pred)

    # -----------------------------------------------------------------
    # ROC-AUC
    # -----------------------------------------------------------------

    def compute_roc_auc(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
    ) -> float:
        """
        Compute the ROC-AUC score.

        Args:
            y_true: True binary labels.
            y_proba: Predicted probabilities for the positive class.

        Returns:
            ROC-AUC score as a float.
        """
        try:
            score = roc_auc_score(y_true, y_proba)
            logger.info("ROC-AUC: %.4f", score)
            return float(score)
        except ValueError as exc:
            logger.warning("ROC-AUC computation failed: %s", exc)
            return 0.0

    # -----------------------------------------------------------------
    # Cross-Validation
    # -----------------------------------------------------------------

    def cross_validate_model(
        self,
        model: object,
        X: np.ndarray,
        y: np.ndarray,
        n_splits: int = CV_SPLITS,
    ) -> dict[str, list[float]]:
        """
        Run time-series cross-validation and return fold-wise scores.

        Args:
            model: The sklearn estimator to evaluate.
            X: Feature matrix.
            y: Target labels.
            n_splits: Number of cross-validation folds.

        Returns:
            Dictionary with keys ``"accuracy"``, ``"precision"``, ``"recall"``,
            ``"f1"`` mapping to lists of per-fold scores.
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)

        # Compute scores for multiple metrics
        results: dict[str, list[float]] = {}

        for metric_name, scoring in [
            ("accuracy", "accuracy"),
            ("precision", "precision"),
            ("recall", "recall"),
            ("f1", "f1"),
        ]:
            scores = cross_val_score(
                model, X, y, cv=tscv, scoring=scoring, n_jobs=-1
            )
            results[metric_name] = scores.tolist()

        logger.info(
            "Cross-validation (k=%d) — Mean accuracy: %.4f ± %.4f",
            n_splits,
            np.mean(results["accuracy"]),
            np.std(results["accuracy"]),
        )

        return results

    # -----------------------------------------------------------------
    # Classification Report
    # -----------------------------------------------------------------

    def generate_classification_report(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> str:
        """
        Generate a text-based classification report.

        Args:
            y_true: True labels.
            y_pred: Predicted labels.

        Returns:
            Formatted classification report string.
        """
        report = classification_report(
            y_true, y_pred,
            target_names=["Bearish (0)", "Bullish (1)"],
            zero_division=0,
        )
        logger.info("Classification Report:\n%s", report)
        return report

    # -----------------------------------------------------------------
    # Plotly Visualization: Confusion Matrix
    # -----------------------------------------------------------------

    def plot_confusion_matrix(
        self,
        cm: np.ndarray,
        labels: list[str] | None = None,
    ) -> go.Figure:
        """
        Create a Plotly heatmap of the confusion matrix.

        Args:
            cm: 2×2 confusion matrix.
            labels: Class labels (default: ``["Bearish", "Bullish"]``).

        Returns:
            Plotly ``Figure`` object.
        """
        if labels is None:
            labels = ["Bearish", "Bullish"]

        fig = go.Figure(data=go.Heatmap(
            z=cm,
            x=labels,
            y=labels,
            colorscale=[[0, "#0E1117"], [1, PRIMARY_ACCENT]],
            text=cm,
            texttemplate="%{text}",
            textfont={"size": 18},
            hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
        ))

        fig.update_layout(
            title="Confusion Matrix",
            xaxis_title="Predicted Label",
            yaxis_title="Actual Label",
            template=CHART_TEMPLATE,
            width=500,
            height=500,
        )

        return fig

    # -----------------------------------------------------------------
    # Plotly Visualization: ROC Curve
    # -----------------------------------------------------------------

    def plot_roc_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        label: str = "Model",
    ) -> go.Figure:
        """
        Create a Plotly ROC curve plot.

        Args:
            y_true: True binary labels.
            y_proba: Predicted probabilities for the positive class.
            label: Label for the legend entry.

        Returns:
            Plotly ``Figure`` object with the ROC curve and diagonal reference.
        """
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        auc_score = roc_auc_score(y_true, y_proba)

        fig = go.Figure()

        # ROC curve
        fig.add_trace(go.Scatter(
            x=fpr, y=tpr,
            mode="lines",
            name=f"{label} (AUC = {auc_score:.4f})",
            line=dict(color=PRIMARY_ACCENT, width=2),
        ))

        # Diagonal reference line (random classifier)
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode="lines",
            name="Random Classifier",
            line=dict(color="gray", width=1, dash="dash"),
        ))

        fig.update_layout(
            title="ROC Curve",
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            template=CHART_TEMPLATE,
            legend=dict(x=0.6, y=0.1),
        )

        return fig
