"""
Rebalance Workflow - Orchestrates the 3-phase agentic workflow.
"""

from datetime import datetime
from typing import Optional, List, Dict
import json

from src.agents.monitor_agent import MonitorAgent
from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.decision_agent import DecisionAgent
from src.agents.sentiment_explainer_agent import SentimentExplainerAgent
from src.models.decision import Decision, DecisionLog, DecisionStatus, ScenarioType
from src.models.portfolio import Portfolio
from src.utils.mcp_client import MCPClient
from config.settings import PORTFOLIO_ID, PORTFOLIO_BASIS


class RebalanceWorkflow:
    """
    Orchestrates the autonomous rebalancing workflow.

    Workflow: Monitor → Analyzer → Decision → Report
    """

    def __init__(self):
        """Initialize workflow with agents."""
        self.mcp_client = MCPClient()
        self.monitor_agent = MonitorAgent(self.mcp_client)
        self.analyzer_agent = AnalyzerAgent(self.mcp_client)
        self.decision_agent = DecisionAgent()
        self.sentiment_explainer = SentimentExplainerAgent(self.mcp_client)
        self.decision_log = DecisionLog()

    def run_cycle(self) -> Decision:
        """
        Execute one complete rebalancing workflow cycle.

        Returns:
            Final decision
        """
        print("=" * 63)
        print(f"AUTONOMOUS REBALANCING AGENT: {PORTFOLIO_ID}")
        print(
            f"Cycle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Portfolio Basis: ${PORTFOLIO_BASIS:,}")
        print("=" * 63)

        monitor_result = self.monitor_agent.assess_situation()

        portfolio = self.monitor_agent._fetch_portfolio_data()

        if not monitor_result.should_trigger_analyzer():
            print(f"\nMonitor Decision: CONTINUE MONITORING (no action needed)")
            decision = self.decision_agent._create_defer_decision(
                f"MON-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                monitor_result.trigger_reason,
                monitor_result
            )
            self.decision_log.add_decision(decision)
            return decision

        print(f"\nMonitor Decision: TRIGGER ANALYZER AGENT")

        analyzer_result = self.analyzer_agent.evaluate_scenarios(
            monitor_result,
            portfolio
        )

        decision = self.decision_agent.make_decision(
            monitor_result,
            analyzer_result,
            portfolio
        )

        sentiment_context = None
        if decision.chosen_scenario and decision.chosen_scenario.adjusted_positions:
            positions_to_change = self._extract_position_changes(
                decision.chosen_scenario.adjusted_positions,
                portfolio
            )

            if positions_to_change:
                sentiment_context = self.sentiment_explainer.explain_rebalancing(
                    positions_to_change,
                    [p.ticker for p in portfolio.positions]
                )

        self.decision_log.add_decision(decision)

        self._print_final_report(
            decision, monitor_result, analyzer_result, portfolio, sentiment_context)

        return decision

    def _print_final_report(self, decision: Decision, monitor_result,
                            analyzer_result, portfolio: Portfolio,
                            sentiment_context=None) -> None:
        """
        Print comprehensive final report.

        Args:
            decision: Final decision
            monitor_result: Monitor result
            analyzer_result: Analyzer result
            portfolio: Portfolio state
            sentiment_context: Optional sentiment explanations
        """
        print("\n" + "=" * 63)
        print("FINAL DECISION REPORT")
        print("=" * 63)

        print(f"\nDecision ID: {decision.decision_id}")
        print(f"Status: {decision.decision_status.value}")
        print(f"Confidence: {decision.confidence:.0%}")

        if decision.chosen_scenario:
            print(
                f"\nChosen Scenario: {decision.chosen_scenario.scenario_type.value}")
            print(f"Number of Trades: {decision.chosen_scenario.num_trades}")
            print(
                f"Total Capital: ${decision.chosen_scenario.total_capital:,.0f}")
            print(f"Portfolio Turnover: {decision.total_turnover:.1%}")

        print(f"\nReasoning:")
        for reason in decision.reasoning.split(" | "):
            print(f"  - {reason}")

        print(f"\nExecution Timing: {decision.execution_timing}")

        if decision.adaptive_adjustments:
            print(f"\nAdaptive Adjustments:")
            for adjustment in decision.adaptive_adjustments:
                print(f"  - {adjustment}")

        if decision.chosen_scenario and decision.chosen_scenario.trades:
            print(f"\n{'-' * 63}")
            print("EXECUTION PLAN")
            print(f"{'-' * 63}")
            print(
                f"{'Priority':<9} | {'Ticker':<6} | {'Action':<4} | {'Shares':>6} | {'Value':>10} | Rationale")
            print(f"{'-' * 63}")

            sorted_trades = sorted(decision.chosen_scenario.trades,
                                   key=lambda t: (
                                       {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2,
                                        "LOW": 3}.get(t.priority, 4),
                                       -t.value
                                   ))

            for trade in sorted_trades:
                print(f"{trade.priority:<9} | {trade.ticker:<6} | {trade.action:<4} | "
                      f"{trade.shares:>6} | ${trade.value:>9,.0f} | {trade.rationale}")

            print(f"{'-' * 63}")
            print(f"Total: {len(decision.chosen_scenario.trades)} trades, "
                  f"${decision.chosen_scenario.total_capital:,.0f} turnover "
                  f"({decision.total_turnover:.2%} of portfolio)")

        print(f"\n{'-' * 63}")
        print("EXPECTED IMPACT")
        print(f"{'-' * 63}")
        print(f"Sharpe Ratio Impact: {decision.expected_sharpe_impact:+.2f}")
        print(f"VaR Impact: {decision.expected_var_impact:+.3%}")

        if decision.chosen_scenario:
            print(
                f"Expected Max Drift Post-Rebalance: {decision.chosen_scenario.expected_max_drift:.1%}")

        print(f"\n{'-' * 63}")
        print("LEARNING & FEEDBACK")
        print(f"{'-' * 63}")

        recent_decisions = self.decision_log.get_recent_decisions(limit=3)
        if len(recent_decisions) > 1:
            prev_decision = recent_decisions[1]
            print(f"Previous Decision: {prev_decision.decision_status.value} "
                  f"({prev_decision.timestamp.strftime('%Y-%m-%d')})")

            if prev_decision.decision_status == DecisionStatus.DEFER:
                print(f"Outcome: Drift increased from {monitor_result.max_position_drift - 0.01:.1%} "
                      f"to {monitor_result.max_position_drift:.1%}")

        print(f"\nLogged for Future Adaptation: [{decision.decision_id}]")

        if sentiment_context:
            sentiment_report = self.sentiment_explainer.format_sentiment_report(
                sentiment_context)
            print(sentiment_report)

        print("\n" + "=" * 63)
        print(f"AGENT STATUS: {decision.decision_status.value} - "
              f"{'AWAITING EXECUTION' if decision.decision_status == DecisionStatus.EXECUTE else 'MONITORING'}")
        print("=" * 63)

    def _extract_position_changes(self, adjusted_positions: List,
                                  portfolio: Portfolio) -> Dict[str, float]:
        """
        Extract which positions are changing and by how much.

        Args:
            adjusted_positions: List of adjusted position dicts
            portfolio: Current portfolio

        Returns:
            Dict of ticker -> weight_change
        """
        changes = {}
        current_weights = {p.ticker: p.weight for p in portfolio.positions}

        for adj_pos in adjusted_positions:
            ticker = adj_pos['ticker']
            new_weight = adj_pos['weight']
            old_weight = current_weights.get(ticker, 0.0)
            weight_change = new_weight - old_weight

            if abs(weight_change) > 0.01:
                changes[ticker] = weight_change

        return changes

    def get_decision_history(self, limit: int = 10) -> list:
        """
        Get recent decision history.

        Args:
            limit: Number of recent decisions to retrieve

        Returns:
            List of recent decisions
        """
        return self.decision_log.get_recent_decisions(limit)

    def export_decision(self, decision: Decision, filepath: str) -> None:
        """
        Export decision to JSON file.

        Args:
            decision: Decision to export
            filepath: Output file path
        """
        with open(filepath, 'w') as f:
            json.dump(decision.to_dict(), f, indent=2)
        print(f"\nDecision exported to: {filepath}")
