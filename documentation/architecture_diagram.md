# System Architecture Diagram
## AI-Based Cryptocurrency Market Behavior Analyzer and Risk Predictor

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     USER (Web Browser)                              │
│                    http://localhost:8501                             │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                                │
│                                                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐      │
│  │  Page 1    │ │  Page 2    │ │  Page 3    │ │  Page 4    │      │
│  │  Overview  │ │  Live Mkt  │ │ Historical │ │ Prediction │      │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                     │
│  │  Page 5    │ │  Page 6    │ │  Page 7    │                     │
│  │   Risk     │ │  Buy/Sell  │ │   Model    │                     │
│  │  Classify  │ │   /Hold    │ │   Perf.    │                     │
│  └────────────┘ └────────────┘ └────────────┘                     │
│                                                                     │
│  COMPONENTS:  sidebar.py │ charts.py │ metrics_card.py             │
│  FRAMEWORK:   Streamlit + Plotly                                    │
├─────────────────────────────────────────────────────────────────────┤
│                   APPLICATION LAYER                                 │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     Orchestrator                             │   │
│  │   - Session state management                                │   │
│  │   - Model/result persistence across pages                   │   │
│  │   - Prediction & recommendation history                     │   │
│  └─────────────────────┬───────────────────────────────────────┘   │
│                        │                                            │
│  ┌─────────────────────▼───────────────────────────────────────┐   │
│  │                   CryptoPipeline                             │   │
│  │   run_full_pipeline() → PipelineResult                      │   │
│  │   Data → Clean → Features → Train → Predict → Risk → Agent │   │
│  └─────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                   INTELLIGENCE LAYER                                │
│                                                                     │
│  ┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │ RandomForest  │  │ LogisticRegress. │  │ KMeansRisk       │    │
│  │ Classifier    │  │ (Baseline)       │  │ Classifier       │    │
│  │               │  │                  │  │                  │    │
│  │ - GridSearchCV│  │ - StandardScaler │  │ - k=3 clusters   │    │
│  │ - 200 trees   │  │ - Balanced wts   │  │ - Elbow method   │    │
│  │ - TimeSeriesCV│  │ - C=1.0          │  │ - Silhouette     │    │
│  │ - Gini import.│  │                  │  │ - Risk mapping   │    │
│  └───────────────┘  └──────────────────┘  └──────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              RecommendationAgent                             │   │
│  │   - Decision table (Bull% × Risk → Action)                  │   │
│  │   - Risk modifiers                                           │   │
│  │   - Stop-loss / take-profit calculation                      │   │
│  │   - Human-readable reasoning generation                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                   DATA LAYER                                        │
│                                                                     │
│  ┌───────────┐  ┌───────────┐  ┌──────────────────────────┐       │
│  │ DataLoader│  │DataCleaner│  │   FeatureEngineer        │       │
│  │           │  │           │  │                          │       │
│  │ - CSV     │  │ - Dedup   │  │ - SMA (7,14,21)         │       │
│  │ - Binance │  │ - FFill   │  │ - EMA (12,26)           │       │
│  │ - Yahoo   │  │ - Z-score │  │ - RSI (14)              │       │
│  │ - Fallback│  │ - Validate│  │ - MACD (12,26,9)        │       │
│  └───────────┘  └───────────┘  │ - Bollinger Bands       │       │
│                                 │ - Volatility, Momentum  │       │
│                                 │ - Target Label           │       │
│                                 └──────────────────────────┘       │
├─────────────────────────────────────────────────────────────────────┤
│                   SERVICES LAYER                                    │
│                                                                     │
│  ┌───────────────────┐   ┌───────────────────┐                     │
│  │  BinanceService   │   │ YahooFinService   │                     │
│  │  (Primary)        │──▶│ (Fallback)        │                     │
│  │                   │   │                   │                     │
│  │ - Public REST API │   │ - yfinance lib    │                     │
│  │ - Exp. backoff    │   │ - No auth needed  │                     │
│  │ - No auth needed  │   │                   │                     │
│  └───────┬───────────┘   └───────┬───────────┘                     │
│          │                       │                                  │
│  ┌───────▼───────────────────────▼───────────────────────────┐     │
│  │              MarketDataService (Unified)                   │     │
│  │   get_data() → tries Binance → falls back to Yahoo        │     │
│  │   get_live_price() → with source tracking                 │     │
│  └───────────────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────────────┤
│                   UTILITIES LAYER                                   │
│                                                                     │
│  config.py │ logger.py │ helpers.py │ evaluator.py │ feature_sel. │
│                                                                     │
│  - Centralized constants     - Structured logging                   │
│  - Model thresholds          - Price formatting                     │
│  - API configuration         - Evaluation metrics                   │
│  - UI styling tokens         - Feature selection                    │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                                 │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐   │
│  │  Binance API     │  │  Yahoo Finance   │  │  Local CSV     │   │
│  │  api.binance.com │  │  via yfinance    │  │  data/sample/  │   │
│  └──────────────────┘  └──────────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
         ┌──────────┐
         │  User    │
         │ Selects  │
         │  Coin    │
         └────┬─────┘
              │
              ▼
    ┌─────────────────┐      ┌────────────┐
    │  MarketData     │─────▶│  Binance   │
    │  Service        │      │  API       │
    │                 │      └────────────┘
    │  (Fallback) ────│─────▶┌────────────┐
    │                 │      │  Yahoo     │
    └────────┬────────┘      │  Finance   │
             │               └────────────┘
             ▼
    ┌─────────────────┐
    │  DataCleaner    │  Remove duplicates, fill NaN, remove outliers
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │FeatureEngineer  │  +15 technical indicators + target label
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  ML Models      │
    │  ┌───────────┐  │
    │  │    RF     ├──┼──▶ Bullish/Bearish Prediction + Probabilities
    │  └───────────┘  │
    │  ┌───────────┐  │
    │  │    LR     ├──┼──▶ Baseline Comparison
    │  └───────────┘  │
    │  ┌───────────┐  │
    │  │  K-Means  ├──┼──▶ Risk Level (Low/Medium/High)
    │  └───────────┘  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Recommendation  │  BUY / HOLD / SELL + Confidence + Reasoning
    │    Agent        │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │   Dashboard     │  7 interactive pages with Plotly charts
    └─────────────────┘
```

---

## Module Dependency Graph

```
app.py
├── frontend/components/sidebar.py
│   └── utils/config.py
├── frontend/pages/page_*.py (7 pages)
│   ├── frontend/components/charts.py
│   │   └── utils/config.py
│   ├── frontend/components/metrics_card.py
│   │   └── utils/helpers.py
│   └── services/market_data_service.py
├── backend/pipeline.py
│   ├── data/loader.py
│   ├── data/cleaner.py
│   ├── data/feature_engineer.py
│   ├── models/random_forest.py
│   ├── models/logistic_regression.py
│   ├── models/kmeans_clustering.py
│   ├── models/model_manager.py
│   ├── agent/recommendation_agent.py
│   └── utils/evaluator.py
└── backend/orchestrator.py
    └── backend/pipeline.py
```
