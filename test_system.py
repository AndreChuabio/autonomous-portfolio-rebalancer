"""
Test script to verify the system structure and imports.
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from config import settings
        print("✓ config.settings imported successfully")
    except Exception as e:
        print(f"✗ config.settings import failed: {e}")
        return False

    try:
        from src.models.portfolio import Portfolio, Position, RiskMetrics
        print("✓ src.models.portfolio imported successfully")
    except Exception as e:
        print(f"✗ src.models.portfolio import failed: {e}")
        return False

    try:
        from src.models.decision import (
            Decision, Scenario, Trade, MonitorResult,
            AnalyzerResult, DecisionStatus, ScenarioType
        )
        print("✓ src.models.decision imported successfully")
    except Exception as e:
        print(f"✗ src.models.decision import failed: {e}")
        return False

    try:
        from src.utils.mcp_client import MCPClient
        print("✓ src.utils.mcp_client imported successfully")
    except Exception as e:
        print(f"✗ src.utils.mcp_client import failed: {e}")
        return False

    try:
        from src.utils.calculations import (
            calculate_weight_drift,
            calculate_sector_weights,
            calculate_implied_weights
        )
        print("✓ src.utils.calculations imported successfully")
    except Exception as e:
        print(f"✗ src.utils.calculations import failed: {e}")
        return False

    try:
        from src.agents.monitor_agent import MonitorAgent
        print("✓ src.agents.monitor_agent imported successfully")
    except Exception as e:
        print(f"✗ src.agents.monitor_agent import failed: {e}")
        return False

    try:
        from src.agents.analyzer_agent import AnalyzerAgent
        print("✓ src.agents.analyzer_agent imported successfully")
    except Exception as e:
        print(f"✗ src.agents.analyzer_agent import failed: {e}")
        return False

    try:
        from src.agents.decision_agent import DecisionAgent
        print("✓ src.agents.decision_agent imported successfully")
    except Exception as e:
        print(f"✗ src.agents.decision_agent import failed: {e}")
        return False

    try:
        from src.workflows.rebalance_workflow import RebalanceWorkflow
        print("✓ src.workflows.rebalance_workflow imported successfully")
    except Exception as e:
        print(f"✗ src.workflows.rebalance_workflow import failed: {e}")
        return False

    return True


def test_configuration():
    """Test that configuration values are properly set."""
    print("\nTesting configuration...")

    from config.settings import (
        PORTFOLIO_ID, PORTFOLIO_BASIS, TARGET_ALLOCATION,
        SECTOR_ALLOCATION, SECTOR_MAPPING
    )

    print(f"✓ Portfolio ID: {PORTFOLIO_ID}")
    print(f"✓ Portfolio Basis: ${PORTFOLIO_BASIS:,}")
    print(f"✓ Target Allocation: {len(TARGET_ALLOCATION)} positions")
    print(f"✓ Sector Allocation: {len(SECTOR_ALLOCATION)} sectors")
    print(f"✓ Sector Mapping: {len(SECTOR_MAPPING)} tickers")

    total_allocation = sum(TARGET_ALLOCATION.values())
    print(f"✓ Total allocation: {total_allocation:.2%}")

    if abs(total_allocation - 1.0) > 0.001:
        print(f"✗ Warning: Total allocation is not 100%")
        return False

    return True


def test_model_creation():
    """Test that models can be instantiated."""
    print("\nTesting model creation...")

    from src.models.portfolio import Portfolio, Position
    from src.models.decision import Decision, Scenario, Trade, DecisionStatus, ScenarioType
    from datetime import datetime

    try:
        portfolio = Portfolio(portfolio_id="TEST", total_value=1000000)
        print("✓ Portfolio model created")
    except Exception as e:
        print(f"✗ Portfolio creation failed: {e}")
        return False

    try:
        position = Position(
            ticker="AAPL",
            target_weight=0.10,
            current_weight=0.11,
            drift=0.01
        )
        print("✓ Position model created")
    except Exception as e:
        print(f"✗ Position creation failed: {e}")
        return False

    try:
        scenario = Scenario(
            scenario_type=ScenarioType.DEFER,
            trades=[],
            total_capital=0.0,
            num_trades=0
        )
        print("✓ Scenario model created")
    except Exception as e:
        print(f"✗ Scenario creation failed: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("AUTONOMOUS REBALANCING AGENT - VERIFICATION TEST")
    print("=" * 60)

    all_passed = True

    if not test_imports():
        all_passed = False

    if not test_configuration():
        all_passed = False

    if not test_model_creation():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
        print("System is ready to run!")
        print("\nNext steps:")
        print("1. Ensure MCP yfinance server is configured")
        print("2. Run: python main.py --run")
    else:
        print("SOME TESTS FAILED")
        print("Please fix the issues above before running.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
