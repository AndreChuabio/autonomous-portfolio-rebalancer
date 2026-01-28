"""
Data models for decision tracking and scenarios.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class DecisionStatus(Enum):
    """Decision execution status."""

    TRIGGER = "TRIGGER"
    MONITORING = "MONITORING"
    ALERT = "ALERT"
    EXECUTE = "EXECUTE"
    DEFER = "DEFER"


class ScenarioType(Enum):
    """Rebalancing scenario types."""

    FULL_REBALANCE = "FULL_REBALANCE"
    PARTIAL_REBALANCE = "PARTIAL_REBALANCE"
    SECTOR_REBALANCE = "SECTOR_REBALANCE"
    DEFER = "DEFER"


@dataclass
class Trade:
    """Represents a single trade recommendation."""

    ticker: str
    action: str
    shares: int
    value: float
    price: float
    current_weight: float
    target_weight: float
    drift: float
    priority: str
    rationale: str = ""
    sector: str = ""


@dataclass
class Scenario:
    """Represents a rebalancing scenario."""

    scenario_type: ScenarioType
    trades: List[Trade] = field(default_factory=list)
    total_capital: float = 0.0
    num_trades: int = 0
    expected_max_drift: float = 0.0
    expected_sharpe_impact: float = 0.0
    expected_var_impact: float = 0.0
    score: float = 0.0
    tradeoffs: str = ""

    def calculate_turnover(self, portfolio_value: float) -> float:
        """Calculate turnover ratio for this scenario."""
        total_trade_value = sum(trade.value for trade in self.trades)
        return total_trade_value / portfolio_value if portfolio_value > 0 else 0.0


@dataclass
class MonitorResult:
    """Result from Monitor Agent."""

    status: DecisionStatus
    trigger_reason: str
    max_position_drift: float
    max_position_ticker: str
    max_sector_drift: float
    max_sector: str
    var_95: float
    sharpe_ratio: float
    beta: float
    market_regime: str
    days_since_rebalance: int
    timestamp: datetime = field(default_factory=datetime.now)

    def should_trigger_analyzer(self) -> bool:
        """Determine if Analyzer Agent should be triggered."""
        return self.status in [DecisionStatus.TRIGGER, DecisionStatus.ALERT]


@dataclass
class AnalyzerResult:
    """Result from Analyzer Agent."""

    scenarios: List[Scenario]
    recommended_scenario: Optional[Scenario] = None
    confidence: float = 0.0
    market_regime: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Decision:
    """Final decision from Decision Agent."""

    decision_id: str
    decision_status: DecisionStatus
    chosen_scenario: Optional[Scenario] = None
    reasoning: str = ""
    execution_timing: str = ""
    adaptive_adjustments: List[str] = field(default_factory=list)
    confidence: float = 0.0
    expected_sharpe_impact: float = 0.0
    expected_var_impact: float = 0.0
    total_turnover: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert decision to dictionary for logging."""
        return {
            "decision_id": self.decision_id,
            "status": self.decision_status.value,
            "scenario_type": (
                self.chosen_scenario.scenario_type.value
                if self.chosen_scenario
                else None
            ),
            "num_trades": (
                self.chosen_scenario.num_trades if self.chosen_scenario else 0
            ),
            "total_capital": (
                self.chosen_scenario.total_capital if self.chosen_scenario else 0.0
            ),
            "reasoning": self.reasoning,
            "execution_timing": self.execution_timing,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DecisionLog:
    """Tracks decision history for learning."""

    decisions: List[Decision] = field(default_factory=list)

    def add_decision(self, decision: Decision) -> None:
        """Add a decision to the log."""
        self.decisions.append(decision)

    def get_recent_decisions(self, limit: int = 10) -> List[Decision]:
        """Get recent decisions."""
        return sorted(self.decisions, key=lambda d: d.timestamp, reverse=True)[:limit]

    def calculate_regret_score(self, decision: Decision, actual_outcome: Dict) -> float:
        """Calculate regret score based on actual outcomes."""
        pass
