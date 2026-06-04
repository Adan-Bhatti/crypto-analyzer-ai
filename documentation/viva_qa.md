# Viva Questions & Answers
## AI-Based Cryptocurrency Market Behavior Analyzer and Risk Predictor

---

## Category A: AI/ML Concepts (10 Questions)

### 1. What is the difference between supervised and unsupervised learning? How does your project use both?

Supervised learning uses labeled training data where the correct output is known, enabling the model to learn the mapping from inputs to outputs. Unsupervised learning discovers hidden patterns in unlabeled data without predefined outputs. Our project uses supervised learning through Random Forest and Logistic Regression classifiers that are trained on labeled data where the target is the next-period price direction (1=Bullish, 0=Bearish). We use unsupervised learning through K-Means clustering, which groups market conditions into three risk categories (Low, Medium, High) without any predefined risk labels. The clustering model discovers natural groupings based on volatility, RSI, volume change, and daily return standard deviation features.

### 2. Why did you choose Random Forest over a single Decision Tree?

A single Decision Tree is prone to overfitting — it can memorize training data noise, leading to poor generalization on unseen data. Random Forest mitigates this by building 200 individual trees, each trained on a bootstrapped sample of the data with random feature subsets at each split. This ensemble approach, called bagging (Bootstrap AGGregatING), averages out the variance of individual trees while preserving their low bias. In our experiments, a single Decision Tree achieved approximately 65-70% accuracy, while the Random Forest ensemble achieved over 80% by cancelling out the overfitting tendencies of individual trees. Additionally, Random Forest provides reliable feature importance scores via the mean decrease in Gini impurity across all trees, which we display on the dashboard.

### 3. Explain how K-Means clustering works. What is the time complexity?

K-Means works through iterative refinement: (1) Initialize k centroids randomly, (2) Assign each data point to the nearest centroid based on Euclidean distance, (3) Recompute each centroid as the mean of all assigned points, (4) Repeat steps 2-3 until convergence (centroids stop moving significantly). In our project, k=3 represents Low, Medium, and High risk categories. The features used are volatility_14, rsi_14, volume_change, and daily_return_std, all standardized with StandardScaler before clustering. The time complexity is O(n × k × d × i) where n is the number of data points, k is the number of clusters, d is the dimensionality (4 features), and i is the number of iterations. With n_init=10, we run the algorithm 10 times with different random initializations and keep the best result.

### 4. What is the curse of dimensionality and how did you address it?

The curse of dimensionality refers to the phenomenon where the feature space becomes increasingly sparse as the number of dimensions grows, making it harder for distance-based algorithms to find meaningful patterns. In high-dimensional spaces, all data points tend to be equidistant from each other, degrading the performance of algorithms like K-Means and KNN. We address this through our FeatureSelector module, which uses correlation-based selection (removing features with < 5% correlation with the target) and inter-correlation filtering (removing redundant features with > 90% mutual correlation). For K-Means specifically, we use only 4 carefully chosen clustering features rather than the full 15+ feature set, keeping the dimensionality manageable.

### 5. Why is TimeSeriesSplit used instead of random train-test split for financial data?

Random train-test split would create look-ahead bias — the model could be trained on data from, say, March 2024 and tested on data from January 2024, effectively learning from the future to predict the past. Financial data has a strict temporal ordering where past events influence future prices but not vice versa. TimeSeriesSplit ensures that training data always precedes test data chronologically. With n_splits=5, we create 5 folds where each successive fold uses more training data and tests on the immediately following time period. This provides a realistic assessment of how the model would perform in production, where it must predict future unseen data using only historical information.

### 6. What is overfitting? How did you prevent it in your Random Forest model?

