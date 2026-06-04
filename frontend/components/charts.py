"""
Chart Factory Module
=====================
All Plotly chart factory functions used across the dashboard.
Every function returns a ``go.Figure`` object styled with the
``plotly_dark`` template and ``#00D4AA`` teal-green accent.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.config import (
    BACKGROUND_COLOR,
    BEARISH_COLOR,
    BULLISH_COLOR,
    CHART_TEMPLATE,
    KMEANS_ELBOW_RANGE,
    NEUTRAL_COLOR,
    PRIMARY_ACCENT,
    VOLUME_COLOR,
)


# =============================================================================
# Shared Layout Helper
# =============================================================================

def _base_layout(**kwargs) -> dict:
    """Return a base layout dictionary for consistent chart styling."""
    layout = dict(
        template=CHART_TEMPLATE,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        font=dict(family="Inter, sans-serif", color="#FFFFFF"),
        margin=dict(l=50, r=30, t=50, b=40),
    )
    layout.update(kwargs)
    return layout


# =============================================================================
# 1. Candlestick Chart with Volume Subplot
# =============================================================================

def candlestick_chart(df: pd.DataFrame, title: str = "OHLCV Candlestick Chart") -> go.Figure:
    """
    Create a candlestick chart with volume bars as a subplot.

    Args:
        df: DataFrame with ``date``, ``open``, ``high``, ``low``, ``close``, ``volume``.
        title: Chart title.

    Returns:
        Plotly Figure with candlestick and volume.
    """
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.03, row_heights=[0.75, 0.25],
        subplot_titles=("", "Volume"),
    )

    # Candlestick trace
    fig.add_trace(
        go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            increasing_line_color=BULLISH_COLOR,
            decreasing_line_color=BEARISH_COLOR,
            name="OHLC",
        ),
        row=1, col=1,
    )

    # Volume bar trace
    colors = [
        BULLISH_COLOR if row["close"] >= row["open"] else BEARISH_COLOR
        for _, row in df.iterrows()
    ]
    fig.add_trace(
        go.Bar(
            x=df["date"], y=df["volume"],
            marker_color=colors, opacity=0.6,
            name="Volume", showlegend=False,
        ),
        row=2, col=1,
    )

    fig.update_layout(
        **_base_layout(title=title, xaxis_rangeslider_visible=False, height=600)
    )

    return fig


# =============================================================================
# 2. Line Chart with Moving Average Overlays
# =============================================================================

def line_chart_with_ma(
    df: pd.DataFrame,
    mas: list[str] | None = None,
    title: str = "Price with Moving Averages",
) -> go.Figure:
    """
    Create a line chart of close price with selectable moving average overlays.

    Args:
        df: DataFrame with ``date``, ``close``, and MA columns.
        mas: List of MA column names to overlay (e.g., ``["sma_7", "ema_12"]``).
        title: Chart title.

    Returns:
        Plotly Figure with price and MA lines.
    """
    fig = go.Figure()

    # Close price line
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["close"],
        mode="lines", name="Close",
        line=dict(color="#FFFFFF", width=1.5),
    ))

    # MA overlays
    ma_colors = [PRIMARY_ACCENT, "#636EFA", "#EF553B", "#FFA15A", "#AB63FA", "#FF6692"]
    if mas:
        for idx, ma_col in enumerate(mas):
            if ma_col in df.columns:
                color = ma_colors[idx % len(ma_colors)]
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df[ma_col],
                    mode="lines", name=ma_col.upper(),
                    line=dict(color=color, width=1, dash="dot"),
                ))

    fig.update_layout(**_base_layout(title=title, height=450))
    return fig


# =============================================================================
# 3. RSI Chart
# =============================================================================

def rsi_chart(df: pd.DataFrame, title: str = "RSI (14)") -> go.Figure:
    """
    Create an RSI chart with overbought/oversold reference lines.

    Args:
        df: DataFrame with ``date`` and ``rsi_14`` columns.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()

    if "rsi_14" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["rsi_14"],
            mode="lines", name="RSI",
            line=dict(color=PRIMARY_ACCENT, width=1.5),
        ))

    # Overbought line (70)
    fig.add_hline(y=70, line_dash="dash", line_color=BEARISH_COLOR,
                  annotation_text="Overbought (70)")
    # Oversold line (30)
    fig.add_hline(y=30, line_dash="dash", line_color=BULLISH_COLOR,
                  annotation_text="Oversold (30)")

    fig.update_layout(**_base_layout(title=title, height=300, yaxis_range=[0, 100]))
    return fig


