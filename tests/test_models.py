"""
Unit tests for data models.
"""
import pytest
from datetime import datetime
from src.models.portfolio import Portfolio, Position, RiskMetrics
from src.models.decision import (
    Decision, Scenario, Trade, 
    ScenarioType, DecisionStatus, MonitorResult, AnalyzerResult
)


class TestPosition:
    """Tests for Position model."""
    
    def test_position_creation(self):
        """Test creating a position with all fields."""
        position = Position(
            ticker="AAPL",
            target_weight=0.10,
            current_weight=0.12,
            drift=0.02,
            current_value=120000.0,
            target_value=100000.0,
            shares=400,
            price=300.0
        )
        
        assert position.ticker == "AAPL"
        assert position.drift == 0.02
        assert position.is_overweight()
        assert not position.is_underweight()
    
    def test_position_underweight(self):
        """Test underweight position detection."""
        position = Position(
            ticker="NVDA",
            target_weight=0.08,
            current_weight=0.06,
            drift=-0.02
        )
        
        assert position.is_underweight()
        assert not position.is_overweight()
    
    def test_position_drift_magnitude(self):
        """Test drift magnitude calculation."""
        position = Position(
            ticker="AAPL",
            target_weight=0.10,
            current_weight=0.13,
            drift=0.03
        )
        
        assert position.drift_magnitude() == 0.03


class TestPortfolio:
    """Tests for Portfolio model."""
    
    def test_portfolio_creation(self, sample_portfolio):
        """Test creating a portfolio."""
        assert sample_portfolio.portfolio_id == "TEST_PORTFOLIO"
        assert sample_portfolio.total_value == 1000000.0
        assert len(sample_portfolio.positions) == 2
    
    def test_get_position(self, sample_portfolio):
        """Test getting a specific position."""
        position = sample_portfolio.get_position("AAPL")
        assert position is not None
        assert position.ticker == "AAPL"
        
        missing = sample_portfolio.get_position("TSLA")
        assert missing is None
    
    def test_max_drift(self, sample_portfolio):
        """Test finding maximum drift."""
        max_drift = sample_portfolio.max_drift()
        assert max_drift == 0.02
    
    def test_positions_by_drift(self, sample_portfolio):
        """Test getting positions sorted by drift."""
        sorted_positions = sample_portfolio.positions_by_drift()
        assert sorted_positions[0].ticker == "AAPL"
        assert sorted_positions[0].drift == 0.02


class TestRiskMetrics:
    """Tests for RiskMetrics model."""
    
    def test_risk_metrics_creation(self, sample_risk_metrics):
        """Test creating risk metrics."""
        assert sample_risk_metrics.var_95 == -1.5
        assert sample_risk_metrics.sharpe_ratio == 2.0
        assert sample_risk_metrics.beta == 1.2
    
    def test_risk_level_classification(self):
        """Test risk level classification."""
        low_risk = RiskMetrics(var_95=-1.0, sharpe_ratio=2.5, beta=0.8, volatility=0.10)
        high_risk = RiskMetrics(var_95=-5.0, sharpe_ratio=0.5, beta=1.8, volatility=0.30)
        
        assert low_risk.is_healthy()
        assert not high_risk.is_healthy()


class TestTrade:
    """Tests for Trade model."""
    
    def test_trade_creation(self):
        """Test creating a trade."""
        trade = Trade(
            ticker="AAPL",
            action="SELL",
            shares=50,
            value=-15000.0,
            priority="HIGH",
            rationale="Overweight by 2%"
        )
        
        assert trade.ticker == "AAPL"
        assert trade.action == "SELL"
        assert trade.is_sell()
        assert not trade.is_buy()
    
    def test_trade_buy(self):
        """Test buy trade detection."""
        trade = Trade(
            ticker="NVDA",
            action="BUY",
            shares=100,
            value=20000.0,
            priority="MEDIUM"
        )
        
        assert trade.is_buy()
        assert not trade.is_sell()


class TestScenario:
    """Tests for Scenario model."""
    
    def test_scenario_creation(self, sample_scenario):
        """Test creating a scenario."""
        assert sample_scenario.scenario_type == ScenarioType.PARTIAL_REBALANCE
        assert sample_scenario.num_trades == 2
        assert sample_scenario.total_capital == 35000.0
    
    def test_defer_scenario(self):
        """Test defer scenario."""
        scenario = Scenario(
            scenario_type=ScenarioType.DEFER,
            trades=[],
            total_capital=0.0,
            num_trades=0,
            score=3.0,
            reasoning="Market conditions unfavorable"
        )
        
        assert scenario.scenario_type == ScenarioType.DEFER
        assert scenario.num_trades == 0
        assert len(scenario.trades) == 0


class TestDecision:
    """Tests for Decision model."""
    
    def test_decision_creation(self, sample_scenario):
        """Test creating a decision."""
        decision = Decision(
            decision_id="test_001",
            timestamp=datetime.utcnow(),
            decision_status=DecisionStatus.EXECUTE,
            chosen_scenario=sample_scenario,
            confidence=0.85,
            reasoning="High drift requires immediate action",
            execution_timing="IMMEDIATE"
        )
        
        assert decision.decision_id == "test_001"
        assert decision.decision_status == DecisionStatus.EXECUTE
        assert decision.confidence == 0.85
    
    def test_decision_defer(self):
        """Test defer decision."""
        decision = Decision(
            decision_id="test_002",
            timestamp=datetime.utcnow(),
            decision_status=DecisionStatus.DEFER,
            confidence=0.60,
            reasoning="Market volatility too high"
        )
        
        assert decision.decision_status == DecisionStatus.DEFER
        assert decision.chosen_scenario is None
