"""
Pytest configuration and shared fixtures.
"""

from datetime import datetime

import pytest

from src.models.decision import (Decision, DecisionStatus, Scenario,
                                 ScenarioType, Trade)
from src.models.portfolio import Portfolio, Position, RiskMetrics


@pytest.fixture
def sample_portfolio():
    """Create a sample portfolio for testing."""
    portfolio = Portfolio(
        portfolio_id="TEST_PORTFOLIO",
        total_value=1000000.0,
        timestamp=datetime.utcnow(),
    )

    portfolio.add_position(
        Position(
            ticker="AAPL",
            target_weight=0.10,
            current_weight=0.12,
            drift=0.02,
            current_value=120000.0,
            target_value=100000.0,
            shares=400,
            price=300.0,
        )
    )

    portfolio.add_position(
        Position(
            ticker="NVDA",
            target_weight=0.08,
            current_weight=0.06,
            drift=-0.02,
            current_value=60000.0,
            target_value=80000.0,
            shares=300,
            price=200.0,
        )
    )

    return portfolio


@pytest.fixture
def sample_risk_metrics():
    """Create sample risk metrics for testing."""
    return RiskMetrics(
        var_95=-1.5,
        sharpe_ratio=2.0,
        beta=1.2,
        volatility=0.15,
        timestamp=datetime.utcnow(),
    )


@pytest.fixture
def sample_scenario():
    """Create a sample rebalancing scenario."""
    trades = [
        Trade(
            ticker="AAPL",
            action="SELL",
            shares=50,
            value=-15000.0,
            priority="HIGH",
            rationale="2% overweight",
        ),
        Trade(
            ticker="NVDA",
            action="BUY",
            shares=100,
            value=20000.0,
            priority="HIGH",
            rationale="2% underweight",
        ),
    ]

    return Scenario(
        scenario_type=ScenarioType.PARTIAL_REBALANCE,
        trades=trades,
        total_capital=35000.0,
        num_trades=2,
        turnover_pct=0.035,
        max_position_drift_after=0.01,
        score=8.5,
        reasoning="Fix high-drift positions efficiently",
    )


@pytest.fixture
def mock_mcp_client(mocker):
    """Create a mock MCP client."""
    client = mocker.MagicMock()

    # Mock portfolio holdings response
    client.query_portfolio_holdings.return_value = {
        "portfolio_id": "TEST_PORTFOLIO",
        "total_value": 1000000.0,
        "positions": [
            {"ticker": "AAPL", "shares": 400, "value": 120000.0},
            {"ticker": "NVDA", "shares": 300, "value": 60000.0},
        ],
    }

    # Mock risk metrics response
    client.query_risk_metrics.return_value = {
        "var_95": -1.5,
        "sharpe_ratio": 2.0,
        "beta": 1.2,
        "volatility": 0.15,
    }

    # Mock stock info response
    client.get_stock_info.return_value = {"regularMarketPrice": 300.0}

    return client
