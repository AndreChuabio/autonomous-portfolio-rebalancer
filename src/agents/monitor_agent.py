"""
Monitor Agent - Phase 1: Situation Assessment
Continuously tracks portfolio drift and decides when deeper analysis is needed.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

from config.settings import (DRIFT_THRESHOLD_CRITICAL, PORTFOLIO_BASIS,
                             SECTOR_ALLOCATION, SECTOR_MAPPING,
                             SHARPE_THRESHOLD_WARNING, TARGET_ALLOCATION,
                             VAR_THRESHOLD_WARNING)
from src.models.decision import DecisionStatus, MonitorResult
from src.models.portfolio import Portfolio, Position, RiskMetrics
from src.utils.calculations import (calculate_implied_weights,
                                    calculate_sector_drift,
                                    calculate_sector_weights,
                                    calculate_weight_drift,
                                    classify_market_regime)
from src.utils.mcp_client import MCPClient


class MonitorAgent:
    """
    Monitor Agent for detecting portfolio drift and triggering analysis.

    Autonomous Goal: Maintain situational awareness and decide when deeper
    analysis is needed based on drift thresholds and market conditions.
    """

    def __init__(self, mcp_client: Optional[MCPClient] = None):
        """
        Initialize Monitor Agent.

        Args:
            mcp_client: MCP client for data retrieval
        """
        self.mcp_client = mcp_client or MCPClient()
        self.last_assessment_time: Optional[datetime] = None

    def assess_situation(self) -> MonitorResult:
        """
        Assess current portfolio situation and decide if analysis is needed.

        Returns:
            MonitorResult with status and metrics
        """
        print("\n[PHASE 1: MONITOR AGENT] Starting situation assessment...")

        portfolio = self._fetch_portfolio_data()
        risk_metrics = self._fetch_risk_metrics()

        max_position_ticker, max_position_drift = portfolio.get_max_drift()

        sector_weights = portfolio.get_sector_weights()
        sector_drift = calculate_sector_drift(sector_weights, SECTOR_ALLOCATION)
        max_sector = (
            max(sector_drift.keys(), key=lambda s: sector_drift[s])
            if sector_drift
            else ""
        )
        max_sector_drift = sector_drift.get(max_sector, 0.0)

        market_regime = classify_market_regime(
            risk_metrics.sharpe_ratio, risk_metrics.var_95
        )

        days_since_rebalance = self._estimate_days_since_rebalance(portfolio)

        status = self._determine_status(
            max_position_drift, max_sector_drift, risk_metrics, market_regime
        )

        trigger_reason = self._generate_trigger_reason(
            status, max_position_drift, max_sector_drift, risk_metrics, market_regime
        )

        result = MonitorResult(
            status=status,
            trigger_reason=trigger_reason,
            max_position_drift=max_position_drift,
            max_position_ticker=max_position_ticker,
            max_sector_drift=max_sector_drift,
            max_sector=max_sector,
            var_95=risk_metrics.var_95,
            sharpe_ratio=risk_metrics.sharpe_ratio,
            beta=risk_metrics.beta,
            market_regime=market_regime,
            days_since_rebalance=days_since_rebalance,
        )

        self.last_assessment_time = datetime.now()

        print(f"Status: {status.value}")
        print(f"Trigger Reason: {trigger_reason}")
        print(f"Max Position Drift: {max_position_drift:.2%} ({max_position_ticker})")
        print(f"Max Sector Drift: {max_sector_drift:.2%} ({max_sector})")
        print(f"Market Regime: {market_regime}")

        return result

    def _fetch_portfolio_data(self) -> Portfolio:
        """
        Fetch and construct portfolio from MongoDB and live prices.

        Returns:
            Portfolio object with current state
        """
        print("Fetching portfolio data from MongoDB...")
        holdings = self.mcp_client.query_portfolio_holdings(limit=100)

        portfolio = Portfolio(
            portfolio_id="PORT_A_TechGrowth", total_value=PORTFOLIO_BASIS
        )

        price_changes = {}
        live_prices = {}

        print(f"Fetching live prices for {len(TARGET_ALLOCATION)} tickers...")
        for ticker in TARGET_ALLOCATION.keys():
            stock_info = self.mcp_client.get_stock_info(ticker)

            live_price = stock_info.get("regularMarketPrice", 0.0)
            if live_price == 0.0:
                live_price = stock_info.get("currentPrice", 0.0)

            live_prices[ticker] = live_price

            stored_price = self._get_stored_price(holdings, ticker)

            if stored_price > 0 and live_price > 0:
                price_change = (live_price - stored_price) / stored_price
                price_changes[ticker] = price_change
            else:
                price_changes[ticker] = 0.0

        implied_weights = calculate_implied_weights(TARGET_ALLOCATION, price_changes)
        drift = calculate_weight_drift(implied_weights, TARGET_ALLOCATION)

        for ticker, target_weight in TARGET_ALLOCATION.items():
            position = Position(
                ticker=ticker,
                target_weight=target_weight,
                current_weight=implied_weights.get(ticker, 0.0),
                stored_price=self._get_stored_price(holdings, ticker),
                live_price=live_prices.get(ticker, 0.0),
                drift=drift.get(ticker, 0.0),
                sector=SECTOR_MAPPING.get(ticker, ""),
                value=PORTFOLIO_BASIS * implied_weights.get(ticker, 0.0),
            )
            portfolio.add_position(position)

        return portfolio

    def _fetch_risk_metrics(self) -> RiskMetrics:
        """
        Fetch latest risk metrics from MongoDB.

        Returns:
            RiskMetrics object
        """
        print("Fetching risk metrics from MongoDB...")
        metrics = self.mcp_client.query_risk_metrics(limit=1)

        if metrics and len(metrics) > 0:
            metric = metrics[0]
            return RiskMetrics(
                date=datetime.now(),
                var_95=metric.get("VaR_95", -0.02),
                expected_shortfall=metric.get("expected_shortfall", -0.03),
                sharpe_ratio=metric.get("Sharpe", 1.5),
                beta=metric.get("beta", 1.0),
                volatility=metric.get("volatility", 0.015),
            )
        else:
            return RiskMetrics(
                date=datetime.now(),
                var_95=-0.02,
                expected_shortfall=-0.03,
                sharpe_ratio=1.5,
                beta=1.0,
                volatility=0.015,
            )

    def _get_stored_price(self, holdings: list, ticker: str) -> float:
        """Extract stored price for ticker from holdings."""
        for holding in holdings:
            if holding.get("ticker") == ticker:
                return holding.get("price", 0.0)
        return 0.0

    def _estimate_days_since_rebalance(self, portfolio: Portfolio) -> int:
        """Estimate days since last rebalance."""
        if portfolio.last_rebalance_date:
            return (datetime.now() - portfolio.last_rebalance_date).days
        return 7

    def _determine_status(
        self,
        max_position_drift: float,
        max_sector_drift: float,
        risk_metrics: RiskMetrics,
        market_regime: str,
    ) -> DecisionStatus:
        """
        Determine monitor status based on metrics.

        Args:
            max_position_drift: Maximum position drift
            max_sector_drift: Maximum sector drift
            risk_metrics: Current risk metrics
            market_regime: Market regime classification

        Returns:
            DecisionStatus
        """
        if (
            max_position_drift >= DRIFT_THRESHOLD_CRITICAL
            or max_sector_drift >= 0.05
            or risk_metrics.var_95 < VAR_THRESHOLD_WARNING
            or risk_metrics.sharpe_ratio < SHARPE_THRESHOLD_WARNING
            or market_regime == "CRISIS"
        ):
            return DecisionStatus.TRIGGER

        elif (
            max_position_drift >= 0.02
            or max_sector_drift >= 0.03
            or risk_metrics.var_95 < -0.025
        ):
            return DecisionStatus.ALERT

        else:
            return DecisionStatus.MONITORING

    def _generate_trigger_reason(
        self,
        status: DecisionStatus,
        max_position_drift: float,
        max_sector_drift: float,
        risk_metrics: RiskMetrics,
        market_regime: str,
    ) -> str:
        """Generate human-readable trigger reason."""
        if status == DecisionStatus.MONITORING:
            return "All metrics within normal ranges"

        reasons = []

        if max_position_drift >= DRIFT_THRESHOLD_CRITICAL:
            reasons.append(
                f"Max drift {max_position_drift:.1%} exceeds {DRIFT_THRESHOLD_CRITICAL:.1%} threshold"
            )

        if max_sector_drift >= 0.05:
            reasons.append(f"Sector drift {max_sector_drift:.1%} exceeds 5% threshold")

        if risk_metrics.var_95 < VAR_THRESHOLD_WARNING:
            reasons.append(f"VaR {risk_metrics.var_95:.2%} below warning threshold")

        if risk_metrics.sharpe_ratio < SHARPE_THRESHOLD_WARNING:
            reasons.append(
                f"Sharpe {risk_metrics.sharpe_ratio:.2f} below warning threshold"
            )

        if market_regime == "CRISIS":
            reasons.append("Crisis market regime detected")

        return " + ".join(reasons) if reasons else "Elevated risk metrics"
