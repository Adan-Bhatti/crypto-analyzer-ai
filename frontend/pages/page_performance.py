"""
Page 7 — Model Performance
=============================
Side-by-side comparison of Random Forest vs Logistic Regression.
Metrics table, confusion matrix heatmaps, ROC curves, cross-validation
scores, training time, feature importance, and learning curve.
"""
from __future__ import annotations

import numpy as np
import streamlit as st
import plotly.graph_objects as go

from frontend.components.charts import (
    confusion_matrix_heatmap,
    feature_importance_bar,
    roc_curve_plot,
)
from frontend.components.metrics_card import metric_card
from utils.config import (
    BACKGROUND_COLOR,
    BEARISH_COLOR,
    BULLISH_COLOR,
    CHART_TEMPLATE,
    MIN_ACCURACY_TARGET,
    PRIMARY_ACCENT,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def render_page() -> None:
    """Render the Model Performance page."""

    st.markdown(
        "<h2 style='color: #00D4AA;'>📈 Model Performance</h2>",
        unsafe_allow_html=True,
    )

    # Check if analysis has been run
    result = st.session_state.get("pipeline_result")
    pipeline = st.session_state.get("pipeline_instance")

    if result is None or pipeline is None:
        st.info(
            "📌 No model performance data available. Please run the analysis "
            "from the sidebar first."
        )
        return

    metrics = pipeline.evaluation_metrics

    if not metrics:
        st.info("Model evaluation metrics are not yet available. Please run the analysis.")
        return

    # ── Warning Banner if Below Target ────────────────────────────
    if metrics.get("rf_below_target") or metrics.get("lr_below_target"):
        st.warning(
            f"⚠️ One or more models have accuracy below the {MIN_ACCURACY_TARGET:.0%} target. "
            f"Consider retraining with more data or different hyperparameters."
        )

    st.markdown("---")

    # ── Side-by-Side Metrics Comparison ───────────────────────────
    st.subheader("📊 Model Comparison — Key Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "<h4 style='color: #00D4AA; text-align: center;'>🌲 Random Forest</h4>",
            unsafe_allow_html=True,
        )
        _render_metrics_cards(
            accuracy=metrics.get("rf_accuracy", 0),
            precision=metrics.get("rf_precision", 0),
            recall=metrics.get("rf_recall", 0),
            f1=metrics.get("rf_f1", 0),
            roc_auc=metrics.get("rf_roc_auc", 0),
        )

    with col2:
        st.markdown(
            "<h4 style='color: #636EFA; text-align: center;'>📐 Logistic Regression</h4>",
            unsafe_allow_html=True,
        )
        _render_metrics_cards(
            accuracy=metrics.get("lr_accuracy", 0),
            precision=metrics.get("lr_precision", 0),
            recall=metrics.get("lr_recall", 0),
            f1=metrics.get("lr_f1", 0),
            roc_auc=metrics.get("lr_roc_auc", 0),
        )

    st.markdown("---")

    # ── Metrics Table ─────────────────────────────────────────────
    st.subheader("📋 Detailed Metrics Table")

    import pandas as pd

    metrics_table = pd.DataFrame({
        "Metric": ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"],
        "Random Forest": [
            f"{metrics.get('rf_accuracy', 0):.4f}",
            f"{metrics.get('rf_precision', 0):.4f}",
            f"{metrics.get('rf_recall', 0):.4f}",
            f"{metrics.get('rf_f1', 0):.4f}",
            f"{metrics.get('rf_roc_auc', 0):.4f}",
        ],
        "Logistic Regression": [
            f"{metrics.get('lr_accuracy', 0):.4f}",
            f"{metrics.get('lr_precision', 0):.4f}",
            f"{metrics.get('lr_recall', 0):.4f}",
            f"{metrics.get('lr_f1', 0):.4f}",
            f"{metrics.get('lr_roc_auc', 0):.4f}",
        ],
    })

    st.dataframe(metrics_table, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Confusion Matrices (Side by Side) ─────────────────────────
    st.subheader("🎯 Confusion Matrices")

    col1, col2 = st.columns(2)

    with col1:
        rf_cm = metrics.get("rf_confusion_matrix")
        if rf_cm is not None:
            fig_rf_cm = confusion_matrix_heatmap(
                rf_cm, title="Random Forest Confusion Matrix"
            )
            st.plotly_chart(fig_rf_cm, use_container_width=True)

    with col2:
        lr_cm = metrics.get("lr_confusion_matrix")
        if lr_cm is not None:
            fig_lr_cm = confusion_matrix_heatmap(
                lr_cm, title="Logistic Regression Confusion Matrix"
            )
            st.plotly_chart(fig_lr_cm, use_container_width=True)

    st.markdown("---")

    # ── ROC Curves (Both Models on Same Axes) ─────────────────────
    st.subheader("📈 ROC Curves")

    if result.engineered_df is not None and not result.engineered_df.empty:
        try:
            from sklearn.metrics import roc_curve, roc_auc_score
            from utils.config import TEST_SIZE

            df = result.engineered_df.copy()
            exclude_cols = ["date", "target", "timestamp"]
            feature_cols = [
                c for c in df.columns
                if c not in exclude_cols
                and df[c].dtype in ["float64", "int64", "float32"]
            ]

            train_df = df.dropna(subset=["target"])
            X = train_df[feature_cols].values
            y = train_df["target"].values

            split_idx = int(len(X) * (1 - TEST_SIZE))
            X_test = X[split_idx:]
            y_test = y[split_idx:]

            fig_roc = go.Figure()

            # RF ROC
            if pipeline.rf_model.is_trained and len(y_test) > 0:
                rf_proba = pipeline.rf_model.predict_proba(X_test)[:, 1]
                fpr_rf, tpr_rf, _ = roc_curve(y_test, rf_proba)
                auc_rf = roc_auc_score(y_test, rf_proba)

                fig_roc.add_trace(go.Scatter(
                    x=fpr_rf, y=tpr_rf,
                    mode="lines",
                    name=f"Random Forest (AUC = {auc_rf:.4f})",
                    line=dict(color=PRIMARY_ACCENT, width=2),
                ))

            # LR ROC
            if pipeline.lr_model.is_trained and len(y_test) > 0:
                lr_proba = pipeline.lr_model.predict_proba(X_test)[:, 1]
                fpr_lr, tpr_lr, _ = roc_curve(y_test, lr_proba)
                auc_lr = roc_auc_score(y_test, lr_proba)

                fig_roc.add_trace(go.Scatter(
                    x=fpr_lr, y=tpr_lr,
                    mode="lines",
                    name=f"Logistic Regression (AUC = {auc_lr:.4f})",
                    line=dict(color="#636EFA", width=2),
                ))

            # Diagonal
            fig_roc.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                mode="lines",
                name="Random Classifier",
                line=dict(color="gray", width=1, dash="dash"),
            ))

            fig_roc.update_layout(
                title="ROC Curves — Model Comparison",
                xaxis_title="False Positive Rate",
                yaxis_title="True Positive Rate",
                template=CHART_TEMPLATE,
                paper_bgcolor=BACKGROUND_COLOR,
                plot_bgcolor=BACKGROUND_COLOR,
                height=450,
                legend=dict(x=0.5, y=0.05),
            )

            st.plotly_chart(fig_roc, use_container_width=True)
        except Exception as exc:
            st.info(f"ROC curves unavailable: {exc}")

    st.markdown("---")

    # ── Cross-Validation Scores Box Plot ──────────────────────────
    st.subheader("📦 Cross-Validation Scores")

    if result.engineered_df is not None and not result.engineered_df.empty:
        try:
            from utils.evaluator import ModelEvaluator
            from utils.config import TEST_SIZE

            evaluator = ModelEvaluator()

            df = result.engineered_df.copy()
            exclude_cols = ["date", "target", "timestamp"]
            feature_cols = [
                c for c in df.columns
                if c not in exclude_cols
                and df[c].dtype in ["float64", "int64", "float32"]
            ]
            train_df = df.dropna(subset=["target"])
            X = train_df[feature_cols].values
            y = train_df["target"].values

            if pipeline.rf_model.is_trained:
                cv_results = evaluator.cross_validate_model(
                    pipeline.rf_model.model, X, y
                )

                fig_cv = go.Figure()
                for metric_name, scores in cv_results.items():
                    fig_cv.add_trace(go.Box(
                        y=scores,
                        name=metric_name.capitalize(),
                        marker_color=PRIMARY_ACCENT,
                    ))

                fig_cv.update_layout(
                    title="Random Forest — Cross-Validation Scores (k=5)",
                    yaxis_title="Score",
                    template=CHART_TEMPLATE,
                    paper_bgcolor=BACKGROUND_COLOR,
                    plot_bgcolor=BACKGROUND_COLOR,
                    height=400,
                )
                st.plotly_chart(fig_cv, use_container_width=True)
        except Exception as exc:
            st.info(f"Cross-validation unavailable: {exc}")

    st.markdown("---")

    # ── Training Time Comparison ──────────────────────────────────
    st.subheader("⏱️ Training Time Comparison")

    rf_time = pipeline.rf_model.training_time if pipeline.rf_model.is_trained else 0
    lr_time = pipeline.lr_model.training_time if pipeline.lr_model.is_trained else 0

    fig_time = go.Figure(data=go.Bar(
        x=["Random Forest", "Logistic Regression"],
        y=[rf_time, lr_time],
        marker_color=[PRIMARY_ACCENT, "#636EFA"],
        text=[f"{rf_time:.2f}s", f"{lr_time:.2f}s"],
        textposition="auto",
    ))
    fig_time.update_layout(
        title="Training Time (seconds)",
        yaxis_title="Time (s)",
        template=CHART_TEMPLATE,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        height=350,
    )
    st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("---")

    # ── Feature Importance ────────────────────────────────────────
    st.subheader("🏆 Feature Importance (Random Forest)")

    if result.prediction and not result.prediction.feature_importance.empty:
        fig_imp = feature_importance_bar(result.prediction.feature_importance)
        st.plotly_chart(fig_imp, use_container_width=True)

    st.markdown("---")

    # ── Learning Curve ────────────────────────────────────────────
    st.subheader("📉 Learning Curve")

    if result.engineered_df is not None and not result.engineered_df.empty:
        try:
            from sklearn.model_selection import learning_curve, TimeSeriesSplit

            df = result.engineered_df.copy()
            exclude_cols = ["date", "target", "timestamp"]
            feature_cols = [
                c for c in df.columns
                if c not in exclude_cols
                and df[c].dtype in ["float64", "int64", "float32"]
            ]
            train_df = df.dropna(subset=["target"])
            X = train_df[feature_cols].values
            y = train_df["target"].values

            if pipeline.rf_model.is_trained and len(X) > 50:
                tscv = TimeSeriesSplit(n_splits=3)
                train_sizes, train_scores, val_scores = learning_curve(
                    pipeline.rf_model.model, X, y,
                    cv=tscv,
                    train_sizes=np.linspace(0.2, 1.0, 5),
                    scoring="accuracy",
                    n_jobs=-1,
                )

                fig_lc = go.Figure()

                fig_lc.add_trace(go.Scatter(
                    x=train_sizes, y=train_scores.mean(axis=1),
                    mode="lines+markers",
                    name="Training Score",
                    line=dict(color=PRIMARY_ACCENT, width=2),
                ))

                fig_lc.add_trace(go.Scatter(
                    x=train_sizes, y=val_scores.mean(axis=1),
                    mode="lines+markers",
                    name="Validation Score",
                    line=dict(color="#636EFA", width=2),
                ))

                fig_lc.update_layout(
                    title="Learning Curve — Training vs Validation",
                    xaxis_title="Training Set Size",
                    yaxis_title="Accuracy Score",
                    template=CHART_TEMPLATE,
                    paper_bgcolor=BACKGROUND_COLOR,
                    plot_bgcolor=BACKGROUND_COLOR,
                    height=400,
                )
                st.plotly_chart(fig_lc, use_container_width=True)
        except Exception as exc:
            st.info(f"Learning curve unavailable: {exc}")


def _render_metrics_cards(
    accuracy: float,
    precision: float,
    recall: float,
    f1: float,
    roc_auc: float,
) -> None:
    """Helper to render a column of metric cards."""
    target_color = BULLISH_COLOR if accuracy >= MIN_ACCURACY_TARGET else BEARISH_COLOR

    metric_card(title="Accuracy", value=f"{accuracy:.2%}",
                delta=f"Target: {MIN_ACCURACY_TARGET:.0%}",
                delta_color=target_color, icon="🎯")
    st.markdown("<br>", unsafe_allow_html=True)

    metric_card(title="Precision", value=f"{precision:.2%}", icon="📌")
    st.markdown("<br>", unsafe_allow_html=True)

    metric_card(title="Recall", value=f"{recall:.2%}", icon="🔍")
    st.markdown("<br>", unsafe_allow_html=True)

    metric_card(title="F1-Score", value=f"{f1:.2%}", icon="⚖️")
    st.markdown("<br>", unsafe_allow_html=True)

    metric_card(title="ROC-AUC", value=f"{roc_auc:.4f}", icon="📈")
