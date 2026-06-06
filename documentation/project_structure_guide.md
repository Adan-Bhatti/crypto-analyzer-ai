# 📁 Project Structure & Architecture Guide
## AI-Based Cryptocurrency Market Behavior Analyzer & Risk Predictor

---

## Table of Contents
1. [Overview](#overview)
2. [Folder Hierarchy](#folder-hierarchy)
3. [Architecture Flow](#architecture-flow)
4. [Root-Level Files](#root-level-files)
5. [Module-by-Module Breakdown](#module-by-module-breakdown)
   - [agent/](#agent)
   - [backend/](#backend)
   - [data/](#data)
   - [frontend/](#frontend)
   - [models/](#models)
   - [services/](#services)
   - [utils/](#utils)
   - [documentation/](#documentation)

---

## Overview

This project is a full-stack AI-powered cryptocurrency analysis dashboard built with Python and Streamlit.
It combines real-time data fetching, machine learning prediction, unsupervised risk classification,
and an intelligent rule-based agent to generate actionable trading recommendations.

**Supported Coins:** BTC, ETH, BNB, SOL, ADA, DOGE, XRP

**Tech Stack:**
- **Frontend:** Streamlit + Plotly (interactive charts)
- **ML Models:** XGBoost (primary), Random Forest, Logistic Regression, K-Means Clustering
- **Data Sources:** Binance REST API, Yahoo Finance (`yfinance`), Local CSV upload
- **Feature Engineering:** `ta` library (14+ technical indicators)
- **Model Persistence:** `joblib`

---

## Folder Hierarchy

```
crypto_analyzer/                        ← Project root
│
├── app.py                              ← Main entry point (run with: streamlit run app.py)
├── train_models.py                     ← Standalone script for full model training
├── download_datasets.py                ← Standalone script to export historical CSVs
├── requirements.txt                    ← Python package dependencies
├── .env.example                        ← Template for environment variables (API keys)
├── .gitignore                          ← Files excluded from Git version control
├── README.md                           ← Project overview and setup instructions
│
├── agent/                              ← AI Recommendation Engine
│   ├── __init__.py
│   └── recommendation_agent.py         ← Rule-based BUY/HOLD/SELL decision agent
│
├── backend/                            ← Pipeline Orchestration
│   ├── __init__.py
│   ├── pipeline.py                     ← End-to-end pipeline (data → prediction → recommendation)
│   └── orchestrator.py                 ← Session state and pipeline coordination
│
├── data/                               ← Data Layer
│   ├── __init__.py
│   ├── loader.py                       ← Loads data from CSV, Binance API, Yahoo Finance
│   ├── cleaner.py                      ← Removes nulls, normalizes OHLCV data
│   ├── feature_engineer.py             ← Computes 14+ technical indicators
│   └── datasets/                       ← (Optional) Downloaded historical CSV files
│
├── frontend/                           ← UI Layer
│   ├── __init__.py
│   ├── components/                     ← Reusable UI components
│   │   ├── __init__.py
│   │   ├── sidebar.py                  ← Sidebar controls (coin, data source, run button)
│   │   ├── charts.py                   ← Plotly chart builders (candlestick, indicators)
│   │   └── metrics_card.py             ← Metric display cards
│   └── pages/                          ← Individual dashboard pages
│       ├── __init__.py
│       ├── page_overview.py            ← Project overview & instructions
│       ├── page_live_market.py         ← Live price, ticker, real-time data
│       ├── page_historical.py          ← Historical charts + indicator overlays
│       ├── page_prediction.py          ← ML prediction results (probabilities, feature importance)
│       ├── page_risk.py                ← K-Means risk classification + 3D cluster chart
│       ├── page_recommendation.py      ← BUY/HOLD/SELL output + stop-loss/take-profit
│       └── page_performance.py         ← Model accuracy, F1, ROC-AUC, confusion matrix
│
├── models/                             ← Machine Learning Models
│   ├── __init__.py
│   ├── xgboost_model.py                ← XGBoost classifier (primary prediction model)
│   ├── random_forest.py                ← Random Forest classifier
│   ├── logistic_regression.py          ← Logistic Regression classifier
│   ├── kmeans_clustering.py            ← K-Means unsupervised risk classifier
│   ├── model_manager.py                ← Handles model saving/loading via joblib
│   └── saved/                          ← Serialized trained models (.joblib files)
│
├── services/                           ← External API Clients
│   ├── __init__.py
│   ├── binance_service.py              ← Binance REST API client (live OHLCV data)
│   ├── yahoo_service.py                ← Yahoo Finance client (historical data)
│   └── market_data_service.py          ← Unified service (live price, orderbook, ticker)
│
├── utils/                              ← Shared Utilities
│   ├── __init__.py
│   ├── config.py                       ← All global constants and thresholds
│   ├── logger.py                       ← Logging setup
│   ├── evaluator.py                    ← ML metrics (Accuracy, F1, ROC-AUC, confusion matrix)
│   ├── feature_selector.py             ← Automated feature selection helpers
│   └── helpers.py                      ← General-purpose helper functions
│
├── documentation/                      ← Project Documentation
│   ├── project_structure_guide.md      ← THIS FILE — folder & file explanations
│   ├── project_report.md               ← Full academic/technical report
│   ├── architecture_diagram.md         ← ASCII architecture and data flow diagrams
│   ├── api_reference.md                ← Complete module/class/method documentation
│   ├── deployment_guide.md             ← Docker and Streamlit Cloud deployment
│   └── viva_qa.md                      ← 30 common questions with detailed answers
│
└── logs/                               ← Runtime log files (auto-generated, not submitted)
```

---

## Architecture Flow

The system follows a **layered pipeline architecture**. When a user clicks "Run Analysis":

```
User (Streamlit UI)
        │
        ▼
   app.py  ──────────────────────────────────────┐
   (Entry Point)                                 │
        │                                        │ Renders pages
        ▼                                        ▼
   backend/pipeline.py          frontend/pages/*.py
   (CryptoPipeline)
        │
        ├─── Step 1: DATA LOADING
        │         data/loader.py
        │         services/binance_service.py  ──► Binance REST API
        │         services/yahoo_service.py   ──► Yahoo Finance
        │
        ├─── Step 2: DATA CLEANING
        │         data/cleaner.py
        │         (Remove nulls, normalize OHLCV columns)
        │
        ├─── Step 3: FEATURE ENGINEERING
        │         data/feature_engineer.py
        │         (SMA, EMA, RSI, MACD, Bollinger Bands, ATR,
        │          OBV, Stochastic, Williams %R, lag features)
        │
        ├─── Step 4: ML PREDICTION
        │         models/xgboost_model.py   ─────► Primary model
        │         models/random_forest.py
        │         models/logistic_regression.py
        │         (GridSearchCV + TimeSeriesSplit cross-validation)
        │         (Outputs: Bullish/Bearish probabilities)
        │
        ├─── Step 5: RISK CLASSIFICATION
        │         models/kmeans_clustering.py
        │         (Unsupervised clustering on volatility,
        │          RSI, volume change → Low/Medium/High risk)
        │
        └─── Step 6: RECOMMENDATION
                  agent/recommendation_agent.py
                  (Decision table: probabilities + risk → BUY/HOLD/SELL)
                  (Computes stop-loss and take-profit levels)
```

---

## Root-Level Files

### `app.py` — Main Entry Point
- The **only file** the user runs: `streamlit run app.py`
- Configures the page layout, dark theme CSS, and sidebar navigation
- Acts as a **router**: reads which page is selected and imports+renders the correct page module
- Handles the "Run Analysis" button: triggers `CryptoPipeline` and stores results in Streamlit session state

### `train_models.py` — Standalone Model Trainer
- Can be run independently from the command line: `python train_models.py`
- Downloads maximum historical data for all supported coins (via Yahoo Finance)
- Trains all ML models (XGBoost, Random Forest, Logistic Regression, K-Means) with full GridSearchCV
- Saves trained models to `models/saved/` for fast loading in the live app

### `download_datasets.py` — Dataset Exporter
- Downloads historical OHLCV data for all 7 supported coins and saves them as CSV files
- Useful for offline analysis or providing sample data to the teacher

### `requirements.txt` — Dependencies
- Lists all Python packages needed to run the project
- Teacher runs `pip install -r requirements.txt` to install everything

### `.env.example` — Environment Template
- Template showing which environment variables can be set
- **Binance API keys** (optional — public endpoints work without them)
- Copy to `.env` and fill in values if authenticated endpoints are needed

---

## Module-by-Module Breakdown

---

### `agent/`

**Purpose:** The "brain" of the system — synthesizes ML outputs into a human-readable recommendation.

#### `recommendation_agent.py`
- **Class:** `RecommendationAgent`
- **What it does:** Implements a rule-based decision table that combines:
  - **Bullish probability** (from XGBoost) — how likely the price will go up
  - **Bearish probability** (from XGBoost) — how likely the price will go down
  - **Risk level** (from K-Means) — Low, Medium, or High market risk
- **Outputs:** One of `BUY`, `HOLD`, or `SELL` with a confidence level (`High`, `Medium`, `Low`)
- **Also computes:** Suggested stop-loss price (5% buffer) and take-profit price (10% target)
- **Human reasoning:** Generates 3–5 bullet point explanations for why the action was chosen
- **Class:** `RecommendationResult` — a dataclass holding action, confidence, probabilities, stop-loss, take-profit, and reasoning

**Decision Logic Example:**
| Bullish Prob | Risk Level | Recommendation |
|---|---|---|
| > 70% | Low | **BUY** (High confidence) |
| > 70% | High | **HOLD** (risk overrides signal) |
| < 50% | High | **SELL** (High confidence) |

---

### `backend/`

**Purpose:** Orchestrates the entire data → ML → output pipeline.

#### `pipeline.py`
- **Class:** `CryptoPipeline`
- **What it does:** Coordinates all 6 pipeline steps in sequence (see Architecture Flow above)
- **Method:** `run_full_pipeline(symbol, data_source, retrain)` — runs everything end-to-end
- **Dataclasses:**
  - `PipelineResult` — holds raw data, engineered data, prediction, risk, recommendation, and errors
  - `PredictionResult` — holds bullish/bearish probabilities from all 3 ML models
  - `RiskResult` — holds risk level, cluster info, silhouette score

#### `orchestrator.py`
- Manages Streamlit session state across page navigations
- Ensures the pipeline is not re-run unnecessarily

---

### `data/`

**Purpose:** Handles everything related to raw data — loading, cleaning, and feature creation.

#### `loader.py`
- **Class:** `DataLoader`
- **Responsibilities:**
  - `load_csv(filepath)` — loads user-uploaded or local CSV files, auto-detects column names
  - `load_from_binance(symbol)` — fetches live OHLCV data from Binance API
  - `load_from_yahoo(ticker, period)` — fetches historical data from Yahoo Finance
  - `load_with_fallback(symbol)` — tries Yahoo Finance first, falls back to Binance
- **Validation:** Checks that data has at least 200 rows and all required OHLCV columns

#### `cleaner.py`
- **Class:** `DataCleaner`
- **Responsibilities:**
  - Removes duplicate rows and rows with all-null values
  - Forward-fills missing prices (common in crypto data over weekends)
  - Ensures columns are the correct numeric data types
  - Normalizes column names to lowercase

#### `feature_engineer.py`
- **Class:** `FeatureEngineer`
- **Responsibilities:** Computes 14+ technical indicators used as ML input features:
  | Indicator | Purpose |
  |---|---|
  | SMA (7, 14, 21) | Simple Moving Average — trend direction |
  | EMA (12, 26) | Exponential Moving Average — recent-weighted trend |
  | RSI (14) | Relative Strength Index — overbought/oversold signal |
  | MACD | Moving Average Convergence/Divergence — momentum |
  | Bollinger Bands | Volatility envelope around price |
  | ATR (14) | Average True Range — volatility measure |
  | OBV | On-Balance Volume — volume-price relationship |
  | Stochastic (14) | Momentum oscillator |
  | Williams %R (14) | Overbought/oversold indicator |
  | Lag features (1,3,5,7) | Previous-day price values as features |
  | Rolling returns (7,14,21) | Mean return over rolling windows |
  | `target` column | Binary label: 1 = next day up, 0 = next day down |

---

### `frontend/`

**Purpose:** All user-facing Streamlit UI — pages and reusable components.

#### `components/sidebar.py`
- Renders the left sidebar with:
  - Coin selector (BTC, ETH, BNB, SOL, ADA, DOGE, XRP)
  - Data source toggle (Live API or CSV upload)
  - "Retrain models" checkbox
  - **"🚀 Run Analysis"** button that triggers the pipeline

#### `components/charts.py`
- Builds Plotly charts reused across pages:
  - Candlestick charts with volume bars
  - Indicator overlays (RSI, MACD, Bollinger Bands)
  - Confusion matrix heatmaps
  - ROC curves

#### `components/metrics_card.py`
- Renders styled metric cards (e.g., showing accuracy %, current price)

#### `pages/page_overview.py`
- Landing page: explains the project, lists features, shows architecture summary

#### `pages/page_live_market.py`
- Real-time price ticker, 24h volume, price change %, order book snapshot

#### `pages/page_historical.py`
- Full interactive historical OHLCV chart
- Toggle overlays: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, etc.
- Date range selector

#### `pages/page_prediction.py`
- Shows XGBoost, Random Forest, and Logistic Regression predictions side by side
- Bullish/Bearish probability gauges
- Feature importance bar chart (which indicators influenced the prediction most)

#### `pages/page_risk.py`
- K-Means cluster visualization (3D scatter plot of volatility, RSI, volume)
- Current risk level badge (Low 🟢 / Medium 🟡 / High 🔴)
- Elbow curve showing optimal cluster count

#### `pages/page_recommendation.py`
- Final BUY/HOLD/SELL output with large colored badge
- Confidence level
- Suggested stop-loss and take-profit prices
- Human-readable reasoning bullet points

#### `pages/page_performance.py`
- Evaluation metrics table (Accuracy, Precision, Recall, F1, ROC-AUC) for all 3 models
- Confusion matrices
- Learning curves and cross-validation score plots

---

### `models/`

**Purpose:** All machine learning model definitions and persistence.

#### `xgboost_model.py`
- **Class:** `XGBoostModel`
- **Primary prediction model** — highest accuracy of the three
- Uses `XGBClassifier` with GridSearchCV tuning
- `train(X, y)` — trains with TimeSeriesSplit cross-validation
- `predict(X)` — returns 0 (Bearish) or 1 (Bullish)
- `predict_proba(X)` — returns probability for each class
- `get_feature_importance(feature_names)` — returns gain-based importance ranking

#### `random_forest.py`
- **Class:** `RandomForestModel`
- Ensemble of 300 decision trees
- GridSearchCV tunes `n_estimators`, `max_depth`, `min_samples_split`
- Used as a secondary prediction model alongside XGBoost

#### `logistic_regression.py`
- **Class:** `LogisticRegressionModel`
- Linear classifier — fast and interpretable
- GridSearchCV tunes regularization `C` and solver
- Used as a baseline comparison model

#### `kmeans_clustering.py`
- **Class:** `KMeansRiskClassifier`
- **Unsupervised** model — no labels needed
- Groups market conditions into 3 clusters using: volatility, RSI, volume change, daily return std
- Maps clusters to **Low / Medium / High** risk labels based on cluster centroid analysis
- Elbow method selects optimal number of clusters (k=2 to 8)
- Silhouette score measures cluster quality

#### `model_manager.py`
- **Class:** `ModelManager`
- Saves and loads trained models as `.joblib` files in `models/saved/`
- Prevents re-training on every app launch (models persist between sessions)
- `model_exists(name)` — checks if a saved model exists
- `save(model, name)` / `load(name)` — serialization helpers

---

### `services/`

**Purpose:** External API clients for fetching market data.

#### `binance_service.py`
- **Class:** `BinanceService`
- Connects to Binance public REST API (`https://api.binance.com/api/v3`)
- `get_klines(symbol, interval, limit)` — fetches OHLCV candlestick data (max 1000 candles)
- Implements **exponential backoff** retry logic (3 retries) for network failures
- No API key required for public endpoints

#### `yahoo_service.py`
- **Class:** `YahooFinanceService`
- Uses `yfinance` Python library to fetch historical data
- `get_historical(symbol, period, interval)` — supports up to 10+ years of daily data
- Primary data source for historical analysis (BTC data goes back to 2014)

#### `market_data_service.py`
- **Class:** `MarketDataService`
- Unified service used by the Live Market page
- `get_live_price(symbol)` — current price from Binance ticker
- `get_ticker_24h(symbol)` — 24h volume, high, low, price change
- `get_order_book(symbol)` — bid/ask order book depth

---

### `utils/`

**Purpose:** Shared tools used across all other modules.

#### `config.py`
- **The single source of truth** for all constants — no magic numbers anywhere else
- Defines: supported coins, API URLs, technical indicator windows, model hyperparameter grids,
  agent decision thresholds, chart colors, navigation page labels, clustering features

#### `logger.py`
- Configures Python `logging` with consistent format
- `get_logger(__name__)` — used in every module for structured log output
- Logs go to both console and `logs/` files

#### `evaluator.py`
- **Class:** `ModelEvaluator`
- Computes all ML evaluation metrics from predictions:
  - Accuracy, Precision, Recall, F1 Score, ROC-AUC
  - Confusion matrix
  - Whether performance meets the minimum 80% accuracy target

#### `feature_selector.py`
- Automated feature importance and selection utilities
- Removes low-variance or highly correlated features before training
- Helps improve model accuracy and reduce overfitting

#### `helpers.py`
- `normalize_column_names(df)` — converts all DataFrame column names to lowercase
- General-purpose formatting and data transformation utilities
- Price formatting, percentage calculation helpers

---

### `documentation/`

| File | Contents |
|---|---|
| `project_structure_guide.md` | **This file** — explains all folders and files |
| `project_report.md` | Full academic report with methodology, experiments, results |
| `architecture_diagram.md` | ASCII system architecture and data flow diagrams |
| `api_reference.md` | Every class, method, parameter, and return type documented |
| `deployment_guide.md` | How to deploy using Docker or Streamlit Cloud |
| `viva_qa.md` | 30 detailed Q&A covering design decisions and ML concepts |

---

## How the Pages Connect to the Code

```
Page Shown in Browser          ← What renders it        ← Where data comes from
─────────────────────────────────────────────────────────────────────────────
🏠 Project Overview            page_overview.py          (static content)
📡 Live Market Dashboard       page_live_market.py       market_data_service.py → Binance API
📊 Historical Analysis         page_historical.py        pipeline_result.engineered_df
🔮 Prediction Dashboard        page_prediction.py        pipeline_result.prediction
⚠️  Risk Classification        page_risk.py              pipeline_result.risk
💡 Buy/Sell/Hold Engine        page_recommendation.py    pipeline_result.recommendation
📈 Model Performance           page_performance.py       pipeline_result.evaluation_metrics
```

---

## Data Flow Summary

```
Raw API/CSV data
     ↓ loader.py
Cleaned OHLCV DataFrame
     ↓ cleaner.py
Feature-Engineered DataFrame (30+ columns)
     ↓ feature_engineer.py
     ├──► XGBoost / RF / LR  ──► Bullish/Bearish Probabilities
     └──► K-Means             ──► Risk Level (Low/Medium/High)
                 ↓
         RecommendationAgent
                 ↓
     BUY / HOLD / SELL + Stop-Loss + Take-Profit + Reasoning
```

---

*This document was auto-generated as part of the submission package for the AI-Based Cryptocurrency Market Behavior Analyzer project.*