# =============================================================================
# 4. MACD Chart
# =============================================================================

def macd_chart(df: pd.DataFrame, title: str = "MACD") -> go.Figure:
    """
    Create a MACD chart with MACD line, signal line, and histogram.

    Args:
        df: DataFrame with ``date``, ``macd``, ``macd_signal``, ``macd_diff``.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()

    if "macd" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["macd"],
            mode="lines", name="MACD",
            line=dict(color=PRIMARY_ACCENT, width=1.5),
        ))

    if "macd_signal" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["macd_signal"],
            mode="lines", name="Signal",
            line=dict(color="#EF553B", width=1.5),
        ))

    if "macd_diff" in df.columns:
        colors = [BULLISH_COLOR if v >= 0 else BEARISH_COLOR for v in df["macd_diff"]]
        fig.add_trace(go.Bar(
            x=df["date"], y=df["macd_diff"],
            marker_color=colors, opacity=0.6,
            name="Histogram",
        ))

    fig.update_layout(**_base_layout(title=title, height=300))
    return fig


# =============================================================================
# 5. Bollinger Bands Chart
# =============================================================================

def bollinger_chart(df: pd.DataFrame, title: str = "Bollinger Bands") -> go.Figure:
    """
    Create a Bollinger Bands chart with upper, lower, and middle bands.

    Args:
        df: DataFrame with ``date``, ``close``, ``bb_upper``, ``bb_lower``, ``bb_middle``.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()

    # Close price
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["close"],
        mode="lines", name="Close",
        line=dict(color="#FFFFFF", width=1.5),
    ))

    if "bb_upper" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["bb_upper"],
            mode="lines", name="Upper Band",
            line=dict(color=PRIMARY_ACCENT, width=1, dash="dash"),
        ))

    if "bb_lower" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["bb_lower"],
            mode="lines", name="Lower Band",
            line=dict(color=PRIMARY_ACCENT, width=1, dash="dash"),
            fill="tonexty", fillcolor="rgba(0,212,170,0.1)",
        ))

    if "bb_middle" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["bb_middle"],
            mode="lines", name="Middle Band",
            line=dict(color=NEUTRAL_COLOR, width=1, dash="dot"),
        ))

    fig.update_layout(**_base_layout(title=title, height=450))
    return fig


# =============================================================================
# 6. Correlation Heatmap
# =============================================================================

def correlation_heatmap(df: pd.DataFrame, title: str = "Feature Correlation Matrix") -> go.Figure:
    """
    Create a Plotly heatmap of the correlation matrix.

    Args:
        df: DataFrame with numeric feature columns.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.columns.tolist(),
        colorscale=[[0, BEARISH_COLOR], [0.5, BACKGROUND_COLOR], [1, PRIMARY_ACCENT]],
        zmin=-1, zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont={"size": 8},
        hovertemplate="%{x} vs %{y}: %{z:.2f}<extra></extra>",
    ))

    fig.update_layout(**_base_layout(title=title, height=700, width=800))
    return fig


# =============================================================================
# 7. Risk Distribution Pie Chart
# =============================================================================

def risk_distribution_pie(
    risk_counts: dict,
    title: str = "Risk Distribution",
) -> go.Figure:
    """
    Create a pie chart of risk level distribution.

    Args:
        risk_counts: Dictionary mapping risk labels to counts.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    risk_colors = {
        "Low": BULLISH_COLOR,
        "Medium": NEUTRAL_COLOR,
        "High": BEARISH_COLOR,
    }

    labels = list(risk_counts.keys())
    values = list(risk_counts.values())
    colors = [risk_colors.get(l, "#636EFA") for l in labels]

    fig = go.Figure(data=go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors),
        hole=0.4, textinfo="label+percent",
        textfont=dict(size=14),
    ))

    fig.update_layout(**_base_layout(title=title, height=400))
    return fig