Overfitting occurs when a model learns the noise and random fluctuations in the training data rather than the underlying patterns, resulting in excellent training performance but poor test performance. We prevent overfitting in our Random Forest through four mechanisms: (1) Bagging — each tree sees a different bootstrapped sample, preventing any single tree from memorizing the full dataset, (2) Feature randomization — each split considers only a random subset of features, reducing tree correlation, (3) max_depth=10 limits tree complexity, preventing excessively deep trees that could memorize individual data points, (4) GridSearchCV with TimeSeriesSplit cross-validation selects hyperparameters that generalize well rather than overfit to any single train/test split.

### 7. Explain Gini impurity and how it drives splits in Random Forest.

Gini impurity measures the probability that a randomly chosen sample from a node would be incorrectly classified if labeled randomly according to the node's class distribution. It is calculated as G = 1 - Σ(p_i²) where p_i is the proportion of class i in the node. A pure node (all samples from one class) has Gini = 0, and maximum impurity for binary classification is 0.5. At each split in a Decision Tree, the algorithm tries all possible feature/threshold combinations and selects the one that produces the largest reduction in weighted Gini impurity between parent and child nodes. In our project, features like RSI and MACD that best separate bullish from bearish conditions produce the largest Gini reductions and therefore rank highest in feature importance.

### 8. What is the silhouette score and why does it matter for K-Means?

The silhouette score measures how similar a data point is to its own cluster compared to other clusters. For each point, it computes s = (b - a) / max(a, b), where a is the average distance to other points in the same cluster (cohesion) and b is the average distance to points in the nearest other cluster (separation). Scores range from -1 to 1: values near 1 indicate well-clustered data, near 0 indicate overlapping clusters, and negative values indicate misclassification. In our project, we target a silhouette score > 0.4, which we display on the Risk Classification page. It validates that our k=3 clustering produces meaningful separation of market conditions into distinct risk categories rather than arbitrary groupings.

### 9. How does class imbalance affect classification? How did you handle it?

Class imbalance occurs when one class significantly outnumbers the other in the training data. In cryptocurrency markets, bullish and bearish periods are not always equally distributed — extended bull markets create datasets with more positive (1) labels than negative (0) labels. This can cause the classifier to develop a bias toward the majority class, predicting bullish for most inputs simply because it appeared more frequently in training. We handle this by setting `class_weight='balanced'` in both Random Forest and Logistic Regression, which automatically adjusts sample weights inversely proportional to class frequencies. This ensures the minority class has equal influence on the loss function during training.

### 10. What is cross-validation and why is it important for model reliability?

Cross-validation partitions the dataset into k folds and trains/tests the model k times, each time using a different fold as the test set and the remaining folds for training. This provides k performance estimates rather than a single train/test split estimate, giving a more robust assessment of model generalization. We use TimeSeriesSplit(n_splits=5), which creates 5 chronologically ordered folds. The mean and standard deviation of the cross-validation scores indicate both the expected performance and its stability. High variance across folds would suggest the model is sensitive to specific time periods, while consistent scores indicate reliable generalization. We display cross-validation results as a box plot on the Model Performance page.

---

## Category B: System Design (10 Questions)

### 11. Describe the overall system architecture and data flow.

The system follows a 6-layer architecture. At the base, the Services Layer (Binance API + Yahoo Finance) fetches raw OHLCV data from external sources. The Data Layer (Loader → Cleaner → Feature Engineer) processes this raw data into feature-engineered DataFrames. The Intelligence Layer contains three components: Random Forest and Logistic Regression classifiers for prediction, K-Means clustering for risk classification, and a Recommendation Agent for decision synthesis. The Application Layer (CryptoPipeline + Orchestrator) orchestrates the end-to-end flow and manages Streamlit session state. The Presentation Layer consists of 7 Streamlit pages rendering interactive Plotly charts. Data flows bottom-up: API → DataFrame → Features → Predictions + Risk → Recommendation → Dashboard.

### 12. Why is a fallback mechanism important in your data service layer?

