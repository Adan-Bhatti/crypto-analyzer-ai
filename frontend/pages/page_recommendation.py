"""
Page 6 — Buy/Sell/Hold Recommendation Engine
===============================================
Large action badge, confidence display, reasoning, entry/stop-loss/take-profit,
historical recommendation log, and disclaimer.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend.components.metrics_card import action_badge, metric_card
from utils.helpers import format_price
from utils.logger import get_logger

logger = get_logger(__name__)


def render_page() -> None:
    """Render the Buy/Sell/Hold Recommendation Engine page."""

    st.markdown(
        "<h2 style='color: #00D4AA;'>💡 Buy/Sell/Hold Recommendation Engine</h2>",
        unsafe_allow_html=True,
    )

    # Check if analysis has been run
    result = st.session_state.get("pipeline_result")

    if result is None or result.recommendation is None:
        st.info(
            "📌 No recommendation available. Please run the analysis "
            "from the sidebar first."
        )
        return

    rec = result.recommendation

    st.markdown("---")

    # ── Large Action Badge ────────────────────────────────────────
    action_badge(rec.action, rec.confidence, size="large")

    st.markdown("---")

    # ── Confidence & Input Summary ────────────────────────────────
    st.subheader("📊 Analysis Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            title="Bullish Probability",
            value=f"{rec.bullish_prob:.1%}",
            icon="🟢",
        )

    with col2:
        metric_card(
            title="Bearish Probability",
            value=f"{rec.bearish_prob:.1%}",
            icon="🔴",
        )

    with col3:
        metric_card(
            title="Risk Level",
            value=rec.risk_level,
            icon="⚠️",
        )

    with col4:
        metric_card(
            title="Confidence",
            value=rec.confidence,
            icon="🎯",
        )

    st.markdown("---")

    # ── Reasoning ─────────────────────────────────────────────────
    st.subheader("🧠 Decision Reasoning")

    for i, reason in enumerate(rec.reasoning, 1):
        st.markdown(
            f"""
            <div style='background: #1a1a2e; border-left: 3px solid #00D4AA;
                        padding: 10px 16px; margin: 8px 0; border-radius: 0 8px 8px 0;'>
                <span style='color: #00D4AA; font-weight: 600;'>{i}.</span>
                <span style='color: #ccc;'> {reason}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Price Levels ──────────────────────────────────────────────
    st.subheader("💰 Trading Levels")

    col1, col2, col3 = st.columns(3)

    # Get current price from the data
    current_price = 0.0
    if result.engineered_df is not None and not result.engineered_df.empty:
        current_price = float(result.engineered_df["close"].iloc[-1])

    with col1:
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid #636EFA; border-radius: 12px;
                        padding: 20px; text-align: center;'>
                <div style='color: #888; font-size: 0.85em; text-transform: uppercase;'>
                    Entry Price
                </div>
                <div style='font-size: 1.5em; font-weight: 700; color: #FFF; margin-top: 8px;'>
                    {format_price(current_price)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid #FF4444; border-radius: 12px;
                        padding: 20px; text-align: center;'>
                <div style='color: #888; font-size: 0.85em; text-transform: uppercase;'>
                    Suggested Stop-Loss
                </div>
                <div style='font-size: 1.5em; font-weight: 700; color: #FF4444; margin-top: 8px;'>
                    {format_price(rec.suggested_stop_loss)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid #00D4AA; border-radius: 12px;
                        padding: 20px; text-align: center;'>
                <div style='color: #888; font-size: 0.85em; text-transform: uppercase;'>
                    Suggested Take-Profit
                </div>
                <div style='font-size: 1.5em; font-weight: 700; color: #00D4AA; margin-top: 8px;'>
                    {format_price(rec.suggested_take_profit)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Historical Recommendation Log ─────────────────────────────
    st.subheader("📜 Recommendation History")

    from services.db_service import DBService
    db = DBService()
    user_id = st.session_state.get("user_info", {}).get("id", 1)
    rec_history = db.get_recommendation_history(user_id=user_id)

    if rec_history:
        history_df = pd.DataFrame(rec_history)

        # Style the action column with colors
        st.dataframe(
            history_df,
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.TextColumn("Timestamp"),
                "action": st.column_config.TextColumn("Action"),
                "confidence": st.column_config.TextColumn("Confidence"),
                "bullish_prob": st.column_config.NumberColumn("Bull %", format="%.1f%%"),
                "bearish_prob": st.column_config.NumberColumn("Bear %", format="%.1f%%"),
                "risk_level": st.column_config.TextColumn("Risk"),
                "stop_loss": st.column_config.NumberColumn("Stop-Loss", format="$%.2f"),
                "take_profit": st.column_config.NumberColumn("Take-Profit", format="$%.2f"),
            },
        )
    else:
        st.info("No recommendation history yet. Run multiple analyses to build history.")

    st.markdown("---")

    # ── Disclaimer ────────────────────────────────────────────────
    st.markdown(
        """
        <div style='background: rgba(255, 68, 68, 0.1); border: 1px solid #FF4444;
                    border-radius: 12px; padding: 20px; text-align: center;'>
            <h4 style='color: #FF4444;'>⚠️ Important Disclaimer</h4>
            <p style='color: #ccc; line-height: 1.6;'>
                This tool is for <strong>educational and research purposes only</strong>.
                The Buy/Sell/Hold recommendations are generated by machine learning models
                and a rule-based agent. They do <strong>not</strong> constitute financial advice.
                <br><br>
                Always conduct your own research and consult a qualified financial advisor
                before making any investment decisions. Cryptocurrency markets are highly
                volatile and you may lose your entire investment.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
