"""
Database Service Module
=======================
Handles SQLite operations for persisting predictions and recommendations.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from utils.config import PROJECT_ROOT
from utils.logger import get_logger

logger = get_logger(__name__)

DB_PATH = PROJECT_ROOT / "data" / "crypto_analyzer.db"


class DBService:
    """Service to handle SQLite database operations."""

    def __init__(self, db_path: Path | str = DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory configured."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Initialize the database tables if they do not exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Predictions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        bullish_prob REAL NOT NULL,
                        bearish_prob REAL NOT NULL,
                        rf_prediction INTEGER NOT NULL,
                        lr_prediction INTEGER NOT NULL,
                        xgb_prediction INTEGER NOT NULL
                    )
                """)
                
                # Recommendations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        action TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        bullish_prob REAL NOT NULL,
                        bearish_prob REAL NOT NULL,
                        risk_level TEXT NOT NULL,
                        stop_loss REAL NOT NULL,
                        take_profit REAL NOT NULL
                    )
                """)
                conn.commit()
                logger.info("Database initialized at %s", self.db_path)
        except Exception as exc:
            logger.error("Failed to initialize database: %s", exc)

    def insert_prediction(self, data: dict[str, Any]) -> None:
        """Insert a new prediction record into the database."""
        query = """
            INSERT INTO predictions (
                symbol, timestamp, bullish_prob, bearish_prob, 
                rf_prediction, lr_prediction, xgb_prediction
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.get_connection() as conn:
                conn.execute(query, (
                    data.get("symbol", "UNKNOWN"),
                    str(data.get("timestamp", "")),
                    data.get("bullish_prob", 0.0),
                    data.get("bearish_prob", 0.0),
                    data.get("rf_prediction", 0),
                    data.get("lr_prediction", 0),
                    data.get("xgb_prediction", 0)
                ))
                conn.commit()
        except Exception as exc:
            logger.error("Failed to insert prediction: %s", exc)

    def get_prediction_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve prediction history, ordered by newest first but returned chronological."""
        query = "SELECT * FROM predictions ORDER BY id DESC LIMIT ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
                # Reverse to make it chronological
                return [dict(row) for row in reversed(rows)]
        except Exception as exc:
            logger.error("Failed to fetch prediction history: %s", exc)
            return []

    def insert_recommendation(self, data: dict[str, Any]) -> None:
        """Insert a new recommendation record into the database."""
        query = """
            INSERT INTO recommendations (
                symbol, timestamp, action, confidence, bullish_prob, 
                bearish_prob, risk_level, stop_loss, take_profit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.get_connection() as conn:
                conn.execute(query, (
                    data.get("symbol", "UNKNOWN"),
                    str(data.get("timestamp", "")),
                    data.get("action", ""),
                    data.get("confidence", 0.0),
                    data.get("bullish_prob", 0.0),
                    data.get("bearish_prob", 0.0),
                    data.get("risk_level", ""),
                    data.get("stop_loss", 0.0),
                    data.get("take_profit", 0.0)
                ))
                conn.commit()
        except Exception as exc:
            logger.error("Failed to insert recommendation: %s", exc)

    def get_recommendation_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve recommendation history, ordered by newest first but returned chronological."""
        query = "SELECT * FROM recommendations ORDER BY id DESC LIMIT ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
                # Reverse to make it chronological
                return [dict(row) for row in reversed(rows)]
        except Exception as exc:
            logger.error("Failed to fetch recommendation history: %s", exc)
            return []