The fallback mechanism (Binance → Yahoo Finance) ensures the system remains functional even when one data source is unavailable. Binance API can be blocked by firewalls, rate-limited, or experience regional outages. Without fallback, any API disruption would render the entire application useless. Our MarketDataService first attempts Binance with exponential backoff retry (3 attempts), and on failure, transparently switches to Yahoo Finance. The user is informed which source was used but the analysis proceeds uninterrupted. This design pattern follows the "graceful degradation" principle, maintaining core functionality under adverse conditions.

### 13. How does the Intelligent Agent differ from a simple if-else function?

While the implementation uses conditional logic, it qualifies as an intelligent agent because it follows the agent architecture paradigm: it has clearly defined percepts (bullish probability, bearish probability, risk level, current price, model confidence), actions (BUY, HOLD, SELL), a decision table that maps percepts to actions, and an environment (the cryptocurrency market). The agent exhibits bounded rationality by making optimal decisions within its knowledge scope. Unlike a simple if-else, it generates structured output (RecommendationResult dataclass) with confidence scoring, human-readable reasoning chains, and suggested stop-loss/take-profit levels. The thresholds are configurable through config.py, making the agent's behavior tunable without code changes.

### 14. What design patterns did you apply?

**Pipeline Pattern**: The CryptoPipeline class chains data loading → cleaning → feature engineering → training → prediction → risk → recommendation in a single `run_full_pipeline()` call. **Factory Pattern**: The charts.py module provides factory functions (candlestick_chart, rsi_chart, etc.) that encapsulate Plotly figure creation. **Strategy Pattern**: The DataCleaner supports multiple missing value strategies ("ffill", "bfill", "mean", "drop") selected at runtime. **Facade Pattern**: MarketDataService provides a simplified unified interface over two complex data sources (Binance and Yahoo). **Singleton-like State**: The Orchestrator uses `st.session_state` to maintain a single pipeline instance across Streamlit reruns.

### 15. Why did you separate frontend, backend, models, and services into different modules?

This separation follows the Single Responsibility Principle (SRP) and enables: (1) Independent development — the frontend can be redesigned without touching ML code, (2) Testability — each module can be unit-tested in isolation, (3) Reusability — the models module can be imported into a Jupyter notebook for research, (4) Maintainability — a bug in the Binance service doesn't require understanding the entire codebase, (5) Scalability — the services layer could be extracted into a microservice without restructuring the codebase. This layered architecture is standard practice in production software engineering.

### 16. How would you scale this system to handle 1000 users simultaneously?

Currently, the application runs as a single-user Streamlit instance. To scale: (1) Deploy behind a load balancer with multiple Streamlit instances, (2) Move model training to a background job queue (Celery + Redis) so it doesn't block the UI, (3) Cache trained models in a shared store (Redis or S3) instead of local joblib files, (4) Replace synchronous API calls with async (httpx/aiohttp) to handle concurrent requests, (5) Use a CDN for static assets, (6) Implement rate limiting per user, (7) Pre-compute predictions on a schedule rather than on-demand, (8) Consider migrating the frontend to a React/FastAPI architecture for better concurrency handling.

### 17. What is the purpose of model_manager.py? Why serialize models?

ModelManager handles saving, loading, listing, and deleting trained models using joblib serialization. Serialization (saving model objects to disk) serves several purposes: (1) Avoiding redundant retraining — once a model achieves satisfactory accuracy, it can be saved and loaded instantly on subsequent runs, (2) Deployment — serialized models can be deployed without the training data or training code, (3) Versioning — different model versions can be saved and compared, (4) Session persistence — Streamlit reruns the script on each interaction; loading a saved model avoids re-training on every page navigation.

### 18. How does your feature engineering pipeline ensure no data leakage?

