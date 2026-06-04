"""
Page 3 — Historical Analysis
===============================
OHLCV charts, moving average overlays, RSI, MACD, Bollinger Bands,
correlation heatmap, price distribution, and volume analysis.
"""
from __future__ import annotations

import numpy as np
import streamlit as st

from frontend.components.charts import (
    bollinger_chart,
    candlestick_chart,
    correlation_heatmap,
    line_chart_with_ma,
    macd_chart,
    rsi_chart,
    volume_bar_chart,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def render_page() -> None:
    """Render the Historical Analysis page."""

    st.markdown(
        "<h2 style='color: #00D4AA;'>📊 Historical Analysis</h2>",
        unsafe_allow_html=True,
    )

    # Check if data is available
    result = st.session_state.get("pipeline_result")

    if result is None or result.engineered_df.empty:
        st.info(
            "📌 No data loaded yet. Please select a cryptocurrency and click "
            "'Run Analysis' in the sidebar to load historical data."
        )
        return

    df = result.engineered_df.copy()

    # ── Date Range Selector ───────────────────────────────────────
    st.subheader("📅 Date Range")

    if "date" in df.columns:
        col1, col2 = st.columns(2)
        min_date = df["date"].min()
        max_date = df["date"].max()

        # Convert to date objects for the date input widgets
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=min_date.date() if hasattr(min_date, "date") else min_date,
                key="hist_start_date",
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=max_date.date() if hasattr(max_date, "date") else max_date,
                key="hist_end_date",
            )

        # Filter by date range
        import pandas as pd
        start_ts = pd.Timestamp(start_date, tz="UTC")
        end_ts = pd.Timestamp(end_date, tz="UTC")
        df = df[(df["date"] >= start_ts) & (df["date"] <= end_ts)]

    st.markdown("---")

    # ── OHLCV Candlestick Chart ───────────────────────────────────
    st.subheader("🕯️ OHLCV Candlestick Chart")
    fig = candlestick_chart(df, title="Historical OHLCV")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Moving Averages Overlay ───────────────────────────────────
    st.subheader("📈 Moving Averages")

    ma_options = {
        "SMA 7": "sma_7",
        "SMA 14": "sma_14",
        "SMA 21": "sma_21",
        "EMA 12": "ema_12",
        "EMA 26": "ema_26",
    }

    # Filter to only show available MAs
    available_mas = {k: v for k, v in ma_options.items() if v in df.columns}

    selected_ma_labels = st.multiselect(
        "Select Moving Averages to Overlay",
        list(available_mas.keys()),
        default=list(available_mas.keys())[:3],
        key="hist_ma_select",
    )

    selected_ma_cols = [available_mas[label] for label in selected_ma_labels]

    fig_ma = line_chart_with_ma(df, mas=selected_ma_cols, title="Price with Moving Averages")
    st.plotly_chart(fig_ma, use_container_width=True)

    st.markdown("---")

    # ── RSI Chart ─────────────────────────────────────────────────
    st.subheader("📉 RSI (Relative Strength Index)")

    fig_rsi = rsi_chart(df)
    st.plotly_chart(fig_rsi, use_container_width=True)

    # RSI interpretation helper
    if "rsi_14" in df.columns:
        latest_rsi = df["rsi_14"].iloc[-1]
        if latest_rsi > 70:
            st.warning(f"⚠️ RSI = {latest_rsi:.1f} — **Overbought** territory. Price may pull back.")
        elif latest_rsi < 30:
            st.success(f"✅ RSI = {latest_rsi:.1f} — **Oversold** territory. Potential buying opportunity.")
        else:
            st.info(f"ℹ️ RSI = {latest_rsi:.1f} — Neutral range.")

    st.markdown("---")

    # ── MACD Chart ────────────────────────────────────────────────
    st.subheader("📊 MACD (Moving Average Convergence Divergence)")

    fig_macd = macd_chart(df)
    st.plotly_chart(fig_macd, use_container_width=True)

    st.markdown("---")

    # ── Bollinger Bands ───────────────────────────────────────────
    st.subheader("📐 Bollinger Bands")

    fig_bb = bollinger_chart(df)
    st.plotly_chart(fig_bb, use_container_width=True)

    st.markdown("---")

    # ── Correlation Heatmap ───────────────────────────────────────
    st.subheader("🔥 Feature Correlation Matrix")

    # Select only relevant numeric columns for the heatmap
    feature_cols = [c for c in df.select_dtypes(include=[np.number]).columns
                    if c not in ["target"]]
    if feature_cols:
        fig_corr = correlation_heatmap(df[feature_cols])
        st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("---")

    # ── Price Distribution ────────────────────────────────────────
    st.subheader("📊 Price Distribution")

    import plotly.graph_objects as go
    from utils.config import CHART_TEMPLATE, BACKGROUND_COLOR, PRIMARY_ACCENT

    if "close" in df.columns:
        fig_hist = go.Figure(data=go.Histogram(
            x=df["close"],
            nbinsx=50,
            marker_color=PRIMARY_ACCENT,
            opacity=0.7,
        ))
        fig_hist.update_layout(
            title="Close Price Distribution",
            xaxis_title="Price",
            yaxis_title="Frequency",
            template=CHART_TEMPLATE,
            paper_bgcolor=BACKGROUND_COLOR,
            plot_bgcolor=BACKGROUND_COLOR,
            height=350,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    # ── Volume Analysis ───────────────────────────────────────────
    st.subheader("📦 Volume Analysis")

    fig_vol = volume_bar_chart(df, title="Trading Volume Over Time")
    st.plotly_chart(fig_vol, use_container_width=True)
