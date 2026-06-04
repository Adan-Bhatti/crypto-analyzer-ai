"""
K-Means Risk Classification Model
====================================
Clusters market conditions into three risk categories:
  - **Cluster 0** → Low Risk
  - **Cluster 1** → Medium Risk
  - **Cluster 2** → High Risk

Features used for clustering:
  ``volatility_14``, ``rsi_14``, ``volume_change``, ``daily_return_std``

Cluster-to-risk mapping is determined by sorting cluster centers
by mean volatility (lowest volatility = Low Risk).
"""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from utils.config import (
    CLUSTERING_FEATURES,
    KMEANS_ELBOW_RANGE,
    KMEANS_N_CLUSTERS,
    RANDOM_STATE,
    RISK_LABELS,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class KMeansRiskClassifier:
    """
    Clusters market conditions into Low / Medium / High risk categories
    using K-Means clustering on volatility-related features.

    Usage::

        classifier = KMeansRiskClassifier()
        classifier.fit(engineered_df)
        risk_series = classifier.predict_risk(new_df)
    """

    def __init__(
        self,
        n_clusters: int = KMEANS_N_CLUSTERS,
        random_state: int = RANDOM_STATE,
    ) -> None:
        """
        Initialize the K-Means risk classifier.

        Args:
            n_clusters: Number of clusters (default 3 for Low/Medium/High).
            random_state: Random seed for reproducibility.
        """
        self.n_clusters = n_clusters
        self.random_state = random_state

        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10,
        )

        self.scaler = StandardScaler()
        self.cluster_risk_map: dict[int, str] = {}
        self.silhouette: float = 0.0
        self.inertias: list[float] = []
        self.is_fitted: bool = False
        self._cluster_centers_df: pd.DataFrame | None = None

    # -----------------------------------------------------------------
    # Fitting
    # -----------------------------------------------------------------

    def fit(self, df: pd.DataFrame) -> None:
        """
        Fit the K-Means model on clustering features.

        Steps:
          1. Extract clustering features.
          2. Scale features with ``StandardScaler``.
          3. Fit K-Means.
          4. Compute silhouette score.
          5. Map clusters to risk labels by volatility ranking.
          6. Run elbow method for the diagnostic plot.

        Args:
            df: Feature-engineered DataFrame containing the clustering features.
        """
        logger.info("Fitting K-Means risk classifier with k=%d", self.n_clusters)

        # Extract and validate clustering features
        features_df = self._extract_features(df)

        # Scale features
        X_scaled = self.scaler.fit_transform(features_df)

        # Fit K-Means
        self.model.fit(X_scaled)
        labels = self.model.labels_

        # Compute silhouette score (quality metric)
        self.silhouette = float(silhouette_score(X_scaled, labels))
        logger.info("Silhouette score: %.4f", self.silhouette)

        # Create cluster centers DataFrame
        self._cluster_centers_df = pd.DataFrame(
            self.scaler.inverse_transform(self.model.cluster_centers_),
            columns=CLUSTERING_FEATURES,
        )

        # Map clusters to risk labels based on volatility
        self._map_clusters_to_risk()

        # Run elbow method for the diagnostic plot
        self._compute_elbow(X_scaled)

        self.is_fitted = True
        logger.info("K-Means fitting complete. Risk mapping: %s", self.cluster_risk_map)

    # -----------------------------------------------------------------
    # Prediction
    # -----------------------------------------------------------------

    def predict_risk(self, df: pd.DataFrame) -> pd.Series:
        """
        Predict risk levels for new data points.

        Args:
            df: DataFrame containing the clustering features.

        Returns:
            Pandas Series of risk labels (``"Low"``, ``"Medium"``, ``"High"``).
        """
        self._check_fitted()

        features_df = self._extract_features(df)
        X_scaled = self.scaler.transform(features_df)
        cluster_labels = self.model.predict(X_scaled)

        # Map cluster IDs to risk labels
        risk_labels = pd.Series(
            [self.map_cluster_to_label(c) for c in cluster_labels],
            index=features_df.index,
            name="risk_level",
        )

        logger.info("Risk predictions — distribution: %s", risk_labels.value_counts().to_dict())
        return risk_labels

    # -----------------------------------------------------------------
    # Cluster Information
    # -----------------------------------------------------------------

    def get_cluster_centers(self) -> pd.DataFrame:
        """
        Get the cluster centers in original (unscaled) feature space.

        Returns:
            DataFrame with cluster centers and their risk label.
        """
        self._check_fitted()

        centers_df = self._cluster_centers_df.copy()
        centers_df["risk_label"] = [
            self.cluster_risk_map.get(i, "Unknown")
            for i in range(len(centers_df))
        ]

        return centers_df

    def map_cluster_to_label(self, cluster_id: int) -> str:
        """
        Map a cluster ID to its corresponding risk label.

        Args:
            cluster_id: The cluster index (0, 1, or 2).

        Returns:
            Risk label string (``"Low"``, ``"Medium"``, or ``"High"``).
        """
        return self.cluster_risk_map.get(cluster_id, "Unknown")

    def get_risk_distribution(self) -> dict[str, int]:
        """
        Get the distribution of data points across risk clusters
        from the most recent fit.

        Returns:
            Dictionary mapping risk labels to counts.
        """
        self._check_fitted()

        labels = self.model.labels_
        distribution: dict[str, int] = {}

        for cluster_id, count in zip(*np.unique(labels, return_counts=True)):
            risk_label = self.map_cluster_to_label(int(cluster_id))
            distribution[risk_label] = int(count)

        return distribution

    def get_elbow_inertias(self) -> list[float]:
        """
        Return the inertia values computed during the elbow method analysis.

        Returns:
            List of inertia values for k = 2 to 8.
        """
        return self.inertias

    # -----------------------------------------------------------------
    # Model Persistence
    # -----------------------------------------------------------------

    def save(self, path: str) -> None:
        """
        Save the fitted model, scaler, and risk mapping to disk.

        Args:
            path: File path for the saved model.
        """
        self._check_fitted()
        joblib.dump({
            "model": self.model,
            "scaler": self.scaler,
            "cluster_risk_map": self.cluster_risk_map,
            "silhouette": self.silhouette,
            "inertias": self.inertias,
            "cluster_centers_df": self._cluster_centers_df,
        }, path)
        logger.info("K-Means model saved to: %s", path)

    def load(self, path: str) -> None:
        """
        Load a previously fitted model from disk.

        Args:
            path: File path of the saved model.
        """
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.cluster_risk_map = data["cluster_risk_map"]
        self.silhouette = data["silhouette"]
        self.inertias = data["inertias"]
        self._cluster_centers_df = data["cluster_centers_df"]
        self.is_fitted = True
        logger.info("K-Means model loaded from: %s", path)

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract the clustering feature columns from the DataFrame.

        Args:
            df: Source DataFrame.

        Returns:
            DataFrame with only the clustering feature columns, NaNs dropped.
        """
        available = [f for f in CLUSTERING_FEATURES if f in df.columns]

        if len(available) < len(CLUSTERING_FEATURES):
            missing = set(CLUSTERING_FEATURES) - set(available)
            logger.warning("Missing clustering features: %s", missing)

        features_df = df[available].dropna()
        return features_df

    def _map_clusters_to_risk(self) -> None:
        """
        Map cluster IDs to risk labels by sorting cluster centers
        by mean volatility (lowest = Low Risk, highest = High Risk).
        """
        centers = self._cluster_centers_df

        # Use volatility_14 as the primary sorting criterion
        if "volatility_14" in centers.columns:
            sorted_indices = centers["volatility_14"].argsort().values
        else:
            # Fallback: sort by the mean of all features
            sorted_indices = centers.mean(axis=1).argsort().values

        risk_order = ["Low", "Medium", "High"]
        self.cluster_risk_map = {}

        for rank, cluster_id in enumerate(sorted_indices):
            if rank < len(risk_order):
                self.cluster_risk_map[int(cluster_id)] = risk_order[rank]

        logger.info("Cluster-to-risk mapping: %s", self.cluster_risk_map)

    def _compute_elbow(self, X_scaled: np.ndarray) -> None:
        """
        Run K-Means for k=2..8 to compute inertia values for the elbow plot.

        Args:
            X_scaled: Scaled feature matrix.
        """
        self.inertias = []

        for k in KMEANS_ELBOW_RANGE:
            km = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            km.fit(X_scaled)
            self.inertias.append(float(km.inertia_))

        logger.info("Elbow method computed for k=%s", list(KMEANS_ELBOW_RANGE))

    def _check_fitted(self) -> None:
        """Raise an error if the model has not been fitted."""
        if not self.is_fitted:
            raise RuntimeError(
                "K-Means model has not been fitted yet. Call fit() or load() first."
            )