Data leakage occurs when information from the test set or future data points influences training. Our pipeline prevents this through: (1) The target label uses `shift(-1)` on the close price, and we drop the last row where the target would be NaN, ensuring no future-looking label construction, (2) All technical indicators (SMA, EMA, RSI, MACD, Bollinger) use only past/current data — they are computed with rolling windows that look backward, never forward, (3) We drop NaN rows at the beginning (from indicator warm-up periods) rather than imputing them with future values, (4) TimeSeriesSplit ensures training data chronologically precedes test data, (5) StandardScaler in Logistic Regression is fit only on training data and applied to test data via `transform()`.

### 19. Explain the role of config.py in maintaining clean architecture.

config.py centralizes all configurable parameters, thresholds, and constants. This provides: (1) Single source of truth — changing a threshold (e.g., buy probability from 70% to 75%) requires editing only one file, (2) No magic numbers — every numeric constant in business logic references a named variable from config.py, making the code self-documenting, (3) Environment flexibility — different configurations can be used for development, testing, and production, (4) Discoverability — all tunable parameters are visible in one place, making it easy for reviewers to understand the system's behavior, (5) Type safety — all constants have type annotations.

### 20. How would you add a new cryptocurrency coin to the system?

Adding a new coin requires only configuration changes, demonstrating the system's extensibility: (1) Add the Binance symbol to `SUPPORTED_COINS` in config.py (e.g., "DOTUSDT"), (2) Add the Yahoo Finance ticker mapping to `YAHOO_TICKERS` (e.g., "DOTUSDT": "DOT-USD"), (3) Add the display name to `COIN_DISPLAY_NAMES` (e.g., "DOTUSDT": "Polkadot (DOT)"). No code changes are required — the sidebar dropdown, data fetching, and analysis pipeline automatically support the new coin. This is a direct benefit of centralizing configuration.

---

## Category C: Technical / Financial (10 Questions)

### 21. What is RSI and what does a value above 70 indicate?

RSI (Relative Strength Index) is a momentum oscillator that measures the speed and magnitude of recent price changes on a scale of 0 to 100. It is calculated using the ratio of average gains to average losses over a 14-period window. An RSI above 70 indicates that the asset is "overbought" — it has experienced strong buying pressure and may be due for a price pullback or reversal. In our project, we display horizontal reference lines at 70 (overbought) and 30 (oversold) on the RSI chart, and the agent considers RSI as part of the risk classification features via the K-Means clustering.

### 22. Explain MACD and how the crossover signal works.

MACD (Moving Average Convergence Divergence) consists of three components: the MACD line (12-period EMA minus 26-period EMA), the Signal line (9-period EMA of the MACD line), and the Histogram (MACD minus Signal). A bullish crossover occurs when the MACD line crosses above the Signal line, suggesting upward momentum. A bearish crossover occurs when the MACD line crosses below the Signal line, suggesting downward momentum. In our project, we use the MACD difference (macd_diff) as a feature for the classification models, and the MACD chart is displayed on the Historical Analysis page with both lines and the histogram bars.

### 23. What are Bollinger Bands and how do they measure volatility?

Bollinger Bands consist of three lines: a middle band (20-period SMA), an upper band (middle + 2 standard deviations), and a lower band (middle − 2 standard deviations). The width between the bands dynamically adjusts based on market volatility — wider bands indicate higher volatility, narrower bands indicate lower volatility (a "squeeze"). When prices touch or exceed the upper band, it may indicate overbought conditions; touching the lower band may indicate oversold conditions. In our project, we display Bollinger Bands as an overlay on the Historical Analysis page with a shaded region between the bands.

### 24. Why is volatility an important feature for risk classification?

Volatility measures the degree of price variation over time and is the primary determinant of investment risk. High volatility means larger potential gains but also larger potential losses. In cryptocurrency markets, volatility can change dramatically — calm periods can suddenly shift to extreme price swings triggered by news, regulatory changes, or whale activity. Our K-Means clustering uses 14-period rolling volatility (standard deviation of daily returns) as the primary feature for risk classification. By sorting cluster centers by mean volatility, we ensure that the cluster with the highest average volatility is labeled "High Risk," providing a meaningful risk categorization.

