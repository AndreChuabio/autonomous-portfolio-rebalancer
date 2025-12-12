"""
Data models for portfolio representation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Position:
    """Represents a single portfolio position."""
    ticker: str
    target_weight: float
    current_weight: float = 0.0
    stored_price: float = 0.0
    live_price: float = 0.0
    shares: int = 0
    value: float = 0.0
    drift: float = 0.0
    sector: str = ""
    daily_vol: float = 0.0


@dataclass
class Portfolio:
    """Represents the complete portfolio state."""
    portfolio_id: str
    total_value: float
    positions: Dict[str, Position] = field(default_factory=dict)
    snapshot_date: Optional[datetime] = None
    last_rebalance_date: Optional[datetime] = None

    def get_position(self, ticker: str) -> Optional[Position]:
        """Get position by ticker."""
        return self.positions.get(ticker)

    def add_position(self, position: Position) -> None:
        """Add or update a position."""
        self.positions[position.ticker] = position

    def get_max_drift(self) -> tuple[str, float]:
        """Get ticker and value of maximum drift."""
        if not self.positions:
            return "", 0.0
        max_ticker = max(self.positions.keys(),
                         key=lambda t: self.positions[t].drift)
        return max_ticker, self.positions[max_ticker].drift

    def get_sector_weights(self) -> Dict[str, float]:
        """Calculate current sector weights."""
        sector_weights = {}
        for position in self.positions.values():
            if position.sector:
                sector_weights[position.sector] = (
                    sector_weights.get(position.sector, 0.0) +
                    position.current_weight
                )
        return sector_weights

    def get_positions_by_drift(self, min_drift: float = 0.0) -> List[Position]:
        """Get positions sorted by drift, filtered by minimum."""
        filtered = [p for p in self.positions.values() if p.drift >= min_drift]
        return sorted(filtered, key=lambda p: p.drift, reverse=True)


@dataclass
class RiskMetrics:
    """Represents portfolio risk metrics."""
    date: datetime
    var_95: float
    expected_shortfall: float
    sharpe_ratio: float
    beta: float
    volatility: float

    def is_high_risk(self, var_threshold: float = -0.03,
                     sharpe_threshold: float = 1.0) -> bool:
        """Check if portfolio is in high risk state."""
        return self.var_95 < var_threshold or self.sharpe_ratio < sharpe_threshold
