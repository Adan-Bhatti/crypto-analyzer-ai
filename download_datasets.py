"""
Dataset Downloader
==================
Downloads the maximum historical data for supported cryptocurrencies
and saves them as CSV files. Useful for exporting or submitting the dataset.
"""
import os
import sys
from pathlib import Path

# Ensure the project root is on sys.path so imports work correctly
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.loader import DataLoader
from utils.config import SUPPORTED_COINS, YAHOO_TICKERS

def main():
    dataset_dir = PROJECT_ROOT / "data" / "datasets"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    loader = DataLoader()
    
    print(f"Downloading datasets to {dataset_dir}...\n")
    
    for symbol in SUPPORTED_COINS:
        print(f"Fetching data for {symbol}...")
        try:
            yahoo_ticker = YAHOO_TICKERS.get(symbol)
            if yahoo_ticker:
                df = loader.load_max_history(yahoo_ticker)
            else:
                df = loader.load_from_binance(symbol, limit=1000)
                
            csv_path = dataset_dir / f"{symbol}_max_history.csv"
            df.to_csv(csv_path, index=False)
            print(f"  [OK] Saved {len(df)} rows to {csv_path.name}")
        except Exception as e:
            print(f"  [ERR] Failed to fetch {symbol}: {e}")

if __name__ == "__main__":
    main()
