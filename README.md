# AI-Based Cryptocurrency Market Behavior Analyzer & Risk Predictor

![CryptoAI Banner](https://img.shields.io/badge/CryptoAI-Analyzer-00D4AA?style=for-the-badge)
![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn)

A comprehensive AI-powered dashboard that analyzes cryptocurrency market behavior using Machine Learning (Random Forest, Logistic Regression), K-Means Clustering for risk classification, and an Intelligent Agent for actionable Buy/Sell/Hold recommendations.

---

## 🌟 Key Features

1. **Live Market Dashboard**: Real-time OHLCV data from Binance (with automatic Yahoo Finance fallback), price cards, and interactive candlestick charts.
2. **Historical Analysis**: Technical indicator overlays including SMA, EMA, RSI, MACD, and Bollinger Bands with correlation heatmaps.
3. **ML Price Prediction**: Random Forest and Logistic Regression models trained to predict next-period price direction (Bullish/Bearish).
4. **Risk Classification**: Unsupervised K-Means clustering categorizes market conditions into Low, Medium, or High risk with 3D visualization.
5. **Intelligent Agent**: A rule-based engine synthesizes predictions and risk levels to generate BUY/HOLD/SELL recommendations with confidence scores and reasoning.
6. **Model Performance Tracking**: Detailed evaluation metrics (Accuracy, F1, ROC-AUC), confusion matrices, learning curves, and cross-validation scores.

---

## 🏗️ System Architecture

- **Frontend**: Streamlit multi-page application with Plotly visualizations.
- **Backend/Orchestration**: `CryptoPipeline` manages the end-to-end flow from data ingestion to recommendation.
- **Intelligence Layer**: Scikit-learn models (RF, LR, K-Means) with `joblib` persistence and `TimeSeriesSplit` cross-validation.
- **Data Layer**: Cleaners and Feature Engineers using Pandas, NumPy, and `ta` library for technical indicators.
- **Services Layer**: Unified `MarketDataService` handling Binance REST API and `yfinance` with exponential backoff.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crypto-analyzer.git
   cd crypto-analyzer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   *(Optional: Add your Binance API keys if you wish to use authenticated endpoints, though public endpoints work fine for standard analysis).*

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```

---

## 📂 Project Structure

```text
crypto_analyzer/
├── app.py                      # Main Streamlit entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── agent/                      # Intelligent recommendation agent
├── backend/                    # Pipeline and session state orchestrator
├── data/                       # Data loader, cleaner, and feature engineer
├── documentation/              # Architecture, deployment guide, report, QA
├── frontend/                   # Streamlit pages and UI components
├── models/                     # RF, LR, K-Means models and model manager
├── services/                   # Binance and Yahoo Finance API clients
└── utils/                      # Config, logging, evaluation, and helpers
```

---

## 📚 Documentation

Detailed documentation is available in the `documentation/` directory:
- [Project Report](documentation/project_report.md): Full academic/technical report detailing methodology.
- [Architecture Diagram](documentation/architecture_diagram.md): ASCII diagrams of system architecture and data flow.
- [API Reference](documentation/api_reference.md): Complete module, class, and method documentation.
- [Deployment Guide](documentation/deployment_guide.md): Instructions for Docker and Streamlit Cloud.
- [Viva Q&A](documentation/viva_qa.md): 30 common questions and answers regarding the system's design and ML concepts.

---

## ⚠️ Disclaimer

**This software is for educational and research purposes only.** It does not constitute financial advice. Cryptocurrency markets are highly volatile, and machine learning models predicting market direction carry significant risk of error. Always conduct your own research before making financial decisions.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
