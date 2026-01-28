"""
Integration tests for rebalancing workflow.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.workflows.rebalance_workflow import RebalanceWorkflow
from src.models.decision import DecisionStatus


class TestRebalanceWorkflow:
    """Tests for RebalanceWorkflow."""
    
    def test_workflow_creation(self):
        """Test creating a workflow."""
        workflow = RebalanceWorkflow()
        assert workflow.monitor_agent is not None
        assert workflow.analyzer_agent is not None
        assert workflow.decision_agent is not None
    
    @patch('src.workflows.rebalance_workflow.MonitorAgent')
    @patch('src.workflows.rebalance_workflow.AnalyzerAgent')
    @patch('src.workflows.rebalance_workflow.DecisionAgent')
    def test_run_cycle_no_trigger(self, mock_decision, mock_analyzer, mock_monitor):
        """Test workflow cycle when monitor doesn't trigger."""
        mock_monitor_instance = MagicMock()
        mock_monitor_instance.assess_situation.return_value = MagicMock(
            should_trigger=False,
            trigger_reason=None
        )
        mock_monitor.return_value = mock_monitor_instance
        
        workflow = RebalanceWorkflow()
        decision = workflow.run_cycle()
        
        assert decision.decision_status == DecisionStatus.NO_ACTION
        mock_analyzer.return_value.evaluate_scenarios.assert_not_called()
    
    @patch('src.workflows.rebalance_workflow.MonitorAgent')
    @patch('src.workflows.rebalance_workflow.AnalyzerAgent')
    @patch('src.workflows.rebalance_workflow.DecisionAgent')
    def test_run_cycle_with_trigger(self, mock_decision, mock_analyzer, mock_monitor):
        """Test full workflow cycle with trigger."""
        from src.models.decision import MonitorResult, AnalyzerResult, Scenario, ScenarioType
        from src.models.portfolio import Portfolio, RiskMetrics
        from datetime import datetime
        
        monitor_result = MonitorResult(
            should_trigger=True,
            trigger_reason="High drift",
            portfolio_snapshot=Portfolio("TEST", 1000000.0, datetime.utcnow()),
            risk_metrics=RiskMetrics(-1.5, 2.0, 1.2, 0.15, datetime.utcnow()),
            market_regime="MODERATE"
        )
        
        scenario = Scenario(
            scenario_type=ScenarioType.PARTIAL_REBALANCE,
            trades=[],
            total_capital=10000.0,
            num_trades=2,
            score=8.0
        )
        
        analyzer_result = AnalyzerResult(
            recommended_scenario=scenario,
            confidence=0.85,
            all_scenarios=[scenario]
        )
        
        mock_monitor_instance = MagicMock()
        mock_monitor_instance.assess_situation.return_value = monitor_result
        mock_monitor.return_value = mock_monitor_instance
        
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.evaluate_scenarios.return_value = analyzer_result
        mock_analyzer.return_value = mock_analyzer_instance
        
        mock_decision_instance = MagicMock()
        mock_decision_instance.make_final_decision.return_value = MagicMock(
            decision_status=DecisionStatus.EXECUTE,
            chosen_scenario=scenario
        )
        mock_decision.return_value = mock_decision_instance
        
        workflow = RebalanceWorkflow()
        decision = workflow.run_cycle()
        
        mock_monitor_instance.assess_situation.assert_called_once()
        mock_analyzer_instance.evaluate_scenarios.assert_called_once()
        mock_decision_instance.make_final_decision.assert_called_once()
    
    def test_decision_history(self):
        """Test decision history tracking."""
        workflow = RebalanceWorkflow()
        
        assert len(workflow.get_decision_history()) == 0
    
    def test_export_decision(self, tmp_path, sample_scenario):
        """Test exporting decision to JSON."""
        from src.models.decision import Decision, DecisionStatus
        from datetime import datetime
        
        decision = Decision(
            decision_id="test_001",
            timestamp=datetime.utcnow(),
            decision_status=DecisionStatus.EXECUTE,
            chosen_scenario=sample_scenario,
            confidence=0.85,
            reasoning="Test decision"
        )
        
        workflow = RebalanceWorkflow()
        
        export_path = tmp_path / "decision.json"
        workflow.export_decision(decision, str(export_path))
        
        assert export_path.exists()
        assert export_path.stat().st_size > 0
