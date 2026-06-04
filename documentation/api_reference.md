# API Reference
## AI-Based Cryptocurrency Market Behavior Analyzer and Risk Predictor

---

## Data Layer

### `data.loader.DataLoader`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `load_csv(filepath)` | `filepath: str` | `pd.DataFrame` | Load OHLCV data from a CSV file. Auto-detects column names (case-insensitive). |
| `load_from_binance(symbol, interval, limit)` | `symbol: str`, `interval: str = "1d"`, `limit: int = 500` | `pd.DataFrame` | Fetch candlestick data from Binance REST API. |
| `load_from_yahoo(ticker, period, interval)` | `ticker: str`, `period: str = "1y"`, `interval: str = "1d"` | `pd.DataFrame` | Fetch historical data from Yahoo Finance. |
| `load_with_fallback(symbol)` | `symbol: str` | `pd.DataFrame` | Try Binance first, fall back to Yahoo Finance on failure. |

**Exceptions:** `InsufficientDataError` (< 100 rows), `DataLoadError` (all sources failed)

---

### `data.cleaner.DataCleaner`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `remove_duplicates(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Remove duplicate rows. |
| `handle_missing_values(df, strategy)` | `df: pd.DataFrame`, `strategy: str = "ffill"` | `pd.DataFrame` | Handle NaN values. Strategies: "ffill", "bfill", "mean", "drop". |
| `remove_outliers(df, z_threshold)` | `df: pd.DataFrame`, `z_threshold: float = 3.0` | `pd.DataFrame` | Remove rows with z-scores exceeding threshold on OHLCV columns. |
| `normalize_columns(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Lowercase column names and cast OHLCV to float. |
| `validate_ohlcv(df)` | `df: pd.DataFrame` | `bool` | Check High ≥ Low, Volume ≥ 0, all required columns present. |
| `clean(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Full pipeline: normalize → dedup → fill → outliers → validate. |

---

### `data.feature_engineer.FeatureEngineer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_sma(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Add SMA columns: `sma_7`, `sma_14`, `sma_21`. |
| `add_ema(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Add EMA columns: `ema_12`, `ema_26`. |
| `add_rsi(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Add `rsi_14` column. |
| `add_macd(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Add `macd`, `macd_signal`, `macd_diff` columns. |
| `add_bollinger_bands(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Add `bb_upper`, `bb_lower`, `bb_middle` columns. |
| `add_volume_features(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Add `volume_change` column. |
| `add_volatility(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Add `daily_return`, `volatility_14`, `daily_return_std`, `price_momentum`. |
| `add_target_label(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Add `target` column (1 if next Close > current Close, else 0). |
| `engineer_all(df)` | `df: pd.DataFrame` | `pd.DataFrame` | Apply all above methods and drop NaN rows. |

---

## Services Layer

### `services.binance_service.BinanceService`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_klines(symbol, interval, limit)` | `symbol: str`, `interval: str = "1d"`, `limit: int = 500` | `pd.DataFrame` | Fetch OHLCV candles from Binance. |
| `get_ticker_price(symbol)` | `symbol: str` | `float` | Get current market price. |
| `get_24hr_stats(symbol)` | `symbol: str` | `dict` | Get 24-hour rolling statistics. |
| `get_supported_symbols()` | — | `list[str]` | List all supported trading symbols. |

---

### `services.yahoo_service.YahooFinanceService`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_historical(symbol, period, interval)` | `symbol: str`, `period: str = "1y"`, `interval: str = "1d"` | `pd.DataFrame` | Fetch historical OHLCV data. |
| `get_live_price(symbol)` | `symbol: str` | `float` | Get current market price. |
| `get_info(symbol)` | `symbol: str` | `dict` | Get cryptocurrency metadata. |

---

### `services.market_data_service.MarketDataService`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_data(symbol, interval, limit)` | `symbol: str`, `interval: str = "1d"`, `limit: int = 500` | `pd.DataFrame` | Unified data fetch (Binance → Yahoo fallback). |
| `get_live_price(symbol)` | `symbol: str` | `dict` | Live price with source tracking. Returns `{price, source, timestamp}`. |
| `get_24hr_stats(symbol)` | `symbol: str` | `dict` | 24hr stats (Binance only, graceful fallback). |

**Property:** `source_used: str` — tracks which data source was used in the last call.

---

## Models Layer

### `models.random_forest.RandomForestModel`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `train(X_train, y_train)` | `X_train: np.ndarray`, `y_train: np.ndarray` | `None` | Train with GridSearchCV + TimeSeriesSplit(5). |
| `predict(X)` | `X: np.ndarray` | `np.ndarray` | Predict class labels (0=Bearish, 1=Bullish). |
| `predict_proba(X)` | `X: np.ndarray` | `np.ndarray` | Predict class probabilities [bearish, bullish]. |
| `get_feature_importance(feature_names)` | `feature_names: list[str]` | `pd.DataFrame` | Feature importances (Gini) sorted descending. |
| `save(path)` / `load(path)` | `path: str` | `None` | Joblib serialization. |

**Properties:** `best_params`, `training_time`, `is_trained`

---

### `models.logistic_regression.LogisticRegressionModel`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `train(X_train, y_train)` | `X_train: np.ndarray`, `y_train: np.ndarray` | `None` | Train with StandardScaler preprocessing. |
| `predict(X)` | `X: np.ndarray` | `np.ndarray` | Predict class labels. |
| `predict_proba(X)` | `X: np.ndarray` | `np.ndarray` | Predict class probabilities. |
| `save(path)` / `load(path)` | `path: str` | `None` | Saves model + scaler together. |

---

### `models.kmeans_clustering.KMeansRiskClassifier`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `fit(df)` | `df: pd.DataFrame` | `None` | Fit K-Means (k=3) on clustering features. |
| `predict_risk(df)` | `df: pd.DataFrame` | `pd.Series` | Predict risk levels ("Low"/"Medium"/"High"). |
| `get_cluster_centers()` | — | `pd.DataFrame` | Cluster centers in original feature space. |
| `map_cluster_to_label(cluster_id)` | `cluster_id: int` | `str` | Map cluster ID to risk label. |
| `get_risk_distribution()` | — | `dict[str, int]` | Distribution of data across risk levels. |
| `get_elbow_inertias()` | — | `list[float]` | Inertia values for k=2..8 (elbow plot). |
| `save(path)` / `load(path)` | `path: str` | `None` | Saves model, scaler, and risk mapping. |

**Properties:** `silhouette`, `is_fitted`

---

### `models.model_manager.ModelManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `save_model(model, name)` | `model: object`, `name: str` | `str` | Save model to disk. Returns filepath. |
| `load_model(name)` | `name: str` | `object` | Load model from disk. |
| `model_exists(name)` | `name: str` | `bool` | Check if a saved model exists. |
| `list_saved_models()` | — | `list[str]` | List all saved model names. |
| `delete_model(name)` | `name: str` | `None` | Delete a saved model. |

---

## Agent Layer

### `agent.recommendation_agent.RecommendationAgent`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generate_recommendation(bullish_prob, bearish_prob, risk_level, current_price, model_confidence)` | `float, float, str, float, float` | `RecommendationResult` | Generate BUY/HOLD/SELL recommendation. |
| `get_reasoning()` | — | `list[str]` | Get reasoning from last recommendation. |
| `get_confidence_score()` | — | `float` | Get confidence score from last recommendation. |

### `RecommendationResult` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `action` | `str` | "BUY", "HOLD", or "SELL" |
| `confidence` | `str` | "High", "Medium", or "Low" |
| `bullish_prob` | `float` | Bullish probability |
| `bearish_prob` | `float` | Bearish probability |
| `risk_level` | `str` | Risk classification |
| `reasoning` | `list[str]` | 3-5 reasoning bullet points |
| `timestamp` | `datetime` | When the recommendation was generated |
| `suggested_stop_loss` | `float` | Suggested stop-loss price |
| `suggested_take_profit` | `float` | Suggested take-profit price |

---

## Backend Layer

### `backend.pipeline.CryptoPipeline`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run_full_pipeline(symbol, data_source, csv_path, retrain)` | Various | `PipelineResult` | End-to-end pipeline. |
| `run_prediction_only(df)` | `df: pd.DataFrame` | `PredictionResult` | Prediction using trained models. |
| `run_risk_classification(df)` | `df: pd.DataFrame` | `RiskResult` | K-Means risk classification. |
| `get_pipeline_status()` | — | `dict` | Current pipeline state. |

---

## Utilities Layer

### `utils.evaluator.ModelEvaluator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `compute_metrics(y_true, y_pred, y_proba)` | Arrays | `EvaluationMetrics` | All classification metrics. |
| `compute_confusion_matrix(y_true, y_pred)` | Arrays | `np.ndarray` | 2×2 confusion matrix. |
| `compute_roc_auc(y_true, y_proba)` | Arrays | `float` | ROC-AUC score. |
| `cross_validate_model(model, X, y, n_splits)` | Various | `dict` | Per-fold CV scores. |
| `generate_classification_report(y_true, y_pred)` | Arrays | `str` | Text classification report. |
| `plot_confusion_matrix(cm)` | `cm: np.ndarray` | `go.Figure` | Plotly confusion matrix heatmap. |
| `plot_roc_curve(y_true, y_proba, label)` | Various | `go.Figure` | Plotly ROC curve. |

---

## Chart Factory Functions (`frontend.components.charts`)

All functions return `go.Figure` with `plotly_dark` template and `#00D4AA` accent.

| Function | Parameters | Description |
|----------|-----------|-------------|
| `candlestick_chart(df, title)` | DataFrame, str | OHLCV candlestick with volume subplot |
| `line_chart_with_ma(df, mas, title)` | DataFrame, list, str | Price line with MA overlays |
| `rsi_chart(df, title)` | DataFrame, str | RSI with 70/30 reference lines |
| `macd_chart(df, title)` | DataFrame, str | MACD + Signal + Histogram |
| `bollinger_chart(df, title)` | DataFrame, str | Price with Bollinger Bands |
| `correlation_heatmap(df, title)` | DataFrame, str | Feature correlation matrix |
| `risk_distribution_pie(risk_counts, title)` | dict, str | Risk level pie chart |
| `feature_importance_bar(importances, top_n, title)` | DataFrame, int, str | Horizontal bar chart |
| `confusion_matrix_heatmap(cm, labels, title)` | ndarray, list, str | CM heatmap |
| `roc_curve_plot(fpr, tpr, auc_score, label)` | arrays, float, str | ROC curve |
| `cluster_scatter_3d(df, title)` | DataFrame, str | 3D K-Means scatter |
| `probability_gauge(bullish_prob, title)` | float, str | Gauge indicator |
| `elbow_plot(inertias, title)` | list, str | Inertia vs k plot |
| `volume_bar_chart(df, title)` | DataFrame, str | Volume bars |
| `prediction_history_line(history, title)` | list, str | Prediction timeline |
