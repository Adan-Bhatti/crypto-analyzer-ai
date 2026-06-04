"""
Orchestrator Module
=====================
Coordinates models and agent decisions at a high level.
Manages Streamlit session state integration so that trained models
and pipeline results persist across page navigations.
"""
from __future__ import annotations

from typing import Any

import streamlit as st

from backend.pipeline import CryptoPipeline, PipelineResult
from utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    """
    Coordinates models + agent decisions and manages session state.

    Ensures that trained models, pipeline results, and prediction history
    persist in ``st.session_state`` to avoid redundant re-training when
    users navigate between Streamlit pages.

    Usage::

        orch = Orchestrator()
        result = orch.run_analysis("BTCUSDT", data_source="api")
    """

    # Session state keys
    _KEY_PIPELINE = "pipeline_instance"
    _KEY_RESULT = "pipeline_result"
    _KEY_PREDICTIONS = "prediction_history"
    _KEY_RECOMMENDATIONS = "recommendation_history"

    def __init__(self) -> None:
        """Initialize the orchestrator and session state."""
        self._init_session_state()

    # -----------------------------------------------------------------
    # Session State Management
    # -----------------------------------------------------------------

    def _init_session_state(self) -> None:
        """Ensure all required session state keys are initialized."""
        if self._KEY_PIPELINE not in st.session_state:
            st.session_state[self._KEY_PIPELINE] = CryptoPipeline()

        if self._KEY_RESULT not in st.session_state:
            st.session_state[self._KEY_RESULT] = None

        if self._KEY_PREDICTIONS not in st.session_state:
            st.session_state[self._KEY_PREDICTIONS] = []

        if self._KEY_RECOMMENDATIONS not in st.session_state:
            st.session_state[self._KEY_RECOMMENDATIONS] = []

    @property
    def pipeline(self) -> CryptoPipeline:
        """Access the persistent pipeline instance."""
        return st.session_state[self._KEY_PIPELINE]

    @property
    def last_result(self) -> PipelineResult | None:
        """Access the most recent pipeline result."""
        return st.session_state.get(self._KEY_RESULT)

    @property
    def prediction_history(self) -> list[dict]:
        """Access the prediction history."""
        return st.session_state.get(self._KEY_PREDICTIONS, [])

    @property
    def recommendation_history(self) -> list[dict]:
        """Access the recommendation history."""
        return st.session_state.get(self._KEY_RECOMMENDATIONS, [])

    # -----------------------------------------------------------------
    # Run Analysis
    # -----------------------------------------------------------------

    def run_analysis(
        self,
        symbol: str,
        data_source: str = "api",
        csv_path: str | None = None,
        retrain: bool = False,
    ) -> PipelineResult:
        """
        Run the full analysis pipeline and store results in session state.

        Args:
            symbol: Cryptocurrency symbol (e.g., ``"BTCUSDT"``).
            data_source: ``"api"`` or ``"csv"``.
            csv_path: Path to CSV file (when ``data_source="csv"``).
            retrain: Force model retraining.

        Returns:
            ``PipelineResult`` with all analysis outputs.
        """
        logger.info(
            "Orchestrator: running analysis for %s (source=%s, retrain=%s)",
            symbol, data_source, retrain,
        )

        result = self.pipeline.run_full_pipeline(
            symbol=symbol,
            data_source=data_source,
            csv_path=csv_path,
            retrain=retrain,
        )

        # Persist the result
        st.session_state[self._KEY_RESULT] = result

        # Append to prediction history
        if result.prediction is not None:
            self._append_prediction(result)

        # Append to recommendation history
        if result.recommendation is not None:
            self._append_recommendation(result)

        return result

    # -----------------------------------------------------------------
    # Quick Prediction (using existing models)
    # -----------------------------------------------------------------

    def run_quick_prediction(self) -> PipelineResult | None:
        """
        Re-run prediction using the already-loaded data and trained models.

        Returns:
            Updated ``PipelineResult``, or None if no prior data exists.
        """
        last = self.last_result
        if last is None or last.engineered_df.empty:
            logger.warning("No prior data available for quick prediction")
            return None

        # Re-run prediction only (no retraining)
        prediction = self.pipeline.run_prediction_only(last.engineered_df)
        last.prediction = prediction

        # Re-run risk classification
        risk = self.pipeline.run_risk_classification(last.engineered_df)
        last.risk = risk

        # Re-run recommendation
        if prediction and risk:
            current_price = float(last.engineered_df["close"].iloc[-1])
            model_confidence = self.pipeline.evaluation_metrics.get("rf_accuracy", 0.5)

            recommendation = self.pipeline.agent.generate_recommendation(
                bullish_prob=prediction.bullish_prob,
                bearish_prob=prediction.bearish_prob,
                risk_level=risk.risk_level,
                current_price=current_price,
                model_confidence=model_confidence,
            )
            last.recommendation = recommendation
            self._append_recommendation(last)

        st.session_state[self._KEY_RESULT] = last
        self._append_prediction(last)

        return last

    # -----------------------------------------------------------------
    # State Accessors
    # -----------------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """
        Get the current state of the orchestrator and pipeline.

        Returns:
            Dictionary with pipeline status and history counts.
        """
        return {
            "pipeline_status": self.pipeline.get_pipeline_status(),
            "has_result": self.last_result is not None,
            "prediction_count": len(self.prediction_history),
            "recommendation_count": len(self.recommendation_history),
        }

    def clear_state(self) -> None:
        """Reset all session state (clear models and history)."""
        st.session_state[self._KEY_PIPELINE] = CryptoPipeline()
        st.session_state[self._KEY_RESULT] = None
        st.session_state[self._KEY_PREDICTIONS] = []
        st.session_state[self._KEY_RECOMMENDATIONS] = []
        logger.info("Orchestrator state cleared")

    # -----------------------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------------------

    def _append_prediction(self, result: PipelineResult) -> None:
        """Append a prediction entry to the history."""
        if result.prediction is None:
            return

        entry = {
            "timestamp": result.prediction.bullish_prob,  # will be overridden
            "bullish_prob": result.prediction.bullish_prob,
            "bearish_prob": result.prediction.bearish_prob,
            "rf_prediction": result.prediction.rf_prediction,
            "lr_prediction": result.prediction.lr_prediction,
        }

        history = st.session_state.get(self._KEY_PREDICTIONS, [])
        history.append(entry)
        # Keep only the last 50 predictions
        st.session_state[self._KEY_PREDICTIONS] = history[-50:]

    def _append_recommendation(self, result: PipelineResult) -> None:
        """Append a recommendation entry to the history."""
        if result.recommendation is None:
            return

        rec = result.recommendation
        entry = {
            "timestamp": rec.timestamp.isoformat(),
            "action": rec.action,
            "confidence": rec.confidence,
            "bullish_prob": rec.bullish_prob,
            "bearish_prob": rec.bearish_prob,
            "risk_level": rec.risk_level,
            "stop_loss": rec.suggested_stop_loss,
            "take_profit": rec.suggested_take_profit,
        }

        history = st.session_state.get(self._KEY_RECOMMENDATIONS, [])
        history.append(entry)
        # Keep only the last 50 recommendations
        st.session_state[self._KEY_RECOMMENDATIONS] = history[-50:]