# =============================================================================
# 8. Feature Importance Bar Chart
# =============================================================================

def feature_importance_bar(
    importances: pd.DataFrame,
    top_n: int = 15,
    title: str = "Feature Importance (Random Forest)",
) -> go.Figure:
    """
    Create a horizontal bar chart of feature importances.

    Args:
        importances: DataFrame with ``feature`` and ``importance`` columns.
        top_n: Number of top features to display.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    top = importances.head(top_n).sort_values("importance", ascending=True)

    fig = go.Figure(data=go.Bar(
        x=top["importance"],
        y=top["feature"],
        orientation="h",
        marker_color=PRIMARY_ACCENT,
        text=top["importance"].apply(lambda x: f"{x:.4f}"),
        textposition="auto",
    ))

    fig.update_layout(**_base_layout(title=title, height=max(400, top_n * 30)))
    return fig


# =============================================================================
# 9. Confusion Matrix Heatmap
# =============================================================================

def confusion_matrix_heatmap(
    cm: np.ndarray,
    labels: list[str] | None = None,
    title: str = "Confusion Matrix",
) -> go.Figure:
    """
    Create a Plotly heatmap for a confusion matrix.

    Args:
        cm: 2×2 confusion matrix.
        labels: Class labels.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    if labels is None:
        labels = ["Bearish", "Bullish"]

    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=labels,
        y=labels,
        colorscale=[[0, BACKGROUND_COLOR], [1, PRIMARY_ACCENT]],
        text=cm,
        texttemplate="%{text}",
        textfont={"size": 20},
        hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
    ))

    fig.update_layout(**_base_layout(
        title=title,
        xaxis_title="Predicted",
        yaxis_title="Actual",
        height=400, width=450,
    ))
    return fig


# =============================================================================
# 10. ROC Curve Plot
# =============================================================================

def roc_curve_plot(
    fpr: np.ndarray,
    tpr: np.ndarray,
    auc_score: float,
    label: str = "Model",
) -> go.Figure:
    """
    Create a ROC curve plot.

    Args:
        fpr: False positive rates.
        tpr: True positive rates.
        auc_score: Area under the ROC curve.
        label: Legend label.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=fpr, y=tpr,
        mode="lines",
        name=f"{label} (AUC = {auc_score:.4f})",
        line=dict(color=PRIMARY_ACCENT, width=2),
    ))

    # Diagonal reference
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode="lines",
        name="Random",
        line=dict(color="gray", width=1, dash="dash"),
    ))

    fig.update_layout(**_base_layout(
        title="ROC Curve",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=450,
    ))
    return fig


# =============================================================================
# 11. 3D Cluster Scatter Plot
# =============================================================================

def cluster_scatter_3d(
    df: pd.DataFrame,
    title: str = "K-Means Risk Clusters (3D)",
) -> go.Figure:
    """
    Create a 3D scatter plot of K-Means clusters.

    Args:
        df: DataFrame with clustering features and a ``risk_level`` column.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    cluster_colors = {
        "Low": BULLISH_COLOR,
        "Medium": NEUTRAL_COLOR,
        "High": BEARISH_COLOR,
    }

    # Determine axes
    axes = ["volatility_14", "rsi_14", "volume_change"]
    available_axes = [a for a in axes if a in df.columns]

    if len(available_axes) < 3:
        # Fallback to first 3 numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        available_axes = numeric_cols[:3]

    if len(available_axes) < 3:
        fig = go.Figure()
        fig.update_layout(**_base_layout(title="Insufficient features for 3D plot"))
        return fig

    fig = go.Figure()

    if "risk_level" in df.columns:
        for risk, group_df in df.groupby("risk_level"):
            color = cluster_colors.get(str(risk), "#636EFA")
            fig.add_trace(go.Scatter3d(
                x=group_df[available_axes[0]],
                y=group_df[available_axes[1]],
                z=group_df[available_axes[2]],
                mode="markers",
                marker=dict(size=4, color=color, opacity=0.7),
                name=f"{risk} Risk",
            ))
    else:
        fig.add_trace(go.Scatter3d(
            x=df[available_axes[0]],
            y=df[available_axes[1]],
            z=df[available_axes[2]],
            mode="markers",
            marker=dict(size=4, color=PRIMARY_ACCENT, opacity=0.7),
            name="Data Points",
        ))

    fig.update_layout(**_base_layout(
        title=title, height=600,
        scene=dict(
            xaxis_title=available_axes[0],
            yaxis_title=available_axes[1],
            zaxis_title=available_axes[2],
        ),
    ))
    return fig