### 25. What is the difference between SMA and EMA? When is EMA preferred?

SMA (Simple Moving Average) gives equal weight to all data points in the window — each of the last N prices contributes 1/N to the average. EMA (Exponential Moving Average) assigns exponentially decreasing weights to older data points, giving more influence to recent prices. EMA is preferred when responsiveness to recent price changes is important, such as in short-term trading strategies or when identifying trend reversals quickly. In our project, we use both: SMA (7/14/21 periods) for broader trend identification and EMA (12/26 periods) as components of the MACD indicator and for faster-reacting trend signals.

### 26. Why is cryptocurrency price prediction considered a hard problem?

Cryptocurrency price prediction is challenging for several reasons: (1) Markets are 24/7 with no breaks, generating continuous data streams, (2) Prices are influenced by unpredictable events — tweets, regulatory announcements, exchange hacks, (3) High noise-to-signal ratio makes pattern recognition difficult, (4) Non-stationarity — statistical properties of the price series change over time, (5) Market microstructure effects — wash trading and manipulation distort price signals, (6) Efficient Market Hypothesis suggests that historical prices already reflect available information. Our project acknowledges these limitations by predicting only direction (not exact price), using conservative confidence scoring, and including clear disclaimers.

### 27. What is a candlestick chart and what information does it encode?

A candlestick chart is a financial visualization where each "candle" represents one time period (e.g., one day). Each candle encodes four prices: Open (start of period), High (maximum during period), Low (minimum during period), and Close (end of period). The body of the candle spans from Open to Close — a green/hollow body indicates Close > Open (bullish), while a red/filled body indicates Close < Open (bearish). The thin lines above and below the body (wicks/shadows) show the High and Low. In our project, we render candlestick charts using Plotly's `go.Candlestick` with green (#00D4AA) for bullish and red (#FF4444) for bearish candles.

### 28. How would you backtest the Buy/Sell/Hold recommendations?

Backtesting would simulate applying the agent's recommendations historically to assess profitability. The approach would be: (1) Run the pipeline on historical data up to each date t, (2) Record the agent's recommendation at date t, (3) Simulate a trade: if BUY, assume long position at close price; if SELL, close any open position, (4) Track portfolio value over time using actual future prices, (5) Compute metrics: total return, Sharpe ratio, maximum drawdown, win rate, and compare against a simple buy-and-hold strategy. This is listed as a future enhancement (#5) in our project report.

### 29. What are the ethical concerns with building trading recommendation systems?

Key ethical concerns include: (1) User reliance — inexperienced users may follow recommendations without understanding the risks, potentially losing money, (2) False confidence — displaying high model accuracy may create an illusion of certainty in inherently uncertain markets, (3) Regulatory compliance — in many jurisdictions, providing personalized trading recommendations requires financial advisor licensing, (4) Market impact — if widely adopted, such systems could create herding behavior, amplifying market movements, (5) Bias — models trained on specific market conditions may perform poorly in different regimes. Our project addresses these concerns by prominently displaying disclaimers that the tool is for educational purposes only and does not constitute financial advice.

### 30. If the model accuracy drops to 65%, what steps would you take to diagnose and fix it?

Diagnostic steps: (1) Check for concept drift — the statistical properties of recent data may differ from training data; compare feature distributions between train and test sets, (2) Examine the confusion matrix — is the model biased toward one class? If so, adjust class weights, (3) Review feature importance — if top features have changed, the market regime may have shifted, (4) Check for data quality issues — API errors, missing values, or outliers that weren't properly cleaned, (5) Inspect the train/test split — ensure no data leakage. Remediation: (a) Retrain on more recent data, (b) Expand the hyperparameter grid search, (c) Add new features (e.g., volume-weighted indicators), (d) Try a different model architecture (e.g., Gradient Boosting, LSTM), (e) Increase the training window, (f) Implement walk-forward optimization.
