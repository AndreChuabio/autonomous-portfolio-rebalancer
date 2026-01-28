"""
Unit tests for calculation utilities.
"""
import pytest
from src.utils.calculations import (
    calculate_weight_drift,
    calculate_sector_weights,
    calculate_implied_weights,
    calculate_rebalance_trades
)
from config.settings import TARGET_ALLOCATION, SECTOR_MAPPING


class TestWeightDrift:
    """Tests for weight drift calculations."""
    
    def test_calculate_drift_overweight(self):
        """Test drift calculation for overweight position."""
        drift = calculate_weight_drift(
            current_weight=0.12,
            target_weight=0.10
        )
        assert drift == pytest.approx(0.02, abs=0.0001)
    
    def test_calculate_drift_underweight(self):
        """Test drift calculation for underweight position."""
        drift = calculate_weight_drift(
            current_weight=0.06,
            target_weight=0.08
        )
        assert drift == pytest.approx(-0.02, abs=0.0001)
    
    def test_calculate_drift_exact(self):
        """Test drift when current equals target."""
        drift = calculate_weight_drift(
            current_weight=0.10,
            target_weight=0.10
        )
        assert drift == 0.0


class TestSectorWeights:
    """Tests for sector weight calculations."""
    
    def test_calculate_sector_weights(self):
        """Test sector weight aggregation."""
        position_weights = {
            "AAPL": 0.12,
            "MSFT": 0.10,
            "NVDA": 0.08,
            "XOM": 0.04,
            "CVX": 0.04
        }
        
        sector_weights = calculate_sector_weights(
            position_weights, 
            SECTOR_MAPPING
        )
        
        assert "TECHNOLOGY" in sector_weights
        assert "ENERGY" in sector_weights
        assert sector_weights["TECHNOLOGY"] == pytest.approx(0.30, abs=0.0001)
        assert sector_weights["ENERGY"] == pytest.approx(0.08, abs=0.0001)
    
    def test_calculate_sector_weights_empty(self):
        """Test sector weights with empty positions."""
        sector_weights = calculate_sector_weights({}, SECTOR_MAPPING)
        assert len(sector_weights) == 0


class TestImpliedWeights:
    """Tests for implied weight calculations."""
    
    def test_calculate_implied_weights_no_change(self):
        """Test implied weights with no price changes."""
        current_weights = {
            "AAPL": 0.10,
            "NVDA": 0.08,
            "SPY": 0.15
        }
        
        price_changes = {
            "AAPL": 1.0,
            "NVDA": 1.0,
            "SPY": 1.0
        }
        
        implied = calculate_implied_weights(current_weights, price_changes)
        
        assert implied["AAPL"] == pytest.approx(0.10, abs=0.0001)
        assert implied["NVDA"] == pytest.approx(0.08, abs=0.0001)
        assert implied["SPY"] == pytest.approx(0.15, abs=0.0001)
    
    def test_calculate_implied_weights_with_gains(self):
        """Test implied weights after price gains."""
        current_weights = {
            "AAPL": 0.10,
            "NVDA": 0.10
        }
        
        price_changes = {
            "AAPL": 1.0,
            "NVDA": 1.2
        }
        
        implied = calculate_implied_weights(current_weights, price_changes)
        
        assert implied["NVDA"] > implied["AAPL"]


class TestRebalanceTrades:
    """Tests for rebalance trade calculations."""
    
    def test_calculate_trades_overweight(self):
        """Test trade calculation for overweight position."""
        trades = calculate_rebalance_trades(
            ticker="AAPL",
            current_value=120000.0,
            target_value=100000.0,
            current_price=300.0
        )
        
        assert trades["action"] == "SELL"
        assert trades["shares"] > 0
        assert trades["value"] < 0
    
    def test_calculate_trades_underweight(self):
        """Test trade calculation for underweight position."""
        trades = calculate_rebalance_trades(
            ticker="NVDA",
            current_value=60000.0,
            target_value=80000.0,
            current_price=200.0
        )
        
        assert trades["action"] == "BUY"
        assert trades["shares"] > 0
        assert trades["value"] > 0
    
    def test_calculate_trades_exact_weight(self):
        """Test when no trade needed."""
        trades = calculate_rebalance_trades(
            ticker="AAPL",
            current_value=100000.0,
            target_value=100000.0,
            current_price=300.0
        )
        
        assert trades["shares"] == 0
        assert trades["value"] == 0.0
