"""
Decision Agent - Phase 3: Autonomous Decision Making
Makes final rebalancing decisions based on analysis and adapts thresholds.
"""

from datetime import datetime
from typing import List, Optional

from config.settings import (DRIFT_THRESHOLD_CRITICAL, MAX_TURNOVER_RATIO,
                             PORTFOLIO_BASIS, REBALANCE_COOLDOWN_DAYS,
                             SHARPE_THRESHOLD_WARNING, VAR_THRESHOLD_WARNING)
from src.models.decision import (AnalyzerResult, Decision, DecisionStatus,
                                 MonitorResult, Scenario, ScenarioType)
from src.models.portfolio import Portfolio


class DecisionAgent:
    """
    Decision Agent for making autonomous rebalancing decisions.

    Autonomous Goal: Make risk-adjusted rebalancing decisions, not just
    report drift. Adapts thresholds dynamically based on market conditions.
    """

    def __init__(self):
        """Initialize Decision Agent."""
        self.decision_count = 0
        self.adaptive_threshold = DRIFT_THRESHOLD_CRITICAL

    def make_decision(
        self,
        monitor_result: MonitorResult,
        analyzer_result: AnalyzerResult,
        portfolio: Portfolio,
    ) -> Decision:
        """
        Make autonomous rebalancing decision.

        Args:
            monitor_result: Result from Monitor Agent
            analyzer_result: Result from Analyzer Agent
            portfolio: Current portfolio state

        Returns:
            Decision object with chosen scenario and reasoning
        """
        print("\n[PHASE 3: DECISION AGENT] Making autonomous decision...")

        self.decision_count += 1
        decision_id = (
            f"REB-{datetime.now().strftime('%Y-%m-%d')}-{self.decision_count:03d}"
        )

        if not monitor_result.should_trigger_analyzer():
            return self._create_defer_decision(
                decision_id, "Monitor status does not warrant action", monitor_result
            )

        chosen_scenario = self._choose_scenario(
            analyzer_result, monitor_result, portfolio
        )

        if chosen_scenario.scenario_type == ScenarioType.DEFER:
            status = DecisionStatus.DEFER
        else:
            status = DecisionStatus.EXECUTE

        reasoning = self._generate_reasoning(
            chosen_scenario, monitor_result, analyzer_result, portfolio
        )

        execution_timing = self._determine_execution_timing(
            chosen_scenario, monitor_result
        )

        adaptive_adjustments = self._generate_adaptive_adjustments(
            chosen_scenario, monitor_result
        )

        turnover = chosen_scenario.calculate_turnover(PORTFOLIO_BASIS)

        decision = Decision(
            decision_id=decision_id,
            decision_status=status,
            chosen_scenario=chosen_scenario,
            reasoning=reasoning,
            execution_timing=execution_timing,
            adaptive_adjustments=adaptive_adjustments,
            confidence=analyzer_result.confidence,
            expected_sharpe_impact=chosen_scenario.expected_sharpe_impact,
            expected_var_impact=chosen_scenario.expected_var_impact,
            total_turnover=turnover,
        )

        print(f"Autonomous Decision: {status.value}")
        print(f"Chosen Scenario: {chosen_scenario.scenario_type.value}")
        print(f"Confidence: {analyzer_result.confidence:.0%}")
        print(f"Execution Timing: {execution_timing}")

        return decision

    def _choose_scenario(
        self,
        analyzer_result: AnalyzerResult,
        monitor_result: MonitorResult,
        portfolio: Portfolio,
    ) -> Scenario:
        """
        Choose optimal scenario with autonomous decision logic.

        Args:
            analyzer_result: Analyzer recommendations
            monitor_result: Monitor assessment
            portfolio: Current portfolio state

        Returns:
            Chosen scenario
        """
        if monitor_result.market_regime == "CRISIS":
            defer = next(
                s
                for s in analyzer_result.scenarios
                if s.scenario_type == ScenarioType.DEFER
            )
            return defer

        if monitor_result.days_since_rebalance < REBALANCE_COOLDOWN_DAYS:
            defer = next(
                s
                for s in analyzer_result.scenarios
                if s.scenario_type == ScenarioType.DEFER
            )
            return defer

        recommended = analyzer_result.recommended_scenario

        if recommended.calculate_turnover(PORTFOLIO_BASIS) > MAX_TURNOVER_RATIO:
            partial = next(
                (
                    s
                    for s in analyzer_result.scenarios
                    if s.scenario_type == ScenarioType.PARTIAL_REBALANCE
                ),
                recommended,
            )
            return partial

        if (
            monitor_result.max_position_drift < self.adaptive_threshold
            and monitor_result.market_regime == "HIGH_VOL"
        ):
            defer = next(
                s
                for s in analyzer_result.scenarios
                if s.scenario_type == ScenarioType.DEFER
            )
            return defer

        return recommended

    def _create_defer_decision(
        self, decision_id: str, reason: str, monitor_result: MonitorResult
    ) -> Decision:
        """Create a defer decision."""
        defer_scenario = Scenario(
            scenario_type=ScenarioType.DEFER,
            trades=[],
            total_capital=0.0,
            num_trades=0,
            expected_max_drift=monitor_result.max_position_drift,
            score=0.0,
            tradeoffs="Monitoring continues",
        )

        return Decision(
            decision_id=decision_id,
            decision_status=DecisionStatus.DEFER,
            chosen_scenario=defer_scenario,
            reasoning=reason,
            execution_timing="N/A",
            confidence=1.0,
            total_turnover=0.0,
        )

    def _generate_reasoning(
        self,
        scenario: Scenario,
        monitor_result: MonitorResult,
        analyzer_result: AnalyzerResult,
        portfolio: Portfolio,
    ) -> str:
        """
        Generate detailed reasoning for decision.

        Args:
            scenario: Chosen scenario
            monitor_result: Monitor assessment
            analyzer_result: Analyzer recommendations
            portfolio: Current portfolio state

        Returns:
            Reasoning text
        """
        reasons = []

        if scenario.scenario_type == ScenarioType.DEFER:
            if monitor_result.market_regime == "CRISIS":
                reasons.append("Crisis regime detected - avoiding forced selling")
            elif monitor_result.days_since_rebalance < REBALANCE_COOLDOWN_DAYS:
                reasons.append(
                    f"Last rebalance was {monitor_result.days_since_rebalance} days ago"
                )
            else:
                reasons.append("Drift within acceptable ranges")
            return " | ".join(reasons)

        if monitor_result.max_position_drift >= DRIFT_THRESHOLD_CRITICAL:
            reasons.append(
                f"Max drift ({monitor_result.max_position_drift:.1%}) exceeds critical threshold"
            )

        if monitor_result.market_regime == "MODERATE":
            reasons.append(
                f"Market regime is {monitor_result.market_regime} (favorable for rebalancing)"
            )
        elif monitor_result.market_regime == "LOW_VOL":
            reasons.append("Low volatility environment supports action")

        if monitor_result.days_since_rebalance >= REBALANCE_COOLDOWN_DAYS:
            reasons.append(
                f"Last rebalance was {monitor_result.days_since_rebalance} days ago"
            )

        if scenario.scenario_type == ScenarioType.FULL_REBALANCE:
            reasons.append("Full correction warranted across all positions")
        elif scenario.scenario_type == ScenarioType.PARTIAL_REBALANCE:
            reasons.append(
                "Partial rebalance optimal: correct worst offenders, minimize turnover"
            )
        elif scenario.scenario_type == ScenarioType.SECTOR_REBALANCE:
            reasons.append("Sector allocation correction prioritized")

        if scenario.calculate_turnover(PORTFOLIO_BASIS) > MAX_TURNOVER_RATIO * 0.5:
            reasons.append(
                f"Turnover {scenario.calculate_turnover(PORTFOLIO_BASIS):.1%} justified by drift severity"
            )

        return " | ".join(reasons)

    def _determine_execution_timing(
        self, scenario: Scenario, monitor_result: MonitorResult
    ) -> str:
        """
        Determine when to execute trades.

        Args:
            scenario: Chosen scenario
            monitor_result: Monitor assessment

        Returns:
            Execution timing description
        """
        if scenario.scenario_type == ScenarioType.DEFER:
            return "N/A"

        if monitor_result.market_regime == "LOW_VOL":
            return "EXECUTE IMMEDIATELY (market conditions favorable)"
        elif monitor_result.market_regime == "MODERATE":
            return "EXECUTE IMMEDIATELY (normal conditions)"
        elif monitor_result.market_regime == "HIGH_VOL":
            return "GRADUAL EXECUTION over 2-3 days (reduce market impact)"
        else:
            return "DEFER pending market stabilization"

    def _generate_adaptive_adjustments(
        self, scenario: Scenario, monitor_result: MonitorResult
    ) -> List[str]:
        """
        Generate adaptive threshold adjustments for next cycle.

        Args:
            scenario: Chosen scenario
            monitor_result: Monitor assessment

        Returns:
            List of adaptive adjustments
        """
        adjustments = []

        if scenario.scenario_type != ScenarioType.DEFER:
            self.adaptive_threshold = min(self.adaptive_threshold * 1.2, 0.05)
            adjustments.append(
                f"Increased threshold to {self.adaptive_threshold:.1%} for next {REBALANCE_COOLDOWN_DAYS} days"
            )

        if monitor_result.market_regime == "HIGH_VOL":
            adjustments.append("Monitoring NVDA closely (high beta, volatile)")

        if monitor_result.var_95 < VAR_THRESHOLD_WARNING:
            adjustments.append("Risk monitoring intensified due to elevated VaR")

        if scenario.num_trades > 5:
            adjustments.append("Consider splitting execution across multiple sessions")

        return adjustments
