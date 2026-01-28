"""
Unit tests for calculation utilities.
"""

import pytest
from src.utils.calculations import (
    calculate_weight_drift,
    calculate_sector_weights,
    calculate_implied_weights,
    calculate_rebalancing_trades,
)
from config.settings import TARGET_ALLOCATION, SECTOR_MAPPING


class TestWeightDrift:
    """Tests for weight drift calculations."""

    def test_calculate_drift_overweight(self):
        """Test drift calculation for overweight position."""
        current_weights = {"AAPL": 0.12, "NVDA": 0.08}
        target_weights = {"AAPL": 0.10, "NVDA": 0.08}
        drift = calculate_weight_drift(current_weights, target_weights)
        assert drift["AAPL"] == pytest.approx(0.02, abs=0.0001)

    def test_calculate_drift_underweight(self):
        """Test drift calculation for underweight position."""
        current_weights = {"NVDA": 0.06}
        target_weights = {"NVDA": 0.08}
        drift = calculate_weight_drift(current_weights, target_weights)
        assert drift["NVDA"] == pytest.approx(0.02, abs=0.0001)

    def test_calculate_drift_exact(self):
        """Test drift when current equals target."""
        current_weights = {"AAPL": 0.10}
        target_weights = {"AAPL": 0.10}
        drift = calculate_weight_drift(current_weights, target_weights)
        assert drift["AAPL"] == 0.0


class TestSectorWeights:
    """Tests for sector weight calculations."""

    def test_calculate_sector_weights(self):
        """Test sector weight aggregation."""
        position_weights = {
            "AAPL": 0.12,
            "MSFT": 0.10,
            "NVDA": 0.08,
            "XOM": 0.04,
            "CVX": 0.04,
        }

        sector_weights = calculate_sector_weights(position_weights)

        assert "Technology" in sector_weights
        assert "Energy" in sector_weights
        assert sector_weights["Technology"] == pytest.approx(0.30, abs=0.0001)
        assert sector_weights["Energy"] == pytest.approx(0.08, abs=0.0001)

    def test_calculate_sector_weights_empty(self):
        """Test sector weights with empty positions."""
        sector_weights = calculate_sector_weights({})
        assert len(sector_weights) == 0


class TestImpliedWeights:
    """Tests for implied weight calculations."""

    def test_calculate_implied_weights_no_change(self):
        """Test implied weights with no price changes."""
        target_weights = {"AAPL": 0.10, "NVDA": 0.08, "SPY": 0.15}

        price_changes = {"AAPL": 0.0, "NVDA": 0.0, "SPY": 0.0}

        implied = calculate_implied_weights(target_weights, price_changes)

        total = sum(implied.values())
        assert total == pytest.approx(1.0, abs=0.0001)
        assert implied["AAPL"] == pytest.approx(0.303, abs=0.01)

    def test_calculate_implied_weights_with_gains(self):
        """Test implied weights after price gains."""
        target_weights = {"AAPL": 0.10, "NVDA": 0.10}

        price_changes = {"AAPL": 0.0, "NVDA": 0.2}

        implied = calculate_implied_weights(target_weights, price_changes)

        assert implied["NVDA"] > implied["AAPL"]


class TestRebalanceTrades:
    """Tests for rebalance trade calculations."""

    def test_calculate_rebalancing_trades(self):
        """Test trade calculation for multiple positions."""
        current_weights = {"AAPL": 0.14, "NVDA": 0.06}
        target_weights = {"AAPL": 0.10, "NVDA": 0.08}
        live_prices = {"AAPL": 300.0, "NVDA": 200.0}
        portfolio_value = 1000000.0

        trades = calculate_rebalancing_trades(
            current_weights, target_weights, live_prices, portfolio_value
        )

        assert "AAPL" in trades
        assert "NVDA" in trades
        assert trades["AAPL"]["action"] == "SELL"
        assert trades["NVDA"]["action"] == "BUY"

    def test_calculate_rebalancing_trades_no_drift(self):
        """Test when weights are already at target."""
        current_weights = {"AAPL": 0.10, "NVDA": 0.08}
        target_weights = {"AAPL": 0.10, "NVDA": 0.08}
        live_prices = {"AAPL": 300.0, "NVDA": 200.0}
        portfolio_value = 1000000.0

        trades = calculate_rebalancing_trades(
            current_weights, target_weights, live_prices, portfolio_value
        )

        assert len(trades) == 0
