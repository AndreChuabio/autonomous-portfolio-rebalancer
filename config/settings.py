"""
Configuration settings for the Autonomous Rebalancing Agent.
"""

from typing import Dict

PORTFOLIO_ID = "PORT_A_TechGrowth"
PORTFOLIO_BASIS = 1_000_000

TARGET_ALLOCATION: Dict[str, float] = {
    "AAPL": 0.10,
    "MSFT": 0.10,
    "GOOGL": 0.10,
    "NVDA": 0.08,
    "META": 0.07,
    "XLK": 0.10,
    "XOM": 0.04,
    "CVX": 0.04,
    "COP": 0.02,
    "XLE": 0.02,
    "SPY": 0.15,
    "QQQ": 0.13,
    "IWM": 0.05,
}

SECTOR_ALLOCATION: Dict[str, float] = {
    "Technology": 0.55,
    "Energy": 0.12,
    "Benchmarks": 0.33,
}

SECTOR_MAPPING: Dict[str, str] = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL": "Technology",
    "NVDA": "Technology",
    "META": "Technology",
    "XLK": "Technology",
    "XOM": "Energy",
    "CVX": "Energy",
    "COP": "Energy",
    "XLE": "Energy",
    "SPY": "Benchmarks",
    "QQQ": "Benchmarks",
    "IWM": "Benchmarks",
}

DRIFT_THRESHOLD_CRITICAL = 0.03
DRIFT_THRESHOLD_HIGH = 0.025
DRIFT_THRESHOLD_MEDIUM = 0.015

VAR_THRESHOLD_CRITICAL = -0.04
VAR_THRESHOLD_WARNING = -0.03

SHARPE_THRESHOLD_WARNING = 1.0
SHARPE_THRESHOLD_CRITICAL = 0.0

BETA_THRESHOLD = 1.5

MAX_TURNOVER_RATIO = 0.20

REBALANCE_COOLDOWN_DAYS = 3

MARKET_REGIME_THRESHOLDS = {
    "LOW_VOL": {"sharpe": 2.0, "var": -0.02},
    "MODERATE": {"sharpe": 1.0, "var": -0.025},
    "HIGH_VOL": {"sharpe": 0.5, "var": -0.035},
    "CRISIS": {"sharpe": 0.0, "var": -0.04},
}
