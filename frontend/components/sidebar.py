"""
Sidebar Component
==================
Provides the shared sidebar controls used across all dashboard pages:
  - Cryptocurrency coin selector
  - Data source toggle (API vs CSV upload)
  - CSV file uploader
  - Analysis controls (Run Analysis button, Retrain toggle)
"""
from __future__ import annotations

import streamlit as st

from utils.config import COIN_DISPLAY_NAMES, SUPPORTED_COINS


def render_sidebar() -> dict:
    """
    Render the sidebar controls and return the selected configuration.

    Returns:
        Dictionary with keys:
          - ``symbol``: Selected Binance symbol string.
          - ``data_source``: ``"api"`` or ``"csv"``.
          - ``csv_file``: Uploaded file object or None.
          - ``retrain``: Boolean — whether to force model retraining.
          - ``run_analysis``: Boolean — whether the user clicked "Run Analysis".
    """
    with st.sidebar:
        # --- Header ---
        st.markdown(
            """
            <div style='background: linear-gradient(135deg, #16213e, #0a0a1a); padding: 20px; border-radius: 15px; border: 1px solid rgba(0, 212, 170, 0.2); text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);'>
                <div style='font-size: 2.5rem; margin-bottom: 5px;'>📊</div>
                <h2 style='color: #00D4AA; margin: 0; font-family: "Inter", sans-serif; font-weight: 700; letter-spacing: -0.5px;'>CryptoAI</h2>
                <p style='color: #8892B0; font-size: 0.85em; margin-top: 5px; font-weight: 500;'>Market & Risk Intelligence</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --- Coin Selector ---
        st.subheader("🪙 Select Cryptocurrency")

        # Format display names for the selectbox
        display_names = [COIN_DISPLAY_NAMES.get(c, c) for c in SUPPORTED_COINS]
        selected_idx = st.selectbox(
            "Coin",
            range(len(SUPPORTED_COINS)),
            format_func=lambda i: display_names[i],
            key="sidebar_coin_selector",
            label_visibility="collapsed",
        )
        selected_symbol = SUPPORTED_COINS[selected_idx]

        st.markdown("---")

        # --- Data Source ---
        st.subheader("📂 Data Source")
        data_source = st.radio(
            "Source",
            options=["api", "csv"],
            format_func=lambda x: "🌐 Live API (Binance/Yahoo)" if x == "api" else "📄 Upload CSV",
            key="sidebar_data_source",
            label_visibility="collapsed",
        )

        # CSV uploader (only shown when CSV is selected)
        csv_file = None
        if data_source == "csv":
            csv_file = st.file_uploader(
                "Upload CSV file",
                type=["csv"],
                key="sidebar_csv_upload",
                help="Upload a CSV with columns: Date, Open, High, Low, Close, Volume",
            )

        st.markdown("---")

        # --- Analysis Controls ---
        st.subheader("⚙️ Analysis Controls")

        retrain = st.checkbox(
            "Force model retraining",
            value=False,
            key="sidebar_retrain",
            help="Re-train models from scratch instead of using saved ones.",
        )

        run_analysis = st.button(
            "🚀 Run Analysis",
            key="sidebar_run_analysis",
            use_container_width=True,
            type="primary",
        )

        st.markdown("---")

        # --- Status Info ---
        st.subheader("📊 Status")

        if "pipeline_result" in st.session_state and st.session_state["pipeline_result"]:
            result = st.session_state["pipeline_result"]
            if hasattr(result, 'raw_df') and not result.raw_df.empty:
                st.success(f"✅ Data loaded: {len(result.raw_df)} rows")
            if hasattr(result, 'prediction') and result.prediction:
                direction = "🟢 Bullish" if result.prediction.prediction == 1 else "🔴 Bearish"
                st.info(f"Prediction: {direction}")
            if hasattr(result, 'risk') and result.risk:
                st.info(f"Risk: {result.risk.risk_level}")
        else:
            st.caption("No analysis run yet. Click 'Run Analysis' to start.")

        # --- Disclaimer ---
        st.markdown("---")
        st.caption(
            "⚠️ **Disclaimer:** This tool is for educational purposes only. "
            "Not financial advice."
        )

    return {
        "symbol": selected_symbol,
        "data_source": data_source,
        "csv_file": csv_file,
        "retrain": retrain,
        "run_analysis": run_analysis,
    }
