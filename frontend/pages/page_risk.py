"""
Page 5 — Risk Classification
===============================
K-Means risk clustering results with 3D scatter plot, elbow method,
silhouette score, cluster centers, risk distribution, and historical timeline.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from frontend.components.charts import (
    cluster_scatter_3d,
    elbow_plot,
    risk_distribution_pie,
)
from frontend.components.metrics_card import metric_card, risk_badge
from utils.config import (
    CLUSTERING_FEATURES,
    RISK_COLORS,
    CHART_TEMPLATE,
    BACKGROUND_COLOR,
    PRIMARY_ACCENT,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def render_page() -> None:
    """Render the Risk Classification page."""

    st.markdown(
        "<h2 style='color: #00D4AA;'>⚠️ Risk Classification</h2>",
        unsafe_allow_html=True,
    )

    # Check if analysis has been run
    result = st.session_state.get("pipeline_result")

    if result is None or result.risk is None:
        st.info(
            "📌 No risk classification available. Please run the analysis "
            "from the sidebar first."
        )
        return

    risk = result.risk

    # ── Risk Level Display ────────────────────────────────────────
    st.markdown("---")

    risk_badge(risk.risk_level)

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card(
            title="Current Risk Level",
            value=risk.risk_level,
            icon="⚠️",
        )

    with col2:
        metric_card(
            title="Silhouette Score",
            value=f"{risk.silhouette_score:.4f}",
            delta="Good" if risk.silhouette_score > 0.4 else "Weak",
            delta_color=PRIMARY_ACCENT if risk.silhouette_score > 0.4 else "#FF4444",
            icon="📐",
        )

    with col3:
        metric_card(
            title="Clusters Used",
            value="3",
            icon="📊",
        )

    st.markdown("---")

    # ── 3D Cluster Visualization ──────────────────────────────────
    st.subheader("🌐 K-Means Cluster Visualization (3D)")

    if result.engineered_df is not None and not result.engineered_df.empty:
        df = result.engineered_df.copy()

        # Add risk labels to the dataframe
        from models.kmeans_clustering import KMeansRiskClassifier

        pipeline = st.session_state.get("pipeline_instance")
        if pipeline and pipeline.kmeans.is_fitted:
            try:
                risk_labels = pipeline.kmeans.predict_risk(df)
                df["risk_level"] = risk_labels.values
            except Exception:
                df["risk_level"] = "Unknown"

        fig_3d = cluster_scatter_3d(df, title="Market Conditions by Risk Cluster")
        st.plotly_chart(fig_3d, use_container_width=True)
    else:
        st.info("3D visualization requires engineered feature data.")

    st.markdown("---")

    # ── Elbow Method ──────────────────────────────────────────────
    st.subheader("📉 Elbow Method — Optimal k Selection")

    col1, col2 = st.columns([2, 1])

    with col1:
        if risk.inertias:
            fig_elbow = elbow_plot(risk.inertias)
            st.plotly_chart(fig_elbow, use_container_width=True)
        else:
            st.info("Elbow plot data not available.")

    with col2:
        st.markdown(
            """
            <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid #333; border-radius: 12px;
                        padding: 20px; margin-top: 20px;'>
                <h4 style='color: #00D4AA;'>How to Read</h4>
                <p style='color: #aaa; font-size: 0.85em; line-height: 1.6;'>
                    The <strong>elbow point</strong> is where the curve bends sharply,
                    indicating the optimal number of clusters. Beyond this point,
                    adding more clusters doesn't significantly reduce inertia.
                </p>
                <p style='color: #aaa; font-size: 0.85em; line-height: 1.6;'>
                    We use <strong>k=3</strong> to map to Low, Medium, and High
                    risk categories.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Silhouette Score Display ──────────────────────────────────
    st.subheader("📐 Clustering Quality — Silhouette Score")

    import plotly.graph_objects as go

    fig_sil = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk.silhouette_score,
        number={"font": {"size": 36}},
        gauge=dict(
            axis=dict(range=[0, 1]),
            bar=dict(color=PRIMARY_ACCENT),
            bgcolor=BACKGROUND_COLOR,
            borderwidth=2,
            bordercolor="#333",
            steps=[
                dict(range=[0, 0.25], color="#FF4444"),
                dict(range=[0.25, 0.5], color="#FFD700"),
                dict(range=[0.5, 0.75], color="#00D4AA"),
                dict(range=[0.75, 1], color="#00FF88"),
            ],
        ),
        title=dict(text="Silhouette Score", font=dict(size=16)),
    ))
    fig_sil.update_layout(
        template=CHART_TEMPLATE,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        height=300,
    )
    st.plotly_chart(fig_sil, use_container_width=True)

    st.markdown("---")

    # ── Cluster Centers Table ─────────────────────────────────────
    st.subheader("📋 Cluster Centers")

    if not risk.cluster_centers.empty:
        st.dataframe(
            risk.cluster_centers.style.format("{:.4f}", subset=[
                c for c in risk.cluster_centers.columns if c != "risk_label"
            ]).set_properties(**{
                "background-color": "#1a1a2e",
                "color": "#fff",
            }),
            use_container_width=True,
        )
    else:
        st.info("Cluster centers not available.")

    st.markdown("---")

    # ── Risk Distribution Pie ─────────────────────────────────────
    st.subheader("🥧 Risk Distribution")

    col1, col2 = st.columns([2, 1])

    with col1:
        if risk.risk_distribution:
            fig_pie = risk_distribution_pie(risk.risk_distribution)
            st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        if risk.risk_distribution:
            st.markdown("**Distribution Summary:**")
            for label, count in risk.risk_distribution.items():
                color = RISK_COLORS.get(label, "#888")
                st.markdown(
                    f"<span style='color: {color}; font-weight: 600;'>"
                    f"● {label}</span>: {count} periods",
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # ── Historical Risk Timeline ──────────────────────────────────
    st.subheader("📈 Historical Risk Level Timeline")

    if result.engineered_df is not None and not result.engineered_df.empty:
        pipeline = st.session_state.get("pipeline_instance")
        if pipeline and pipeline.kmeans.is_fitted:
            try:
                df = result.engineered_df.copy()
                risk_labels = pipeline.kmeans.predict_risk(df)

                risk_numeric = risk_labels.map({"Low": 1, "Medium": 2, "High": 3})

                fig_timeline = go.Figure()
                fig_timeline.add_trace(go.Scatter(
                    x=df["date"] if "date" in df.columns else list(range(len(risk_numeric))),
                    y=risk_numeric,
                    mode="lines",
                    line=dict(color=PRIMARY_ACCENT, width=1.5),
                    name="Risk Level",
                ))

                fig_timeline.update_layout(
                    title="Risk Level Over Time",
                    yaxis=dict(
                        tickvals=[1, 2, 3],
                        ticktext=["Low", "Medium", "High"],
                    ),
                    template=CHART_TEMPLATE,
                    paper_bgcolor=BACKGROUND_COLOR,
                    plot_bgcolor=BACKGROUND_COLOR,
                    height=350,
                )

                st.plotly_chart(fig_timeline, use_container_width=True)
            except Exception as exc:
                st.info(f"Risk timeline unavailable: {exc}")
