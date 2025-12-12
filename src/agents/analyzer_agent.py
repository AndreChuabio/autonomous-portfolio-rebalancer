"""
Analyzer Agent - Phase 2: Scenario Evaluation
Evaluates multiple rebalancing scenarios and compares trade-offs.
"""

from typing import List, Dict
from datetime import datetime

from src.models.portfolio import Portfolio, Position
from src.models.decision import (
    Scenario, ScenarioType, Trade, AnalyzerResult, MonitorResult
)
from src.utils.mcp_client import MCPClient
from src.utils.calculations import calculate_rebalancing_trades
from config.settings import (
    TARGET_ALLOCATION,
    PORTFOLIO_BASIS,
    DRIFT_THRESHOLD_CRITICAL,
    DRIFT_THRESHOLD_HIGH,
    DRIFT_THRESHOLD_MEDIUM,
    MAX_TURNOVER_RATIO
)


class AnalyzerAgent:
    """
    Analyzer Agent for evaluating rebalancing scenarios.

    Autonomous Goal: Find optimal rebalancing strategy given current
    market conditions by evaluating trade-offs.
    """

    def __init__(self, mcp_client: MCPClient):
        """
        Initialize Analyzer Agent.

        Args:
            mcp_client: MCP client for data retrieval
        """
        self.mcp_client = mcp_client

    def evaluate_scenarios(self, monitor_result: MonitorResult,
                           portfolio: Portfolio) -> AnalyzerResult:
        """
        Evaluate multiple rebalancing scenarios.

        Args:
            monitor_result: Result from Monitor Agent
            portfolio: Current portfolio state

        Returns:
            AnalyzerResult with evaluated scenarios
        """
        print("\n[PHASE 2: ANALYZER AGENT] Evaluating scenarios...")
        print(f"Market Regime: {monitor_result.market_regime}")

        scenarios = []

        scenario_full = self._evaluate_full_rebalance(portfolio)
        scenarios.append(scenario_full)
        print(f"Full Rebalance: {scenario_full.num_trades} trades, "
              f"${scenario_full.total_capital:,.0f}, Score: {scenario_full.score:.1f}/10")

        scenario_partial = self._evaluate_partial_rebalance(portfolio)
        scenarios.append(scenario_partial)
        print(f"Partial Rebalance: {scenario_partial.num_trades} trades, "
              f"${scenario_partial.total_capital:,.0f}, Score: {scenario_partial.score:.1f}/10")

        scenario_sector = self._evaluate_sector_rebalance(portfolio)
        scenarios.append(scenario_sector)
        print(f"Sector Rebalance: {scenario_sector.num_trades} trades, "
              f"${scenario_sector.total_capital:,.0f}, Score: {scenario_sector.score:.1f}/10")

        scenario_defer = self._evaluate_defer(portfolio, monitor_result)
        scenarios.append(scenario_defer)
        print(f"Defer: {scenario_defer.num_trades} trades, "
              f"Score: {scenario_defer.score:.1f}/10")

        recommended = self._select_best_scenario(scenarios, monitor_result)
        confidence = self._calculate_confidence(
            recommended, scenarios, monitor_result)

        print(
            f"\nRecommended: {recommended.scenario_type.value} (Confidence: {confidence:.0%})")

        return AnalyzerResult(
            scenarios=scenarios,
            recommended_scenario=recommended,
            confidence=confidence,
            market_regime=monitor_result.market_regime
        )

    def _evaluate_full_rebalance(self, portfolio: Portfolio) -> Scenario:
        """
        Evaluate full rebalancing scenario - correct all positions.

        Args:
            portfolio: Current portfolio state

        Returns:
            Scenario object
        """
        trades = []

        current_weights = {
            p.ticker: p.current_weight for p in portfolio.positions.values()}
        live_prices = {
            p.ticker: p.live_price for p in portfolio.positions.values()}

        trade_dict = calculate_rebalancing_trades(
            current_weights,
            TARGET_ALLOCATION,
            live_prices,
            PORTFOLIO_BASIS
        )

        for ticker, trade_data in trade_dict.items():
            position = portfolio.get_position(ticker)
            trade = Trade(
                ticker=ticker,
                action=trade_data["action"],
                shares=trade_data["shares"],
                value=trade_data["trade_value"],
                price=trade_data["price"],
                current_weight=trade_data["current_weight"],
                target_weight=trade_data["target_weight"],
                drift=trade_data["drift"],
                priority=trade_data["priority"],
                sector=position.sector if position else "",
                rationale=f"Full rebalance to target {trade_data['target_weight']:.1%}"
            )
            trades.append(trade)

        total_capital = sum(t.value for t in trades)
        num_trades = len(trades)

        score = self._score_full_rebalance(num_trades, total_capital)

        return Scenario(
            scenario_type=ScenarioType.FULL_REBALANCE,
            trades=trades,
            total_capital=total_capital,
            num_trades=num_trades,
            expected_max_drift=0.0,
            expected_sharpe_impact=0.05,
            expected_var_impact=-0.002,
            score=score,
            tradeoffs="High turnover, immediate correction, risk-neutral"
        )

    def _evaluate_partial_rebalance(self, portfolio: Portfolio) -> Scenario:
        """
        Evaluate partial rebalancing scenario - correct only high drift positions.

        Args:
            portfolio: Current portfolio state

        Returns:
            Scenario object
        """
        trades = []

        positions_high_drift = portfolio.get_positions_by_drift(
            min_drift=DRIFT_THRESHOLD_MEDIUM)

        current_weights = {
            p.ticker: p.current_weight for p in portfolio.positions.values()}
        live_prices = {
            p.ticker: p.live_price for p in portfolio.positions.values()}

        trade_dict = calculate_rebalancing_trades(
            current_weights,
            TARGET_ALLOCATION,
            live_prices,
            PORTFOLIO_BASIS
        )

        for position in positions_high_drift:
            if position.ticker in trade_dict:
                trade_data = trade_dict[position.ticker]
                trade = Trade(
                    ticker=position.ticker,
                    action=trade_data["action"],
                    shares=trade_data["shares"],
                    value=trade_data["trade_value"],
                    price=trade_data["price"],
                    current_weight=trade_data["current_weight"],
                    target_weight=trade_data["target_weight"],
                    drift=trade_data["drift"],
                    priority=trade_data["priority"],
                    sector=position.sector,
                    rationale=f"Drift {position.drift:.1%} exceeds threshold"
                )
                trades.append(trade)

        total_capital = sum(t.value for t in trades)
        num_trades = len(trades)

        remaining_max_drift = max([p.drift for p in portfolio.positions.values()
                                  if p.ticker not in [t.ticker for t in trades]],
                                  default=0.0)

        score = self._score_partial_rebalance(
            num_trades, total_capital, remaining_max_drift)

        return Scenario(
            scenario_type=ScenarioType.PARTIAL_REBALANCE,
            trades=trades,
            total_capital=total_capital,
            num_trades=num_trades,
            expected_max_drift=remaining_max_drift,
            expected_sharpe_impact=0.02,
            expected_var_impact=-0.001,
            score=score,
            tradeoffs="Lower cost, incomplete fix, addresses worst offenders"
        )

    def _evaluate_sector_rebalance(self, portfolio: Portfolio) -> Scenario:
        """
        Evaluate sector rebalancing scenario - focus on sector allocation.

        Args:
            portfolio: Current portfolio state

        Returns:
            Scenario object
        """
        trades = []

        current_weights = {
            p.ticker: p.current_weight for p in portfolio.positions.values()}
        live_prices = {
            p.ticker: p.live_price for p in portfolio.positions.values()}

        trade_dict = calculate_rebalancing_trades(
            current_weights,
            TARGET_ALLOCATION,
            live_prices,
            PORTFOLIO_BASIS
        )

        sector_etfs = ["XLK", "XLE", "SPY", "QQQ", "IWM"]

        for ticker in sector_etfs:
            if ticker in trade_dict:
                trade_data = trade_dict[ticker]
                position = portfolio.get_position(ticker)
                trade = Trade(
                    ticker=ticker,
                    action=trade_data["action"],
                    shares=trade_data["shares"],
                    value=trade_data["trade_value"],
                    price=trade_data["price"],
                    current_weight=trade_data["current_weight"],
                    target_weight=trade_data["target_weight"],
                    drift=trade_data["drift"],
                    priority=trade_data["priority"],
                    sector=position.sector if position else "",
                    rationale="Sector allocation rebalance"
                )
                trades.append(trade)

        total_capital = sum(t.value for t in trades)
        num_trades = len(trades)

        score = self._score_sector_rebalance(num_trades, total_capital)

        return Scenario(
            scenario_type=ScenarioType.SECTOR_REBALANCE,
            trades=trades,
            total_capital=total_capital,
            num_trades=num_trades,
            expected_max_drift=0.02,
            expected_sharpe_impact=0.01,
            expected_var_impact=0.0,
            score=score,
            tradeoffs="Maintains stock picks, corrects macro allocation"
        )

    def _evaluate_defer(self, portfolio: Portfolio,
                        monitor_result: MonitorResult) -> Scenario:
        """
        Evaluate defer scenario - wait and see.

        Args:
            portfolio: Current portfolio state
            monitor_result: Monitor result

        Returns:
            Scenario object
        """
        score = self._score_defer(monitor_result)

        return Scenario(
            scenario_type=ScenarioType.DEFER,
            trades=[],
            total_capital=0.0,
            num_trades=0,
            expected_max_drift=monitor_result.max_position_drift,
            expected_sharpe_impact=0.0,
            expected_var_impact=0.0,
            score=score,
            tradeoffs="Drift continues, avoid trading into volatility"
        )

    def _score_full_rebalance(self, num_trades: int, total_capital: float) -> float:
        """Score full rebalance scenario."""
        turnover = total_capital / PORTFOLIO_BASIS

        if turnover > MAX_TURNOVER_RATIO:
            return 4.0

        return 7.0 - (num_trades * 0.1)

    def _score_partial_rebalance(self, num_trades: int, total_capital: float,
                                 remaining_drift: float) -> float:
        """Score partial rebalance scenario."""
        turnover = total_capital / PORTFOLIO_BASIS

        base_score = 8.0

        if remaining_drift > DRIFT_THRESHOLD_HIGH:
            base_score -= 2.0

        if turnover > MAX_TURNOVER_RATIO * 0.5:
            base_score -= 1.0

        return max(base_score, 1.0)

    def _score_sector_rebalance(self, num_trades: int, total_capital: float) -> float:
        """Score sector rebalance scenario."""
        return 6.0 - (num_trades * 0.2)

    def _score_defer(self, monitor_result: MonitorResult) -> float:
        """Score defer scenario based on current conditions."""
        if monitor_result.market_regime == "CRISIS":
            return 8.0
        elif monitor_result.market_regime == "HIGH_VOL":
            return 6.0
        elif monitor_result.max_position_drift > DRIFT_THRESHOLD_CRITICAL:
            return 2.0
        else:
            return 5.0

    def _select_best_scenario(self, scenarios: List[Scenario],
                              monitor_result: MonitorResult) -> Scenario:
        """
        Select best scenario based on scores and conditions.

        Args:
            scenarios: List of evaluated scenarios
            monitor_result: Monitor result

        Returns:
            Best scenario
        """
        if monitor_result.market_regime == "CRISIS":
            defer = next(s for s in scenarios if s.scenario_type ==
                         ScenarioType.DEFER)
            return defer

        return max(scenarios, key=lambda s: s.score)

    def _calculate_confidence(self, recommended: Scenario,
                              all_scenarios: List[Scenario],
                              monitor_result: MonitorResult) -> float:
        """
        Calculate confidence in recommendation.

        Args:
            recommended: Recommended scenario
            all_scenarios: All evaluated scenarios
            monitor_result: Monitor result

        Returns:
            Confidence score (0-1)
        """
        scores = [s.score for s in all_scenarios]
        max_score = max(scores)
        second_max = sorted(scores, reverse=True)[1] if len(scores) > 1 else 0

        score_gap = max_score - second_max

        base_confidence = min(0.6 + (score_gap * 0.1), 0.95)

        if monitor_result.market_regime == "LOW_VOL":
            base_confidence += 0.05
        elif monitor_result.market_regime == "CRISIS":
            base_confidence -= 0.1

        return max(min(base_confidence, 1.0), 0.5)
