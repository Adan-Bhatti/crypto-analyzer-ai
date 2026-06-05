"""
Page 1 — Project Overview
===========================
Hero section, system architecture, technology stack, AI techniques,
live project stats, and "How it works" step-by-step flow.
"""
from __future__ import annotations

import streamlit as st


def render_page() -> None:
    """Render the Project Overview page."""

    # ── Hero Section ──────────────────────────────────────────────
    st.markdown(
        """
        <div style='text-align: center; padding: 40px 0 20px 0;'>
            <h1 style='font-size: 2.5em; color: #00D4AA; margin-bottom: 8px;'>
                📈 AI-Based Cryptocurrency Market Behavior Analyzer
            </h1>
            <h3 style='color: #aaa; font-weight: 400; margin-top: 0;'>
                & Risk Predictor
            </h3>
            <p style='color: #888; max-width: 700px; margin: 16px auto; line-height: 1.7;'>
                A comprehensive AI-powered dashboard that analyzes cryptocurrency market
                behavior using Machine Learning (Random Forest, Logistic Regression),
                K-Means Clustering for risk classification, and an Intelligent Agent
                for actionable Buy/Sell/Hold recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── System Architecture ───────────────────────────────────────
    st.subheader("🏗️ System Architecture")

    st.markdown(
        """
        ```
        ┌─────────────────────────────────────────────────────────────┐
        │                    STREAMLIT FRONTEND                       │
        │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
        │  │ Overview  │ │  Live    │ │Historical│ │Prediction│      │
        │  │  Page     │ │ Market   │ │ Analysis │ │Dashboard │      │
        │  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
        │  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
        │  │   Risk   │ │ Buy/Sell │ │  Model   │                   │
        │  │ Classify │ │  /Hold   │ │  Perf.   │                   │
        │  └──────────┘ └──────────┘ └──────────┘                   │
        ├─────────────────────────────────────────────────────────────┤
        │                BACKEND ORCHESTRATOR                         │
        │              ┌──────────────────┐                          │
        │              │  CryptoPipeline  │                          │
        │              └────────┬─────────┘                          │
        │         ┌─────────────┼─────────────┐                      │
        │    ┌────▼────┐  ┌────▼─────┐  ┌────▼──────┐               │
        │    │  Data   │  │  Models  │  │   Agent   │               │
        │    │  Layer  │  │  Layer   │  │   Layer   │               │
        │    └────┬────┘  └────┬─────┘  └───────────┘               │
        │    ┌────▼────┐  ┌────▼─────┐                               │
        │    │ Loader  │  │   RF     │                               │
        │    │ Cleaner │  │   LR     │                               │
        │    │ Features│  │  K-Means │                               │
        │    └────┬────┘  └──────────┘                               │
        ├─────────┼───────────────────────────────────────────────────┤
        │    ┌────▼────────────────────┐                              │
        │    │    SERVICES LAYER       │                              │
        │    │  Binance API → Yahoo    │                              │
        │    │    Finance Fallback     │                              │
        │    └─────────────────────────┘                              │
        └─────────────────────────────────────────────────────────────┘
        ```
        """,
    )

    st.markdown("---")

    # ── Technology Stack ──────────────────────────────────────────
    st.subheader("💻 Technology Stack")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            | Category | Technology |
            |----------|-----------|
            | **Language** | Python 3.10+ |
            | **Frontend** | Streamlit |
            | **ML Framework** | Scikit-learn |
            | **Data** | Pandas, NumPy |
            | **Visualization** | Plotly |
            """
        )

    with col2:
        st.markdown(
            """
            | Category | Technology |
            |----------|-----------|
            | **Technical Indicators** | ta (TA-Lib) |
            | **Live Data (Primary)** | Binance REST API |
            | **Live Data (Fallback)** | Yahoo Finance |
            | **Model Persistence** | Joblib |
            | **Logging** | Python logging |
            """
        )

    st.markdown("---")

    # ── AI Techniques ─────────────────────────────────────────────
    st.subheader("🧠 AI Techniques Used")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid #00D4AA; border-radius: 12px;
                        padding: 20px; text-align: center; height: 220px;'>
                <h4 style='color: #00D4AA;'>🌲 Random Forest + LR</h4>
                <p style='color: #ccc; font-size: 0.85em;'>
                    Ensemble classification (RF) with Logistic Regression baseline.
                    Predicts next-period price direction (Bullish/Bearish).
                    GridSearchCV + TimeSeriesSplit for reliable validation.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid #FFD700; border-radius: 12px;
                        padding: 20px; text-align: center; height: 220px;'>
                <h4 style='color: #FFD700;'>📊 K-Means Clustering</h4>
                <p style='color: #ccc; font-size: 0.85em;'>
                    Unsupervised clustering of market conditions into
                    Low / Medium / High risk categories based on
                    volatility, RSI, and volume features.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid #636EFA; border-radius: 12px;
                        padding: 20px; text-align: center; height: 220px;'>
                <h4 style='color: #636EFA;'>🤖 Intelligent Agent</h4>
                <p style='color: #ccc; font-size: 0.85em;'>
                    Rule-based agent that synthesizes ML predictions
                    and risk levels into BUY / HOLD / SELL
                    recommendations with confidence scoring.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Live Project Stats ────────────────────────────────────────
    st.subheader("📊 Live Project Stats")

    result = st.session_state.get("pipeline_result")
    
    from pathlib import Path

    # 1. Count Total Data Points from saved CSVs
    data_points = 0
    try:
        csv_files = list(Path("data/datasets").glob("*.csv"))
        for f in csv_files:
            with open(f, 'r', encoding='utf-8') as file:
                data_points += sum(1 for _ in file) - 1
    except Exception:
        pass

    # Fallback to session state if no local CSVs are found
    if data_points <= 0:
        if result and hasattr(result, "raw_df") and not result.raw_df.empty:
            data_points = len(result.raw_df)

    # 2. Features Engineered is fixed at 36 by the feature engineer module
    features = 36

    # 3. Count Models Trained from the saved directory
    try:
        saved_models = list(Path("models/saved").glob("*.joblib"))
        models_trained = len(saved_models)
    except Exception:
        models_trained = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Data Points Available", f"{data_points:,}")

    with col2:
        st.metric("Features Engineered", features)

    with col3:
        st.metric("Models Trained", models_trained)

    with col4:
        st.metric("Supported Coins", "7")

    st.markdown("---")

    # ── How It Works ──────────────────────────────────────────────
    st.subheader("🔄 How It Works")

    st.markdown(
        """
        <div style='display: flex; flex-wrap: wrap; gap: 8px;
                    justify-content: center; padding: 20px 0;'>
            <div style='background: #1a1a2e; border: 1px solid #333; border-radius: 10px;
                        padding: 16px 20px; text-align: center; flex: 1; min-width: 130px;'>
                <div style='font-size: 1.8em;'>📡</div>
                <div style='color: #00D4AA; font-weight: 600; margin: 6px 0;'>Step 1</div>
                <div style='color: #aaa; font-size: 0.8em;'>Data Collection</div>
            </div>
            <div style='color: #555; display: flex; align-items: center; font-size: 1.5em;'>→</div>
            <div style='background: #1a1a2e; border: 1px solid #333; border-radius: 10px;
                        padding: 16px 20px; text-align: center; flex: 1; min-width: 130px;'>
                <div style='font-size: 1.8em;'>🧹</div>
                <div style='color: #00D4AA; font-weight: 600; margin: 6px 0;'>Step 2</div>
                <div style='color: #aaa; font-size: 0.8em;'>Cleaning</div>
            </div>
            <div style='color: #555; display: flex; align-items: center; font-size: 1.5em;'>→</div>
            <div style='background: #1a1a2e; border: 1px solid #333; border-radius: 10px;
                        padding: 16px 20px; text-align: center; flex: 1; min-width: 130px;'>
                <div style='font-size: 1.8em;'>⚙️</div>
                <div style='color: #00D4AA; font-weight: 600; margin: 6px 0;'>Step 3</div>
                <div style='color: #aaa; font-size: 0.8em;'>Features</div>
            </div>
            <div style='color: #555; display: flex; align-items: center; font-size: 1.5em;'>→</div>
            <div style='background: #1a1a2e; border: 1px solid #333; border-radius: 10px;
                        padding: 16px 20px; text-align: center; flex: 1; min-width: 130px;'>
                <div style='font-size: 1.8em;'>🧠</div>
                <div style='color: #00D4AA; font-weight: 600; margin: 6px 0;'>Step 4</div>
                <div style='color: #aaa; font-size: 0.8em;'>ML Models</div>
            </div>
            <div style='color: #555; display: flex; align-items: center; font-size: 1.5em;'>→</div>
            <div style='background: #1a1a2e; border: 1px solid #333; border-radius: 10px;
                        padding: 16px 20px; text-align: center; flex: 1; min-width: 130px;'>
                <div style='font-size: 1.8em;'>⚠️</div>
                <div style='color: #00D4AA; font-weight: 600; margin: 6px 0;'>Step 5</div>
                <div style='color: #aaa; font-size: 0.8em;'>Risk</div>
            </div>
            <div style='color: #555; display: flex; align-items: center; font-size: 1.5em;'>→</div>
            <div style='background: #1a1a2e; border: 1px solid #333; border-radius: 10px;
                        padding: 16px 20px; text-align: center; flex: 1; min-width: 130px;'>
                <div style='font-size: 1.8em;'>💡</div>
                <div style='color: #00D4AA; font-weight: 600; margin: 6px 0;'>Step 6</div>
                <div style='color: #aaa; font-size: 0.8em;'>Recommendation</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
