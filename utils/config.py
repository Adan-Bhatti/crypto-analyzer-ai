"""
Central Configuration Module
=============================
All project-wide constants, thresholds, and configuration values.
No magic numbers should appear in any other module — reference this file instead.
"""
from __future__ import annotations

import os
from pathlib import Path

# =============================================================================
# Project Paths
# =============================================================================
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
MODELS_DIR: str = str(PROJECT_ROOT / "models" / "saved")
DATA_DIR: str = str(PROJECT_ROOT / "data" / "sample")
LOGS_DIR: str = str(PROJECT_ROOT / "logs")

# =============================================================================
# Supported Cryptocurrencies
# =============================================================================
SUPPORTED_COINS: list[str] = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT",
    "DOGEUSDT", "XRPUSDT",
]

# Mapping from Binance symbols to Yahoo Finance tickers
YAHOO_TICKERS: dict[str, str] = {
    "BTCUSDT": "BTC-USD",
    "ETHUSDT": "ETH-USD",
    "BNBUSDT": "BNB-USD",
    "SOLUSDT": "SOL-USD",
    "ADAUSDT": "ADA-USD",
    "DOGEUSDT": "DOGE-USD",
    "XRPUSDT": "XRP-USD",
}

# Human-readable display names
COIN_DISPLAY_NAMES: dict[str, str] = {
    "BTCUSDT": "Bitcoin (BTC)",
    "ETHUSDT": "Ethereum (ETH)",
    "BNBUSDT": "Binance Coin (BNB)",
    "SOLUSDT": "Solana (SOL)",
    "ADAUSDT": "Cardano (ADA)",
    "DOGEUSDT": "Dogecoin (DOGE)",
    "XRPUSDT": "XRP (XRP)",
}

# =============================================================================
# API Configuration
# =============================================================================
BINANCE_BASE_URL: str = "https://api.binance.com/api/v3"
REQUEST_TIMEOUT: int = 10
MAX_RETRIES: int = 3
BACKOFF_FACTOR: float = 0.5  # Exponential backoff multiplier

# Supported Binance kline intervals
SUPPORTED_INTERVALS: list[str] = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]

# =============================================================================
# Data Defaults
# =============================================================================
DEFAULT_INTERVAL: str = "1d"
DEFAULT_LIMIT: int = 1000          # Binance max per request
YAHOO_MAX_PERIOD: str = "max"      # Full historical data via Yahoo Finance
MIN_DATA_ROWS: int = 200

# Required OHLCV columns (case-insensitive matching is handled in the loader)
REQUIRED_COLUMNS: list[str] = ["date", "open", "high", "low", "close", "volume"]

# =============================================================================
# Feature Engineering Windows
# =============================================================================
SMA_WINDOWS: list[int] = [7, 14, 21]
EMA_WINDOWS: list[int] = [12, 26]
RSI_WINDOW: int = 14
MACD_FAST: int = 12
MACD_SLOW: int = 26
MACD_SIGNAL: int = 9
BOLLINGER_WINDOW: int = 20
VOLATILITY_WINDOW: int = 14
MOMENTUM_WINDOW: int = 5

# =============================================================================
# Model Configuration
# =============================================================================
RANDOM_STATE: int = 42
TEST_SIZE: float = 0.20  # 80/20 train/test split
CV_SPLITS: int = 5       # TimeSeriesSplit n_splits

# Random Forest defaults
RF_N_ESTIMATORS: int = 300
RF_MAX_DEPTH: int = 10

# Expanded GridSearchCV parameter grid for Random Forest
RF_PARAM_GRID: dict[str, list] = {
    "n_estimators": [100, 200, 300],
    "max_depth": [5, 10, 15, None],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2],
    "max_features": ["sqrt", "log2"],
}

# Logistic Regression defaults
LR_C: float = 1.0
LR_MAX_ITER: int = 2000

# GridSearchCV parameter grid for Logistic Regression
LR_PARAM_GRID: dict[str, list] = {
    "C": [0.01, 0.1, 1.0, 10.0, 100.0],
    "solver": ["lbfgs", "liblinear"],
    "max_iter": [1000, 2000],
}

# XGBoost defaults
XGB_N_ESTIMATORS: int = 300
XGB_MAX_DEPTH: int = 6
XGB_LEARNING_RATE: float = 0.05

# GridSearchCV parameter grid for XGBoost
XGB_PARAM_GRID: dict[str, list] = {
    "n_estimators": [100, 200, 300],
    "max_depth": [3, 5, 7],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0],
}

# K-Means defaults
KMEANS_N_CLUSTERS: int = 3
KMEANS_ELBOW_RANGE: range = range(2, 9)  # k = 2 to 8

# Minimum accuracy target (triggers re-tuning if below)
MIN_ACCURACY_TARGET: float = 0.80
MIN_SILHOUETTE_TARGET: float = 0.40

# =============================================================================
# Agent / Recommendation Thresholds
# =============================================================================
BUY_THRESHOLD: float = 0.70    # bullish_prob > 70% → consider BUY
HOLD_LOWER: float = 0.50       # bullish_prob 50–70% → consider HOLD
SELL_THRESHOLD: float = 0.60   # bearish_prob > 60% → consider SELL

# Stop-loss / take-profit multipliers
STOP_LOSS_PCT: float = 0.05    # 5% below entry
TAKE_PROFIT_PCT: float = 0.10  # 10% above entry

# =============================================================================
# Risk Classification Labels
# =============================================================================
RISK_LABELS: dict[int, str] = {
    0: "Low",
    1: "Medium",
    2: "High",
}

RISK_COLORS: dict[str, str] = {
    "Low": "#00D4AA",
    "Medium": "#FFD700",
    "High": "#FF4444",
}

# =============================================================================
# UI / Chart Styling
# =============================================================================
CHART_TEMPLATE: str = "plotly_dark"
PRIMARY_ACCENT: str = "#00D4AA"      # Teal-green accent
BACKGROUND_COLOR: str = "#0E1117"    # Dark background
BULLISH_COLOR: str = "#00D4AA"       # Green for bullish / BUY
BEARISH_COLOR: str = "#FF4444"       # Red for bearish / SELL
NEUTRAL_COLOR: str = "#FFD700"       # Yellow for HOLD
VOLUME_COLOR: str = "#636EFA"        # Blue for volume bars

# Navigation page labels
PAGE_LABELS: list[str] = [
    "🏠 Project Overview",
    "📡 Live Market Dashboard",
    "📊 Historical Analysis",
    "🔮 Prediction Dashboard",
    "⚠️ Risk Classification",
    "💡 Buy/Sell/Hold Engine",
    "📜 Personal History",
    "📈 Model Performance",
]

# =============================================================================
# Clustering Features (used by KMeansRiskClassifier)
# =============================================================================
CLUSTERING_FEATURES: list[str] = [
    "volatility_14",
    "rsi_14",
    "volume_change",
    "daily_return_std",
]

# =============================================================================
# Additional Feature Engineering Windows
# =============================================================================
ATR_WINDOW: int = 14            # Average True Range window
STOCH_WINDOW: int = 14         # Stochastic Oscillator window
WILLIAMS_LBPERIOD: int = 14    # Williams %R lookback
LAG_PERIODS: list[int] = [1, 3, 5, 7]   # Lag feature periods
ROLL_RETURN_WINDOWS: list[int] = [7, 14, 21]  # Rolling return windows
