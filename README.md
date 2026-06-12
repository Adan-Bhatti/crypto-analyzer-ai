<div align="center">

# 📈 Crypto Analyzer AI

**An AI-powered cryptocurrency market behavior analyzer and risk predictor — featuring real-time dashboards, ML price prediction, and intelligent Buy/Sell/Hold recommendations.**

[![CI](https://github.com/Adan-Bhatti/crypto-analyzer-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Adan-Bhatti/crypto-analyzer-ai/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📊 **Live Market Dashboard** | Real-time and historical OHLCV data from Yahoo Finance and Binance API |
| 📉 **Technical Analysis** | 14+ indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV, Stochastic, Williams %R |
| 🤖 **ML Price Prediction** | XGBoost, Random Forest and Logistic Regression with GridSearchCV tuning |
| 🎯 **Risk Classification** | Unsupervised K-Means clustering → Low / Medium / High risk with 3D visualization |
| 💡 **Intelligent Agent** | Rule-based engine generates BUY / HOLD / SELL signals with confidence scores |
| 📋 **Model Evaluation** | Accuracy, F1, ROC-AUC, confusion matrices, learning curves, cross-validation |

---

## 🏗️ System Architecture

```
+------------------------------------------+
|          Streamlit Frontend              |
|   (Multi-page App + Plotly Charts)       |
+--------------------+---------------------+
                     |
+--------------------v---------------------+
|          CryptoPipeline Backend          |
|   (Orchestration + Session State)        |
+------+-------------+------------+--------+
       |             |            |
  +----v----+   +----v----+  +---v------+
  | Data    |   |  ML     |  |  Agent   |
  | Layer   |   | Models  |  |  Layer   |
  | Pandas/ |   | XGB/RF/ |  | Buy/Hold/|
  | NumPy   |   | LR/KMeans  | Sell Recs|
  +---------+   +---------+  +----------+
       |
  +----v--------------------+
  |   Services Layer        |
  | Binance + yfinance      |
  +-------------------------+
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Adan-Bhatti/crypto-analyzer-ai.git
cd crypto-analyzer-ai

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Optional: add your Binance API keys for authenticated endpoints

# 5. (Optional) Download full historical datasets
python download_datasets.py

# 6. Launch the app
streamlit run app.py
```

The dashboard will open at **http://localhost:8501**

---

## 📁 Project Structure

```
crypto-analyzer-ai/
├── app.py                    # Streamlit entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── download_datasets.py      # Export CSV datasets
├── train_models.py           # Standalone model training
├── agent/                    # Intelligent recommendation agent
├── backend/                  # Pipeline orchestrator
├── data/                     # Loader, cleaner, feature engineer, datasets
├── documentation/            # Architecture, API reference, deployment guide
├── frontend/                 # Streamlit pages and UI components
├── models/                   # XGB, RF, LR, K-Means + model manager
├── services/                 # Binance and Yahoo Finance API clients
└── utils/                    # Config, logging, evaluation helpers
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Project Report](documentation/project_report.md) | Full technical report and methodology |
| [Architecture Diagram](documentation/architecture_diagram.md) | System architecture and data flow |
| [API Reference](documentation/api_reference.md) | Module, class and method docs |
| [Deployment Guide](documentation/deployment_guide.md) | Docker and Streamlit Cloud instructions |
| [Viva Q&A](documentation/viva_qa.md) | 30 common questions about design and ML concepts |

---

## ⚠️ Disclaimer

**This software is for educational and research purposes only.** It does not constitute financial advice. Cryptocurrency markets are highly volatile — always conduct your own research before making any financial decisions.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Adan Bhatti** · [GitHub](https://github.com/Adan-Bhatti)
