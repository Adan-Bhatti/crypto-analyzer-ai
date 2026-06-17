"""
Page 4 — Prediction Dashboard
================================
ML prediction results, probability gauge, RF vs LR comparison,
feature importance, prediction confidence timeline, and direction arrow.
"""
from __future__ import annotations

import streamlit as st
import numpy as np

from frontend.components.charts import (
    feature_importance_bar,
    prediction_history_line,
    probability_gauge,
)
from frontend.components.metrics_card import metric_card
from utils.config import PRIMARY_ACCENT, BEARISH_COLOR, BULLISH_COLOR
from utils.helpers import format_percentage
from utils.logger import get_logger

logger = get_logger(__name__)


def render_page() -> None:
    """Render the Prediction Dashboard page."""

    st.markdown(
        "<h2 style='color: #00D4AA;'>🔮 Prediction Dashboard</h2>",
        unsafe_allow_html=True,
    )

    # Check if analysis has been run
    result = st.session_state.get("pipeline_result")

    if result is None or result.prediction is None:
        st.info(
            "📌 No predictions available yet. Please run the analysis "
            "from the sidebar first."
        )

        # Manual prediction button
        if st.button("🚀 Run Prediction", type="primary", key="pred_run_btn"):
            st.warning("Please use the sidebar 'Run Analysis' button to load data and train models first.")

        return

    prediction = result.prediction

    # ── Prediction Result Card ────────────────────────────────────
    st.markdown("---")

    direction = "BULLISH" if prediction.prediction == 1 else "BEARISH"
    dir_color = BULLISH_COLOR if prediction.prediction == 1 else BEARISH_COLOR
    dir_icon = "↑" if prediction.prediction == 1 else "↓"

    st.markdown(
        f"""
        <div style='text-align: center; padding: 20px;'>
            <div style='font-size: 4em; color: {dir_color};'>{dir_icon}</div>
            <div style='font-size: 2.5em; font-weight: 800; color: {dir_color};'>
                {direction}
            </div>
            <div style='color: #aaa; margin-top: 8px; font-size: 1.1em;'>
                Next-period price direction prediction
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Probability Gauge ─────────────────────────────────────────
    st.subheader(
        "📊 Prediction Probability",
        help="The XGBoost model's calculated probability that the next trading period will close higher (Bullish) or lower (Bearish)."
    )

    col1, col2 = st.columns(2)

    with col1:
        fig_gauge = probability_gauge(
            prediction.bullish_prob,
            title="Bullish Probability",
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        # Probability summary metrics
        st.markdown("<br>", unsafe_allow_html=True)

        metric_card(
            title="Bullish Probability",
            value=f"{prediction.bullish_prob:.1%}",
            icon="🟢",
        )
        st.markdown("<br>", unsafe_allow_html=True)

        metric_card(
            title="Bearish Probability",
            value=f"{prediction.bearish_prob:.1%}",
            icon="🔴",
        )

    st.markdown("---")

    # ── RF vs LR Comparison ───────────────────────────────────────
    st.subheader(
        "⚔️ Model Comparison: Random Forest vs Logistic Regression",
        help="Compares the predictions of our complex ensemble model (Random Forest) against the linear baseline model (Logistic Regression)."
    )

    import plotly.graph_objects as go
    from utils.config import CHART_TEMPLATE, BACKGROUND_COLOR

    col1, col2 = st.columns(2)

    with col1:
        rf_dir = "Bullish" if prediction.rf_prediction == 1 else "Bearish"
        rf_color = BULLISH_COLOR if prediction.rf_prediction == 1 else BEARISH_COLOR
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid {rf_color}; border-radius: 12px;
                        padding: 20px; text-align: center;'>
                <h4 style='color: #00D4AA;'>🌲 Random Forest</h4>
                <div style='font-size: 1.8em; font-weight: 700; color: {rf_color};'>
                    {rf_dir}
                </div>
                <div style='color: #aaa; margin-top: 8px;'>
                    Bull: {prediction.rf_proba[1]:.1%} | Bear: {prediction.rf_proba[0]:.1%}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        lr_dir = "Bullish" if prediction.lr_prediction == 1 else "Bearish"
        lr_color = BULLISH_COLOR if prediction.lr_prediction == 1 else BEARISH_COLOR
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid {lr_color}; border-radius: 12px;
                        padding: 20px; text-align: center;'>
                <h4 style='color: #636EFA;'>📐 Logistic Regression</h4>
                <div style='font-size: 1.8em; font-weight: 700; color: {lr_color};'>
                    {lr_dir}
                </div>
                <div style='color: #aaa; margin-top: 8px;'>
                    Bull: {prediction.lr_proba[1]:.1%} | Bear: {prediction.lr_proba[0]:.1%}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Probability comparison bar chart
    st.markdown("<br>", unsafe_allow_html=True)

    fig_compare = go.Figure()
    fig_compare.add_trace(go.Bar(
        name="Random Forest",
        x=["Bearish", "Bullish"],
        y=[prediction.rf_proba[0] * 100, prediction.rf_proba[1] * 100],
        marker_color=PRIMARY_ACCENT,
    ))
    fig_compare.add_trace(go.Bar(
        name="Logistic Regression",
        x=["Bearish", "Bullish"],
        y=[prediction.lr_proba[0] * 100, prediction.lr_proba[1] * 100],
        marker_color="#636EFA",
    ))
    fig_compare.update_layout(
        title="Prediction Probability Comparison",
        yaxis_title="Probability (%)",
        barmode="group",
        template=CHART_TEMPLATE,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        height=400,
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    st.markdown("---")

    # ── Feature Importance ────────────────────────────────────────
    st.subheader(
        "🏆 Feature Importance (Top 15)",
        help="Shows which mathematical indicators (like RSI, MACD, or Moving Averages) the XGBoost model relied on most heavily to make this specific prediction."
    )

    if not prediction.feature_importance.empty:
        fig_imp = feature_importance_bar(prediction.feature_importance, top_n=15)
        st.plotly_chart(fig_imp, use_container_width=True)
    else:
        st.info("Feature importance data not available.")

    st.markdown("---")

    # ── Decision Boundary Visualization (2D PCA) ──────────────────
    st.subheader(
        "🎯 Decision Space (2D PCA)",
        help="Principal Component Analysis (PCA) maps our 34-dimensional feature space down to 2 dimensions to visualize how clearly the model can separate Bullish (Green) and Bearish (Red) market conditions."
    )

    if result.engineered_df is not None and not result.engineered_df.empty:
        try:
            from sklearn.decomposition import PCA

            exclude_cols = ["date", "target", "timestamp"]
            feature_cols = [
                c for c in result.engineered_df.columns
                if c not in exclude_cols
                and result.engineered_df[c].dtype in ["float64", "int64", "float32"]
            ]

            train_df = result.engineered_df.dropna(subset=["target"])
            if len(train_df) > 10 and len(feature_cols) >= 2:
                X = train_df[feature_cols].values
                y = train_df["target"].values

                pca = PCA(n_components=2)
                X_pca = pca.fit_transform(X)

                fig_pca = go.Figure()
                for label, name, color in [
                    (0, "Bearish", BEARISH_COLOR),
                    (1, "Bullish", BULLISH_COLOR),
                ]:
                    mask = y == label
                    fig_pca.add_trace(go.Scatter(
                        x=X_pca[mask, 0], y=X_pca[mask, 1],
                        mode="markers",
                        marker=dict(color=color, size=5, opacity=0.6),
                        name=name,
                    ))

                fig_pca.update_layout(
                    title=f"PCA Decision Space (Explained Variance: "
                          f"{sum(pca.explained_variance_ratio_):.1%})",
                    xaxis_title="PC1",
                    yaxis_title="PC2",
                    template=CHART_TEMPLATE,
                    paper_bgcolor=BACKGROUND_COLOR,
                    plot_bgcolor=BACKGROUND_COLOR,
                    height=450,
                )
                st.plotly_chart(fig_pca, use_container_width=True)
        except Exception as exc:
            st.info(f"PCA visualization unavailable: {exc}")

    # ── Disclaimer ────────────────────────────────────────────────
    st.caption(
        "⚠️ **Disclaimer:** Predictions are for educational purposes only. "
        "The model predicts next-period price *direction* (up/down), not exact price. "
        "This is not financial advice."
    )
