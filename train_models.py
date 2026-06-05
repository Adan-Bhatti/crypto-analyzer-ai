# -*- coding: utf-8 -*-
"""
Standalone Model Training Script
==================================
Downloads maximum historical data for all supported cryptocurrencies,
trains Random Forest, Logistic Regression, and XGBoost with full
GridSearchCV tuning, and saves models to models/saved/.

Usage (from the crypto_analyzer directory):
    python train_models.py
    python train_models.py --coins BTCUSDT ETHUSDT   # specific coins
    python train_models.py --coin BTCUSDT             # single coin
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Force UTF-8 output on Windows to avoid cp1252 encoding errors
# ---------------------------------------------------------------------------
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so imports work correctly
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from data.cleaner import DataCleaner
from data.feature_engineer import FeatureEngineer
from data.loader import DataLoader
from models.kmeans_clustering import KMeansRiskClassifier
from models.logistic_regression import LogisticRegressionModel
from models.model_manager import ModelManager
from models.random_forest import RandomForestModel
from models.xgboost_model import XGBoostModel
from utils.config import SUPPORTED_COINS, TEST_SIZE, YAHOO_TICKERS
from utils.evaluator import ModelEvaluator
from utils.logger import get_logger

logger = get_logger("train_models")

# ---------------------------------------------------------------------------
# ANSI colour helpers (works on modern Windows terminals)
# ---------------------------------------------------------------------------
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def banner(text: str) -> None:
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}\n")


def section(text: str) -> None:
    print(f"\n{BOLD}{YELLOW}>> {text}{RESET}")


def ok(text: str) -> None:
    print(f"  {GREEN}[OK] {text}{RESET}")


def warn(text: str) -> None:
    print(f"  {YELLOW}[WARN] {text}{RESET}")


def err(text: str) -> None:
    print(f"  {RED}[ERR] {text}{RESET}")


# ---------------------------------------------------------------------------
# Core training logic for a single coin
# ---------------------------------------------------------------------------

def train_coin(
    symbol: str,
    loader: DataLoader,
    cleaner: DataCleaner,
    engineer: FeatureEngineer,
    manager: ModelManager,
    evaluator: ModelEvaluator,
) -> dict:
    """
    Download max history, engineer features, and train + save all three models
    for a single cryptocurrency symbol.

    Returns:
        Dictionary of evaluation metrics for all three models.
    """
    banner(f"Training: {symbol}")
    results: dict = {"symbol": symbol, "status": "failed"}

    # ------------------------------------------------------------------
    # Step 1: Load maximum historical data
    # ------------------------------------------------------------------
    section("Step 1/5 - Downloading max historical data")
    try:
        yahoo_ticker = YAHOO_TICKERS.get(symbol)
        if yahoo_ticker:
            df_raw = loader.load_max_history(yahoo_ticker)
        else:
            df_raw = loader.load_from_binance(symbol, limit=1000)
        ok(f"Loaded {len(df_raw):,} rows  ({len(df_raw)/365:.1f} years)")
    except Exception as exc:
        err(f"Data loading failed: {exc}")
        results["error"] = str(exc)
        return results

    # ------------------------------------------------------------------
    # Step 2: Clean
    # ------------------------------------------------------------------
    section("Step 2/5 - Cleaning data")
    try:
        df_clean = cleaner.clean(df_raw)
        ok(f"Clean rows: {len(df_clean):,}")
    except Exception as exc:
        err(f"Cleaning failed: {exc}")
        results["error"] = str(exc)
        return results

    # ------------------------------------------------------------------
    # Step 3: Feature engineering
    # ------------------------------------------------------------------
    section("Step 3/5 - Engineering features")
    try:
        df_feat = engineer.engineer_all(df_clean)
        ok(f"Features: {len(df_feat.columns):,} columns, {len(df_feat):,} usable rows")
    except Exception as exc:
        err(f"Feature engineering failed: {exc}")
        results["error"] = str(exc)
        return results

    # ------------------------------------------------------------------
    # Step 4: Prepare train / test sets
    # ------------------------------------------------------------------
    section("Step 4/5 - Splitting data (80/20 temporal split)")
    exclude_cols = {"date", "target", "timestamp"}
    feature_cols = [
        c for c in df_feat.columns
        if c not in exclude_cols
        and df_feat[c].dtype in ("float64", "int64", "float32")
    ]

    train_df = df_feat.dropna(subset=["target"]).copy()
    X = train_df[feature_cols].values
    y = train_df["target"].values

    split_idx = int(len(X) * (1 - TEST_SIZE))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    ok(f"Train: {len(X_train):,} samples | Test: {len(X_test):,} samples | Features: {len(feature_cols)}")

    # ------------------------------------------------------------------
    # Step 5: Train models
    # ------------------------------------------------------------------
    section("Step 5/5 - Training & evaluating models")

    symbol_safe = symbol.lower()
    metrics: dict = {}

    # --- Random Forest ---
    print(f"\n  {BOLD}[1/3] Random Forest (GridSearchCV){RESET}")
    try:
        t0 = time.time()
        rf = RandomForestModel()
        rf.train(X_train, y_train)
        rf_pred = rf.predict(X_test)
        rf_proba = rf.predict_proba(X_test)
        rf_m = evaluator.compute_metrics(y_test, rf_pred, rf_proba[:, 1])
        rf_path = manager._get_model_path(f"random_forest_{symbol_safe}")
        rf.save(rf_path)
        ok(f"RF  -> Accuracy: {rf_m.accuracy:.4f} | F1: {rf_m.f1_score:.4f} | "
           f"AUC: {rf_m.roc_auc:.4f} | Time: {time.time()-t0:.1f}s")
        metrics["rf"] = rf_m
    except Exception as exc:
        err(f"Random Forest failed: {exc}")

    # --- Logistic Regression ---
    print(f"\n  {BOLD}[2/3] Logistic Regression (GridSearchCV){RESET}")
    try:
        t0 = time.time()
        lr = LogisticRegressionModel()
        lr.train(X_train, y_train)
        lr_pred = lr.predict(X_test)
        lr_proba = lr.predict_proba(X_test)
        lr_m = evaluator.compute_metrics(y_test, lr_pred, lr_proba[:, 1])
        lr_path = manager._get_model_path(f"logistic_regression_{symbol_safe}")
        lr.save(lr_path)
        ok(f"LR  -> Accuracy: {lr_m.accuracy:.4f} | F1: {lr_m.f1_score:.4f} | "
           f"AUC: {lr_m.roc_auc:.4f} | Time: {time.time()-t0:.1f}s")
        metrics["lr"] = lr_m
    except Exception as exc:
        err(f"Logistic Regression failed: {exc}")

    # --- XGBoost ---
    print(f"\n  {BOLD}[3/3] XGBoost (GridSearchCV){RESET}")
    try:
        t0 = time.time()
        xgb = XGBoostModel()
        xgb.train(X_train, y_train)
        xgb_pred = xgb.predict(X_test)
        xgb_proba = xgb.predict_proba(X_test)
        xgb_m = evaluator.compute_metrics(y_test, xgb_pred, xgb_proba[:, 1])
        xgb_path = manager._get_model_path(f"xgboost_{symbol_safe}")
        xgb.save(xgb_path)
        ok(f"XGB -> Accuracy: {xgb_m.accuracy:.4f} | F1: {xgb_m.f1_score:.4f} | "
           f"AUC: {xgb_m.roc_auc:.4f} | Time: {time.time()-t0:.1f}s")
        metrics["xgb"] = xgb_m
    except Exception as exc:
        err(f"XGBoost failed: {exc}")

    # --- K-Means Risk Classifier ---
    print(f"\n  {BOLD}[+] K-Means Risk Classifier{RESET}")
    try:
        kmeans = KMeansRiskClassifier()
        kmeans.fit(df_feat)
        km_path = manager._get_model_path(f"kmeans_{symbol_safe}")
        kmeans.save(km_path)
        ok(f"KMeans -> Silhouette: {kmeans.silhouette:.4f} | "
           f"Risk distribution: {kmeans.get_risk_distribution()}")
    except Exception as exc:
        err(f"K-Means failed: {exc}")

    results["status"] = "success"
    results["metrics"] = metrics
    results["rows"] = len(df_feat)
    results["features"] = len(feature_cols)
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train all crypto prediction models with maximum historical data."
    )
    parser.add_argument(
        "--coins",
        nargs="+",
        default=SUPPORTED_COINS,
        help=f"Coins to train (default: all {len(SUPPORTED_COINS)} supported coins)",
    )
    parser.add_argument(
        "--coin",
        type=str,
        default=None,
        help="Single coin to train (shorthand for --coins SYMBOL)",
    )
    args = parser.parse_args()

    coins = [args.coin] if args.coin else args.coins

    banner("Crypto Analyzer - Maximum Model Training")
    print(f"  Coins to train: {', '.join(coins)}")
    print(f"  Data source:    Yahoo Finance (period=max) -> Binance fallback")
    print(f"  Models:         Random Forest + Logistic Regression + XGBoost + K-Means")
    print(f"  Strategy:       GridSearchCV with TimeSeriesSplit (f1_weighted scoring)")

    # Shared components
    loader   = DataLoader()
    cleaner  = DataCleaner()
    engineer = FeatureEngineer()
    manager  = ModelManager()
    evaluator = ModelEvaluator()

    all_results: list[dict] = []
    grand_start = time.time()

    for symbol in coins:
        result = train_coin(
            symbol=symbol,
            loader=loader,
            cleaner=cleaner,
            engineer=engineer,
            manager=manager,
            evaluator=evaluator,
        )
        all_results.append(result)

    # ------------------------------------------------------------------
    # Final Report
    # ------------------------------------------------------------------
    banner("Training Complete - Summary Report")
    total_time = time.time() - grand_start
    print(f"  Total training time: {total_time/60:.1f} minutes\n")

    header = f"  {'Symbol':<12} {'Rows':>6} {'Feats':>5}  {'RF Acc':>7}  {'LR Acc':>7}  {'XGB Acc':>8}  {'Status':<8}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for r in all_results:
        if r["status"] == "success":
            m = r.get("metrics", {})
            rf_acc  = f"{m['rf'].accuracy:.4f}"  if "rf"  in m else "  N/A  "
            lr_acc  = f"{m['lr'].accuracy:.4f}"  if "lr"  in m else "  N/A  "
            xgb_acc = f"{m['xgb'].accuracy:.4f}" if "xgb" in m else "  N/A  "
            print(f"  {r['symbol']:<12} {r['rows']:>6,} {r['features']:>5}  "
                  f"{rf_acc:>7}  {lr_acc:>7}  {xgb_acc:>8}  {GREEN}OK{RESET}")
        else:
            print(f"  {r['symbol']:<12} {'':>6} {'':>5}  {'':>7}  {'':>7}  {'':>8}  {RED}FAILED{RESET}")

    saved_models = manager.list_saved_models()
    print(f"\n  {GREEN}[DONE] {len(saved_models)} model files saved to: {manager.MODELS_DIR}{RESET}")

    print(f"\n  You can now launch the Streamlit app:")
    print(f"  streamlit run app.py\n")


if __name__ == "__main__":
    main()
