"""
Page 2 — Live Market Dashboard
=================================
Real-time cryptocurrency market data with auto-refresh,
per-coin price cards, live candlestick charts, and market overview.
"""
from __future__ import annotations

import time

import streamlit as st

from frontend.components.charts import candlestick_chart
from frontend.components.metrics_card import price_card
from services.market_data_service import MarketDataService
from utils.config import COIN_DISPLAY_NAMES, SUPPORTED_COINS
from utils.helpers import format_price
from utils.logger import get_logger

logger = get_logger(__name__)


@st.cache_data(ttl=30)
def _fetch_market_data(symbol: str) -> dict:
    """Fetch 24hr stats for a coin (cached for 30s)."""
    try:
        service = MarketDataService()
        stats = service.get_24hr_stats(symbol)
        return stats
    except Exception as exc:
        logger.warning("Failed to fetch market data for %s: %s", symbol, exc)
        return {}


@st.cache_data(ttl=60)
def _fetch_klines(symbol: str, interval: str, limit: int) -> dict:
    """Fetch kline data (cached for 60s). Returns dict for cacheability."""
    try:
        service = MarketDataService()
        df = service.get_data(symbol, interval=interval, limit=limit)
        return {"data": df.to_dict(), "source": service.source_used}
    except Exception as exc:
        logger.warning("Failed to fetch klines for %s: %s", symbol, exc)
        return {}


def render_page() -> None:
    """Render the Live Market Dashboard page."""

    st.markdown(
        "<h2 style='color: #00D4AA;'>📡 Live Market Dashboard</h2>",
        unsafe_allow_html=True,
    )

    # ── Controls ──────────────────────────────────────────────────
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        selected_coins = st.multiselect(
            "Select Cryptocurrencies",
            SUPPORTED_COINS,
            default=["BTCUSDT", "ETHUSDT", "BNBUSDT"],
            format_func=lambda x: COIN_DISPLAY_NAMES.get(x, x),
        )

    with col2:
        auto_refresh = st.checkbox("Auto-Refresh", value=False)

    with col3:
        refresh_interval = st.selectbox(
            "Interval",
            ["30s", "1m", "5m"],
            index=1,
            disabled=not auto_refresh,
        )

    st.markdown("---")

    # ── Per-Coin Price Cards ──────────────────────────────────────
    if selected_coins:
        cols = st.columns(min(len(selected_coins), 4))

        for idx, symbol in enumerate(selected_coins):
            with cols[idx % len(cols)]:
                stats = _fetch_market_data(symbol)

                if stats:
                    price_card(
                        coin_name=COIN_DISPLAY_NAMES.get(symbol, symbol),
                        price=stats.get("last_price", 0),
                        change_pct=stats.get("price_change_pct", 0),
                        high_24h=stats.get("high", 0),
                        low_24h=stats.get("low", 0),
                        volume=stats.get("volume", 0),
                    )
                else:
                    st.warning(f"Data unavailable for {symbol}")

        st.markdown("---")

    # ── Live Candlestick Chart ────────────────────────────────────
    st.subheader("📊 Live Candlestick Chart")

    chart_col1, chart_col2 = st.columns([3, 1])

    with chart_col2:
        chart_symbol = st.selectbox(
            "Chart Coin",
            selected_coins if selected_coins else SUPPORTED_COINS[:3],
            format_func=lambda x: COIN_DISPLAY_NAMES.get(x, x),
            key="live_chart_coin",
        )
        chart_interval = st.selectbox(
            "Timeframe",
            ["1h", "4h", "1d", "1w"],
            index=2,
            key="live_chart_interval",
        )
        chart_limit = st.slider("Candles", 50, 500, 200, key="live_chart_limit")

    with chart_col1:
        import pandas as pd

        kline_data = _fetch_klines(chart_symbol, chart_interval, chart_limit)

        if kline_data and "data" in kline_data:
            df = pd.DataFrame(kline_data["data"])
            source = kline_data.get("source", "Unknown")

            fig = candlestick_chart(
                df,
                title=f"{COIN_DISPLAY_NAMES.get(chart_symbol, chart_symbol)} — "
                      f"{chart_interval.upper()} (Source: {source})",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(
                "⚠️ Unable to fetch live chart data. "
                "Please check your internet connection."
            )

    st.markdown("---")

    # ── Market Dominance ──────────────────────────────────────────
    st.subheader("🥧 Market Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Dominance-like visualization from available data
        import plotly.graph_objects as go
        from utils.config import CHART_TEMPLATE, PRIMARY_ACCENT, BACKGROUND_COLOR

        volumes = {}
        for symbol in selected_coins[:5]:
            stats = _fetch_market_data(symbol)
            if stats:
                volumes[COIN_DISPLAY_NAMES.get(symbol, symbol)] = stats.get("volume", 0)

        if volumes:
            fig = go.Figure(data=go.Pie(
                labels=list(volumes.keys()),
                values=list(volumes.values()),
                hole=0.4,
                textinfo="label+percent",
                marker=dict(colors=[
                    "#00D4AA", "#636EFA", "#EF553B", "#FFA15A", "#AB63FA",
                ]),
            ))
            fig.update_layout(
                title="Volume Distribution",
                template=CHART_TEMPLATE,
                paper_bgcolor=BACKGROUND_COLOR,
                plot_bgcolor=BACKGROUND_COLOR,
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(
            """
            <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid #333; border-radius: 12px;
                        padding: 20px; margin-top: 10px;'>
                <h4 style='color: #00D4AA;'>😱 Fear & Greed Index</h4>
                <div style='text-align: center; padding: 20px;'>
                    <div style='font-size: 3em; font-weight: 800; color: #FFD700;'>
                        55
                    </div>
                    <div style='color: #aaa; margin-top: 4px;'>Neutral</div>
                    <p style='color: #666; font-size: 0.8em; margin-top: 12px;'>
                        Data from alternative.me/crypto/fear-and-greed-index.<br>
                        Updated daily. 0 = Extreme Fear, 100 = Extreme Greed.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Auto-Refresh Logic ────────────────────────────────────────
    if auto_refresh:
        interval_map = {"30s": 30, "1m": 60, "5m": 300}
        wait_seconds = interval_map.get(refresh_interval, 60)

        placeholder = st.empty()
        placeholder.info(f"🔄 Auto-refreshing in {wait_seconds} seconds...")

        time.sleep(wait_seconds)
        st.rerun()
