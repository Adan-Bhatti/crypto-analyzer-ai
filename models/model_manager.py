"""
Model Manager Module
=====================
Handles saving, loading, and versioning of trained ML models.
All models are serialized with ``joblib`` and stored in the
``models/saved/`` directory.
"""
from __future__ import annotations

import os
from pathlib import Path

import joblib

from utils.config import MODELS_DIR
from utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """
    Handles saving, loading, and versioning of trained models.

    Models are stored as ``.joblib`` files in the configured models directory.

    Usage::

        manager = ModelManager()
        path = manager.save_model(trained_model, "random_forest")
        model = manager.load_model("random_forest")
    """

    MODELS_DIR: str = MODELS_DIR

    def __init__(self) -> None:
        """Initialize the model manager and ensure the save directory exists."""
        Path(self.MODELS_DIR).mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------

    def save_model(self, model: object, name: str) -> str:
        """
        Save a trained model to disk.

        Args:
            model: The trained model object to save.
            name: Base name for the model file (without extension).

        Returns:
            The full file path where the model was saved.
        """
        filepath = self._get_model_path(name)
        joblib.dump(model, filepath)
        logger.info("Model '%s' saved to: %s", name, filepath)
        return filepath

    # -----------------------------------------------------------------
    # Load
    # -----------------------------------------------------------------

    def load_model(self, name: str) -> object:
        """
        Load a previously saved model from disk.

        Args:
            name: Base name of the model file (without extension).

        Returns:
            The deserialized model object.

        Raises:
            FileNotFoundError: If the model file does not exist.
        """
        filepath = self._get_model_path(name)

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Model '{name}' not found at: {filepath}"
            )

        model = joblib.load(filepath)
        logger.info("Model '%s' loaded from: %s", name, filepath)
        return model

    # -----------------------------------------------------------------
    # Existence Check
    # -----------------------------------------------------------------

    def model_exists(self, name: str) -> bool:
        """
        Check if a saved model exists on disk.

        Args:
            name: Base name of the model file.

        Returns:
            True if the model file exists, False otherwise.
        """
        filepath = self._get_model_path(name)
        exists = os.path.exists(filepath)
        logger.debug("Model '%s' exists: %s", name, exists)
        return exists

    # -----------------------------------------------------------------
    # List Saved Models
    # -----------------------------------------------------------------

    def list_saved_models(self) -> list[str]:
        """
        List all saved model names in the models directory.

        Returns:
            List of model base names (without the ``.joblib`` extension).
        """
        models = []
        models_path = Path(self.MODELS_DIR)

        if models_path.exists():
            for f in models_path.glob("*.joblib"):
                models.append(f.stem)

        logger.info("Found %d saved models: %s", len(models), models)
        return models

    # -----------------------------------------------------------------
    # Delete Model
    # -----------------------------------------------------------------

    def delete_model(self, name: str) -> None:
        """
        Delete a saved model from disk.

        Args:
            name: Base name of the model file.

        Raises:
            FileNotFoundError: If the model file does not exist.
        """
        filepath = self._get_model_path(name)

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Model '{name}' not found at: {filepath}"
            )

        os.remove(filepath)
        logger.info("Model '%s' deleted from: %s", name, filepath)

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    def _get_model_path(self, name: str) -> str:
        """
        Construct the full file path for a model.

        Args:
            name: Base name of the model.

        Returns:
            Full path with ``.joblib`` extension.
        """
        return str(Path(self.MODELS_DIR) / f"{name}.joblib")
