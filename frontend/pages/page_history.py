"""
Page 7 — Personal History
=========================
Displays the user's isolated prediction and recommendation history.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from services.db_service import DBService
from frontend.components.charts import prediction_history_line
from utils.logger import get_logger

logger = get_logger(__name__)

def render_page() -> None:
    """Render the Personal History dashboard."""
    st.markdown(
        "<h2 style='color: #00D4AA;'>📜 Personal History</h2>",
        unsafe_allow_html=True,
    )
    st.markdown("Review your past model predictions and system recommendations.")
    
    db = DBService()
    user_id = st.session_state.get("user_info", {}).get("id", 1)
    
    tab1, tab2 = st.tabs(["🔮 Prediction History", "💡 Recommendation Log"])
    
    # ── Prediction History ────────────────────────────
    with tab1:
        st.subheader("Model Predictions Over Time")
        history = db.get_prediction_history(user_id=user_id)

        if history:
            fig_history = prediction_history_line(history)
            st.plotly_chart(fig_history, use_container_width=True)
            
            # Show raw data
            with st.expander("View Raw Data"):
                st.dataframe(pd.DataFrame(history).drop(columns=["user_id"], errors="ignore"), use_container_width=True)
        else:
            st.info("No prediction history found. Run an analysis from the sidebar to start tracking!")

    # ── Recommendation History ────────────────────────────
    with tab2:
        st.subheader("Actionable Recommendations")
        rec_history = db.get_recommendation_history(user_id=user_id)

        if rec_history:
            history_df = pd.DataFrame(rec_history).drop(columns=["user_id"], errors="ignore")
            # Reorder for better display
            cols = ["timestamp", "symbol", "action", "confidence", "risk_level", "stop_loss", "take_profit"]
            cols = [c for c in cols if c in history_df.columns] + [c for c in history_df.columns if c not in cols]
            history_df = history_df[cols]
            
            st.dataframe(
                history_df.style.applymap(
                    lambda x: "color: #00D4AA; font-weight: bold;" if x == "BUY" else
                              ("color: #FF4444; font-weight: bold;" if x == "SELL" else
                               ("color: #FFD700; font-weight: bold;" if x == "HOLD" else "")),
                    subset=["action"]
                ),
                use_container_width=True
            )
        else:
            st.info("No recommendation history found. Run an analysis from the sidebar to start tracking!")
