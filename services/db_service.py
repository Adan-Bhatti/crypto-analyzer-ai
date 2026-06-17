"""
Database Service Module
=======================
Handles SQLite operations for persisting predictions and recommendations.
"""
from __future__ import annotations

import sqlite3
import bcrypt
from pathlib import Path
from typing import Any, Optional

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
                
                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        is_admin BOOLEAN DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Predictions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL DEFAULT 1,
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
                        user_id INTEGER NOT NULL DEFAULT 1,
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

                # Add user_id column to existing tables if they don't have it
                try:
                    cursor.execute("ALTER TABLE predictions ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1")
                except sqlite3.OperationalError:
                    pass
                try:
                    cursor.execute("ALTER TABLE recommendations ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1")
                except sqlite3.OperationalError:
                    pass
                conn.commit()
                logger.info("Database initialized at %s", self.db_path)
                
                # Create default admin if no users exist
                cursor.execute("SELECT COUNT(*) as count FROM users")
                if cursor.fetchone()["count"] == 0:
                    self.create_user("admin", "@Bhatti288", is_admin=True)
                    logger.info("Created default admin user (admin/@Bhatti288)")
        except Exception as exc:
            logger.error("Failed to initialize database: %s", exc)

    # -------------------------------------------------------------------------
    # Authentication & Users
    # -------------------------------------------------------------------------

    def create_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        """Create a new user with a hashed password."""
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                    (username, hashed, is_admin)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            logger.warning("Username '%s' already exists", username)
            return False
        except Exception as exc:
            logger.error("Error creating user: %s", exc)
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user and return the user record if successful."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                if user and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
                    return dict(user)
                return None
        except Exception as exc:
            logger.error("Error during authentication: %s", exc)
            return None

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Fetch user by username without password check (for cookie auth)."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                if user:
                    return dict(user)
                return None
        except Exception as exc:
            logger.error("Error fetching user: %s", exc)
            return None

    def get_all_users(self) -> list[dict]:
        """Get all users (for admin panel)."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, is_admin, created_at FROM users")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as exc:
            logger.error("Error fetching users: %s", exc)
            return []

    # -------------------------------------------------------------------------
    # Predictions
    # -------------------------------------------------------------------------

    def insert_prediction(self, data: dict[str, Any]) -> None:
        """Insert a new prediction record into the database."""
        query = """
            INSERT INTO predictions (
                user_id, symbol, timestamp, bullish_prob, bearish_prob, 
                rf_prediction, lr_prediction, xgb_prediction
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.get_connection() as conn:
                conn.execute(query, (
                    data.get("user_id", 1),
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

    def get_prediction_history(self, user_id: int, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve prediction history for a user, ordered by newest first but returned chronological."""
        query = "SELECT * FROM predictions WHERE user_id = ? ORDER BY id DESC LIMIT ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id, limit,))
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
                user_id, symbol, timestamp, action, confidence, bullish_prob, 
                bearish_prob, risk_level, stop_loss, take_profit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.get_connection() as conn:
                conn.execute(query, (
                    data.get("user_id", 1),
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

    def get_recommendation_history(self, user_id: int, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve recommendation history for a user, ordered by newest first but returned chronological."""
        query = "SELECT * FROM recommendations WHERE user_id = ? ORDER BY id DESC LIMIT ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id, limit,))
                rows = cursor.fetchall()
                # Reverse to make it chronological
                return [dict(row) for row in reversed(rows)]
        except Exception as exc:
            logger.error("Failed to fetch recommendation history: %s", exc)
            return []
