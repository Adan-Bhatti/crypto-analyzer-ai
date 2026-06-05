"""
Metrics Card Components
========================
Provides KPI card components for the dashboard using custom HTML/CSS
styled to match the dark-themed crypto dashboard aesthetic.
"""
from __future__ import annotations

import streamlit as st

from utils.config import BEARISH_COLOR, BULLISH_COLOR, NEUTRAL_COLOR, PRIMARY_ACCENT
from utils.helpers import format_large_number, format_percentage, format_price


def metric_card(
    title: str,
    value: str,
    delta: str | None = None,
    delta_color: str | None = None,
    icon: str = "📊",
) -> None:
    """
    Render a custom-styled KPI metric card.

    Args:
        title: Card title / label.
        value: Main display value (pre-formatted string).
        delta: Optional change/delta string (e.g., ``"+3.42%"``).
        delta_color: CSS color for the delta text. Auto-detected if None.
        icon: Emoji icon displayed in the card header.
    """
    # Auto-detect delta color from sign
    if delta_color is None and delta is not None:
        if delta.startswith("+"):
            delta_color = BULLISH_COLOR
        elif delta.startswith("-"):
            delta_color = BEARISH_COLOR
        else:
            delta_color = NEUTRAL_COLOR

    delta_html = ""
    if delta:
        delta_html = f"<div style='font-size: 0.85em; color: {delta_color}; margin-top: 4px;'>{delta}</div>"

    st.markdown(
        f"""
        <div style='
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #333;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease;
        '>
            <div style='font-size: 1.4em; margin-bottom: 6px;'>{icon}</div>
            <div style='color: #888; font-size: 0.8em; text-transform: uppercase;
                        letter-spacing: 1px; margin-bottom: 8px;'>
                {title}
            </div>
            <div style='font-size: 1.6em; font-weight: 700; color: #FFFFFF;'>
                {value}
            </div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def price_card(
    coin_name: str,
    price: float,
    change_pct: float,
    high_24h: float = 0.0,
    low_24h: float = 0.0,
    volume: float = 0.0,
) -> None:
    """
    Render a cryptocurrency price card with 24h stats.

    Args:
        coin_name: Display name of the cryptocurrency.
        price: Current price.
        change_pct: 24h price change percentage.
        high_24h: 24h high price.
        low_24h: 24h low price.
        volume: 24h trading volume.
    """
    # Determine color based on change direction
    change_color = BULLISH_COLOR if change_pct >= 0 else BEARISH_COLOR
    arrow = "▲" if change_pct >= 0 else "▼"

    st.markdown(
        f"""
        <div style='
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #333;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        '>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div style='color: #aaa; font-size: 0.85em; margin-bottom: 4px;'>
                        {coin_name}
                    </div>
                    <div style='font-size: 1.5em; font-weight: 700; color: #FFF;'>
                        {format_price(price)}
                    </div>
                </div>
                <div style='text-align: right;'>
                    <div style='color: {change_color}; font-size: 1.1em; font-weight: 600;'>
                        {arrow} {abs(change_pct):.2f}%
                    </div>
                </div>
            </div>
            <div style='display: flex; justify-content: space-between;
                        margin-top: 12px; font-size: 0.78em; color: #888;'>
                <span>H: {format_price(high_24h)}</span>
                <span>L: {format_price(low_24h)}</span>
                <span>Vol: {format_large_number(volume)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def action_badge(
    action: str,
    confidence: str,
    size: str = "large",
) -> None:
    """
    Render a large BUY/HOLD/SELL action badge.

    Args:
        action: Action string (``"BUY"``, ``"HOLD"``, or ``"SELL"``).
        confidence: Confidence level string.
        size: ``"large"`` or ``"small"``.
    """
    action_colors = {
        "BUY": BULLISH_COLOR,
        "HOLD": NEUTRAL_COLOR,
        "SELL": BEARISH_COLOR,
    }

    action_icons = {
        "BUY": "🟢",
        "HOLD": "🟡",
        "SELL": "🔴",
    }

    color = action_colors.get(action, "#888")
    icon = action_icons.get(action, "⚪")

    if size == "large":
        font_size = "3em"
        padding = "30px 50px"
    else:
        font_size = "1.5em"
        padding = "15px 25px"

    st.markdown(
        f"""
        <div style='text-align: center; margin: 20px 0;'>
            <div style='
                display: inline-block;
                background: linear-gradient(135deg, rgba({_hex_to_rgb(color)}, 0.2), rgba({_hex_to_rgb(color)}, 0.05));
                border: 2px solid {color};
                border-radius: 16px;
                padding: {padding};
                box-shadow: 0 0 20px rgba({_hex_to_rgb(color)}, 0.3);
            '>
                <div style='font-size: {font_size}; font-weight: 800; color: {color};'>
                    {icon} {action}
                </div>
                <div style='font-size: 0.9em; color: #aaa; margin-top: 8px;'>
                    Confidence: {confidence}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(risk_level: str) -> None:
    """
    Render a color-coded risk level badge.

    Args:
        risk_level: Risk level string (``"Low"``, ``"Medium"``, ``"High"``).
    """
    risk_config = {
        "Low": {"color": BULLISH_COLOR, "icon": "🟢", "text": "LOW RISK"},
        "Medium": {"color": NEUTRAL_COLOR, "icon": "🟡", "text": "MEDIUM RISK"},
        "High": {"color": BEARISH_COLOR, "icon": "🔴", "text": "HIGH RISK"},
    }

    config = risk_config.get(risk_level, risk_config["Medium"])

    st.markdown(
        f"""
        <div style='text-align: center; margin: 15px 0;'>
            <span style='
                display: inline-block;
                background: rgba({_hex_to_rgb(config["color"])}, 0.15);
                border: 1px solid {config["color"]};
                border-radius: 20px;
                padding: 8px 24px;
                font-size: 1em;
                font-weight: 600;
                color: {config["color"]};
                letter-spacing: 1px;
            '>
                {config["icon"]} {config["text"]}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _hex_to_rgb(hex_color: str) -> str:
    """Convert a hex color string to an 'R, G, B' string for CSS rgba()."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"{r}, {g}, {b}"