# =============================================================================
# 12. Probability Gauge
# =============================================================================

def probability_gauge(
    bullish_prob: float,
    title: str = "Bullish Probability",
) -> go.Figure:
    """
    Create a gauge chart displaying the bullish probability.

    Args:
        bullish_prob: Bullish probability (0.0–1.0).
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=bullish_prob * 100,
        number={"suffix": "%", "font": {"size": 36}},
        gauge=dict(
            axis=dict(range=[0, 100]),
            bar=dict(color=PRIMARY_ACCENT),
            bgcolor=BACKGROUND_COLOR,
            borderwidth=2,
            bordercolor="#333333",
            steps=[
                dict(range=[0, 30], color=BEARISH_COLOR),
                dict(range=[30, 50], color="#FF8C00"),
                dict(range=[50, 70], color=NEUTRAL_COLOR),
                dict(range=[70, 100], color=BULLISH_COLOR),
            ],
            threshold=dict(
                line=dict(color="white", width=3),
                thickness=0.8,
                value=bullish_prob * 100,
            ),
        ),
        title=dict(text=title, font=dict(size=16)),
    ))

    fig.update_layout(**_base_layout(height=350))
    return fig


# =============================================================================
# 13. Elbow Plot
# =============================================================================

def elbow_plot(
    inertias: list[float],
    title: str = "Elbow Method — Optimal k",
) -> go.Figure:
    """
    Create an elbow method plot (inertia vs. k).

    Args:
        inertias: List of inertia values for k = 2 to 8.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    k_values = list(KMEANS_ELBOW_RANGE)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=k_values, y=inertias,
        mode="lines+markers",
        name="Inertia",
        line=dict(color=PRIMARY_ACCENT, width=2),
        marker=dict(size=8),
    ))

    fig.update_layout(**_base_layout(
        title=title,
        xaxis_title="Number of Clusters (k)",
        yaxis_title="Inertia",
        height=400,
    ))
    return fig


# =============================================================================
# 14. Volume Bar Chart
# =============================================================================

def volume_bar_chart(
    df: pd.DataFrame,
    title: str = "Trading Volume",
) -> go.Figure:
    """
    Create a volume bar chart.

    Args:
        df: DataFrame with ``date`` and ``volume`` columns.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure(data=go.Bar(
        x=df["date"],
        y=df["volume"],
        marker_color=VOLUME_COLOR,
        opacity=0.7,
        name="Volume",
    ))

    fig.update_layout(**_base_layout(title=title, height=350))
    return fig


# =============================================================================
# 15. Prediction History Line Chart
# =============================================================================

def prediction_history_line(
    history: list[dict],
    title: str = "Prediction History",
) -> go.Figure:
    """
    Create a line chart showing prediction confidence over time.

    Args:
        history: List of prediction dictionaries with ``bullish_prob``.
        title: Chart title.

    Returns:
        Plotly Figure.
    """
    if not history:
        fig = go.Figure()
        fig.update_layout(**_base_layout(title="No prediction history yet"))
        return fig

    indices = list(range(1, len(history) + 1))
    bullish_probs = [h.get("bullish_prob", 0.5) for h in history]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=indices, y=[p * 100 for p in bullish_probs],
        mode="lines+markers",
        name="Bullish %",
        line=dict(color=PRIMARY_ACCENT, width=2),
        marker=dict(size=6),
    ))

    # 50% reference line
    fig.add_hline(y=50, line_dash="dash", line_color="gray",
                  annotation_text="50% (Neutral)")

    fig.update_layout(**_base_layout(
        title=title,
        xaxis_title="Prediction #",
        yaxis_title="Bullish Probability (%)",
        yaxis_range=[0, 100],
        height=350,
    ))
    return fig
