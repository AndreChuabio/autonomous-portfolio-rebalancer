"""
Unit tests for agents.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.agents.monitor_agent import MonitorAgent
from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.decision_agent import DecisionAgent
from src.models.portfolio import Portfolio, Position, RiskMetrics
from src.models.decision import ScenarioType, DecisionStatus


class TestMonitorAgent:
    """Tests for MonitorAgent."""

    def test_monitor_creation(self, mock_mcp_client):
        """Test creating a monitor agent."""
        agent = MonitorAgent(mock_mcp_client)
        assert agent.mcp_client is not None

    def test_monitor_low_drift(self, mock_mcp_client, sample_portfolio):
        """Test monitoring with low drift (no trigger)."""
        sample_portfolio.positions[0].drift = 0.01
        sample_portfolio.positions[1].drift = -0.01

        agent = MonitorAgent(mock_mcp_client)

        with patch.object(
            agent,
            "_fetch_portfolio_state",
            return_value=(
                sample_portfolio,
                RiskMetrics(var_95=-1.5, sharpe_ratio=2.0, beta=1.2, volatility=0.15),
            ),
        ):
            result = agent.assess_situation()

        assert result.should_trigger is False
        assert result.trigger_reason is None

    def test_monitor_high_drift(self, mock_mcp_client, sample_portfolio):
        """Test monitoring with high drift (should trigger)."""
        sample_portfolio.positions[0].drift = 0.04

        agent = MonitorAgent(mock_mcp_client)

        with patch.object(
            agent,
            "_fetch_portfolio_state",
            return_value=(
                sample_portfolio,
                RiskMetrics(var_95=-1.5, sharpe_ratio=2.0, beta=1.2, volatility=0.15),
            ),
        ):
            result = agent.assess_situation()

        assert result.should_trigger is True
        assert "drift" in result.trigger_reason.lower()

    def test_market_regime_classification(self, mock_mcp_client):
        """Test market regime classification."""
        agent = MonitorAgent(mock_mcp_client)

        low_vol = RiskMetrics(var_95=-1.0, sharpe_ratio=2.5, beta=0.8, volatility=0.10)
        assert agent._classify_market_regime(low_vol) == "LOW_VOL"

        high_vol = RiskMetrics(var_95=-3.5, sharpe_ratio=1.0, beta=1.5, volatility=0.25)
        assert agent._classify_market_regime(high_vol) == "HIGH_VOL"

        crisis = RiskMetrics(var_95=-5.0, sharpe_ratio=0.3, beta=2.0, volatility=0.40)
        assert agent._classify_market_regime(crisis) == "CRISIS"


class TestAnalyzerAgent:
    """Tests for AnalyzerAgent."""

    def test_analyzer_creation(self, mock_mcp_client):
        """Test creating an analyzer agent."""
        agent = AnalyzerAgent(mock_mcp_client)
        assert agent.mcp_client is not None

    def test_generate_scenarios(
        self, mock_mcp_client, sample_portfolio, sample_risk_metrics
    ):
        """Test scenario generation."""
        agent = AnalyzerAgent(mock_mcp_client)

        scenarios = agent.generate_scenarios(sample_portfolio, sample_risk_metrics)

        assert len(scenarios) >= 4
        scenario_types = [s.scenario_type for s in scenarios]
        assert ScenarioType.FULL_REBALANCE in scenario_types
        assert ScenarioType.PARTIAL_REBALANCE in scenario_types
        assert ScenarioType.SECTOR_REBALANCE in scenario_types
        assert ScenarioType.DEFER in scenario_types

    def test_score_scenarios(
        self, mock_mcp_client, sample_portfolio, sample_risk_metrics
    ):
        """Test scenario scoring."""
        agent = AnalyzerAgent(mock_mcp_client)

        scenarios = agent.generate_scenarios(sample_portfolio, sample_risk_metrics)
        scored = agent.score_scenarios(scenarios, sample_portfolio, sample_risk_metrics)

        assert all(hasattr(s, "score") for s in scored)
        assert all(s.score >= 0 and s.score <= 10 for s in scored)

    def test_recommend_scenario(
        self, mock_mcp_client, sample_portfolio, sample_risk_metrics
    ):
        """Test scenario recommendation."""
        agent = AnalyzerAgent(mock_mcp_client)

        scenarios = agent.generate_scenarios(sample_portfolio, sample_risk_metrics)
        scored = agent.score_scenarios(scenarios, sample_portfolio, sample_risk_metrics)

        best, confidence = agent.recommend_best_scenario(scored)

        assert best is not None
        assert 0 <= confidence <= 1
        assert best.score == max(s.score for s in scored)


class TestDecisionAgent:
    """Tests for DecisionAgent."""

    def test_decision_creation(self, mock_mcp_client):
        """Test creating a decision agent."""
        agent = DecisionAgent(mock_mcp_client)
        assert agent.mcp_client is not None

    def test_make_decision_execute(
        self, mock_mcp_client, sample_scenario, sample_portfolio, sample_risk_metrics
    ):
        """Test making an execute decision."""
        agent = DecisionAgent(mock_mcp_client)

        from src.models.decision import MonitorResult, AnalyzerResult

        monitor_result = MonitorResult(
            should_trigger=True,
            trigger_reason="High drift detected",
            portfolio_snapshot=sample_portfolio,
            risk_metrics=sample_risk_metrics,
            market_regime="MODERATE",
        )

        analyzer_result = AnalyzerResult(
            recommended_scenario=sample_scenario,
            confidence=0.85,
            all_scenarios=[sample_scenario],
        )

        decision = agent.make_final_decision(monitor_result, analyzer_result)

        assert decision is not None
        assert decision.decision_status in [
            DecisionStatus.EXECUTE,
            DecisionStatus.DEFER,
        ]

    def test_adaptive_threshold_adjustment(self, mock_mcp_client):
        """Test adaptive threshold adjustments."""
        agent = DecisionAgent(mock_mcp_client)

        adjustments = agent._calculate_adaptive_adjustments(
            market_regime="HIGH_VOL", last_rebalance_days=2, max_drift=0.04
        )

        assert "threshold_adjustment" in adjustments
        assert "reasoning" in adjustments

    def test_execution_timing(
        self, mock_mcp_client, sample_scenario, sample_risk_metrics
    ):
        """Test execution timing determination."""
        agent = DecisionAgent(mock_mcp_client)

        timing = agent._determine_execution_timing(
            scenario=sample_scenario,
            market_regime="MODERATE",
            risk_metrics=sample_risk_metrics,
        )

        assert timing in ["IMMEDIATE", "GRADUAL", "DEFER"]
