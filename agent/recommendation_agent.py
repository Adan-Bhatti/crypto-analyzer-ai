"""
Intelligent Recommendation Agent
===================================
Rule-based agent that synthesizes ML predictions and risk classification
into actionable trading recommendations (BUY / HOLD / SELL).

Decision Logic:
  - Combines bullish/bearish probabilities with risk level.
  - Applies risk modifiers to base actions.
  - Generates human-readable reasoning.
  - Computes suggested stop-loss and take-profit levels.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from utils.config import (
    BUY_THRESHOLD,
    HOLD_LOWER,
    SELL_THRESHOLD,
    STOP_LOSS_PCT,
    TAKE_PROFIT_PCT,
)
from utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Result Dataclass
# =============================================================================

@dataclass
class RecommendationResult:
    """Container for the recommendation engine output."""

    action: str                           # "BUY" | "HOLD" | "SELL"
    confidence: str                       # "High" | "Medium" | "Low"
    bullish_prob: float                   # Probability of bullish outcome
    bearish_prob: float                   # Probability of bearish outcome
    risk_level: str                       # "Low" | "Medium" | "High"
    reasoning: list[str] = field(default_factory=list)  # 3–5 bullet points
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    suggested_stop_loss: float = 0.0      # e.g., current_price * 0.95
    suggested_take_profit: float = 0.0    # e.g., current_price * 1.10


# =============================================================================
# Recommendation Agent
# =============================================================================

class RecommendationAgent:
    """
    Rule-based intelligent agent that synthesizes ML predictions
    and risk classification into actionable trading recommendations.

    The agent follows a configurable decision table (see ``config.py``
    for threshold values) and applies risk modifiers to adjust base
    actions when market conditions warrant caution.

    Usage::

        agent = RecommendationAgent()
        result = agent.generate_recommendation(
            bullish_prob=0.75,
            bearish_prob=0.25,
            risk_level="Low",
            current_price=67000.0,
            model_confidence=0.80,
        )
        print(result.action)     # "BUY"
        print(result.reasoning)  # ["Bullish probability (75.0%) exceeds...", ...]
    """

    # Decision thresholds (loaded from config for easy tuning)
    BUY_BULL_THRESHOLD: float = BUY_THRESHOLD       # 70%
    HOLD_LOWER_THRESHOLD: float = HOLD_LOWER         # 50%
    SELL_BEAR_THRESHOLD: float = SELL_THRESHOLD       # 60%

    def __init__(self) -> None:
        """Initialize the recommendation agent."""
        self._reasoning: list[str] = []
        self._confidence_score: float = 0.0

    # -----------------------------------------------------------------
    # Main Recommendation Logic
    # -----------------------------------------------------------------

    def generate_recommendation(
        self,
        bullish_prob: float,
        bearish_prob: float,
        risk_level: str,
        current_price: float,
        model_confidence: float,
    ) -> RecommendationResult:
        """
        Generate a trading recommendation based on ML predictions and risk level.

        Decision Table:
          | Bullish Prob | Bearish Prob | Risk   | Action | Confidence |
          |--------------|--------------|--------|--------|------------|
          | > 70%        | any          | Low    | BUY    | High       |
          | > 70%        | any          | Medium | BUY    | Medium     |
          | > 70%        | any          | High   | HOLD   | Medium     |
          | 50%–70%      | any          | Low    | HOLD   | Medium     |
          | 50%–70%      | any          | Medium | HOLD   | Low        |
          | 50%–70%      | any          | High   | SELL   | Medium     |
          | any          | > 60%        | Low    | HOLD   | Low        |
          | any          | > 60%        | Medium | SELL   | Medium     |
          | any          | > 60%        | High   | SELL   | High       |

        Args:
            bullish_prob: Probability of price increase (0.0–1.0).
            bearish_prob: Probability of price decrease (0.0–1.0).
            risk_level: Current risk classification (``"Low"``, ``"Medium"``, ``"High"``).
            current_price: Current market price (for stop-loss / take-profit).
            model_confidence: Overall model confidence score.

        Returns:
            ``RecommendationResult`` with action, confidence, reasoning, and levels.
        """
        self._reasoning = []
        base_action = "HOLD"
        confidence = "Low"

        # === Decision Logic ===

        # Priority 1: Strong bullish signal (> 70%)
        if bullish_prob > self.BUY_BULL_THRESHOLD:
            self._reasoning.append(
                f"Bullish probability ({bullish_prob:.1%}) exceeds "
                f"buy threshold ({self.BUY_BULL_THRESHOLD:.0%})."
            )

            if risk_level == "Low":
                base_action = "BUY"
                confidence = "High"
                self._reasoning.append(
                    "Low risk environment supports aggressive positioning."
                )
            elif risk_level == "Medium":
                base_action = "BUY"
                confidence = "Medium"
                self._reasoning.append(
                    "Medium risk tempers confidence despite strong bullish signal."
                )
            else:  # High risk
                base_action = "HOLD"
                confidence = "Medium"
                self._reasoning.append(
                    "High risk overrides bullish signal — recommend holding."
                )

        # Priority 2: Moderate bullish signal (50%–70%)
        elif bullish_prob >= self.HOLD_LOWER_THRESHOLD:
            self._reasoning.append(
                f"Bullish probability ({bullish_prob:.1%}) is in the "
                f"neutral zone ({self.HOLD_LOWER_THRESHOLD:.0%}–{self.BUY_BULL_THRESHOLD:.0%})."
            )

            if risk_level == "Low":
                base_action = "HOLD"
                confidence = "Medium"
                self._reasoning.append(
                    "Low risk with moderate bullish outlook — hold and monitor."
                )
            elif risk_level == "Medium":
                base_action = "HOLD"
                confidence = "Low"
                self._reasoning.append(
                    "Mixed signals with medium risk — insufficient conviction to act."
                )
            else:  # High risk
                base_action = "SELL"
                confidence = "Medium"
                self._reasoning.append(
                    "High risk combined with uncertain outlook — defensive sell."
                )

        # Priority 3: Bearish signal (bearish prob > 60%)
        if bearish_prob > self.SELL_BEAR_THRESHOLD:
            self._reasoning.append(
                f"Bearish probability ({bearish_prob:.1%}) exceeds "
                f"sell threshold ({self.SELL_BEAR_THRESHOLD:.0%})."
            )

            if risk_level == "Low":
                base_action = "HOLD"
                confidence = "Low"
                self._reasoning.append(
                    "Low risk moderates the bearish signal — hold rather than sell."
                )
            elif risk_level == "Medium":
                base_action = "SELL"
                confidence = "Medium"
                self._reasoning.append(
                    "Bearish signal with medium risk — recommend reducing exposure."
                )
            else:  # High risk
                base_action = "SELL"
                confidence = "High"
                self._reasoning.append(
                    "Strong bearish signal in high-risk environment — sell recommended."
                )

        # Add model confidence context
        self._reasoning.append(
            f"Model confidence: {model_confidence:.1%}. "
            f"Risk classification: {risk_level}."
        )

        # Compute stop-loss and take-profit levels
        stop_loss = current_price * (1 - STOP_LOSS_PCT)
        take_profit = current_price * (1 + TAKE_PROFIT_PCT)

        if base_action == "SELL":
            # Invert: stop-loss above, take-profit below
            stop_loss = current_price * (1 + STOP_LOSS_PCT)
            take_profit = current_price * (1 - TAKE_PROFIT_PCT)

        self._confidence_score = model_confidence

        result = RecommendationResult(
            action=base_action,
            confidence=confidence,
            bullish_prob=bullish_prob,
            bearish_prob=bearish_prob,
            risk_level=risk_level,
            reasoning=self._reasoning.copy(),
            suggested_stop_loss=round(stop_loss, 2),
            suggested_take_profit=round(take_profit, 2),
        )

        logger.info(
            "Recommendation: %s (confidence=%s) | Bull=%.1f%% Bear=%.1f%% Risk=%s",
            result.action, result.confidence,
            bullish_prob * 100, bearish_prob * 100, risk_level,
        )

        return result

    # -----------------------------------------------------------------
    # Risk Modifier (for extensibility)
    # -----------------------------------------------------------------

    def _apply_risk_modifier(
        self,
        base_action: str,
        risk_level: str,
    ) -> str:
        """
        Apply a risk-based modifier to the base action.

        High risk can downgrade BUY → HOLD or HOLD → SELL.

        Args:
            base_action: The initial recommended action.
            risk_level: Current risk classification.

        Returns:
            Modified action string.
        """
        if risk_level == "High":
            if base_action == "BUY":
                return "HOLD"
            elif base_action == "HOLD":
                return "SELL"
        return base_action

    # -----------------------------------------------------------------
    # Accessors
    # -----------------------------------------------------------------

    def get_reasoning(self) -> list[str]:
        """
        Return the human-readable reasoning from the last recommendation.

        Returns:
            List of reasoning bullet points.
        """
        return self._reasoning.copy()

    def get_confidence_score(self) -> float:
        """
        Return the confidence score from the last recommendation.

        Returns:
            Confidence score as a float (0.0–1.0).
        """
        return self._confidence_score
