"""
Calculation utilities for portfolio analysis.
"""

from typing import Dict, List, Tuple
from config.settings import TARGET_ALLOCATION, SECTOR_MAPPING, SECTOR_ALLOCATION


def calculate_weight_drift(
    current_weights: Dict[str, float], target_weights: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate drift between current and target weights.

    Args:
        current_weights: Current portfolio weights by ticker
        target_weights: Target portfolio weights by ticker

    Returns:
        Dictionary of drift values by ticker
    """
    drift = {}
    for ticker in target_weights:
        current = current_weights.get(ticker, 0.0)
        target = target_weights.get(ticker, 0.0)
        drift[ticker] = abs(current - target)
    return drift


def calculate_sector_weights(position_weights: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate sector weights from position weights.

    Args:
        position_weights: Position weights by ticker

    Returns:
        Dictionary of sector weights
    """
    sector_weights = {}
    for ticker, weight in position_weights.items():
        sector = SECTOR_MAPPING.get(ticker)
        if sector:
            sector_weights[sector] = sector_weights.get(sector, 0.0) + weight
    return sector_weights


def calculate_sector_drift(
    current_sector_weights: Dict[str, float], target_sector_weights: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate drift between current and target sector weights.

    Args:
        current_sector_weights: Current sector weights
        target_sector_weights: Target sector weights

    Returns:
        Dictionary of sector drift values
    """
    drift = {}
    for sector in target_sector_weights:
        current = current_sector_weights.get(sector, 0.0)
        target = target_sector_weights.get(sector, 0.0)
        drift[sector] = abs(current - target)
    return drift


def calculate_implied_weights(
    target_weights: Dict[str, float], price_changes: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate implied current weights based on price changes.

    Args:
        target_weights: Target portfolio weights
        price_changes: Price change ratios by ticker

    Returns:
        Dictionary of implied current weights
    """
    weighted_values = {}
    for ticker, target_weight in target_weights.items():
        price_change = price_changes.get(ticker, 0.0)
        weighted_values[ticker] = target_weight * (1 + price_change)

    total_value = sum(weighted_values.values())

    implied_weights = {}
    for ticker, value in weighted_values.items():
        implied_weights[ticker] = value / total_value if total_value > 0 else 0.0

    return implied_weights


def calculate_rebalancing_trades(
    current_weights: Dict[str, float],
    target_weights: Dict[str, float],
    live_prices: Dict[str, float],
    portfolio_value: float,
) -> Dict[str, Dict]:
    """
    Calculate rebalancing trades needed.

    Args:
        current_weights: Current portfolio weights
        target_weights: Target portfolio weights
        live_prices: Current live prices by ticker
        portfolio_value: Total portfolio value

    Returns:
        Dictionary of trade recommendations by ticker
    """
    trades = {}

    for ticker, target_weight in target_weights.items():
        current_weight = current_weights.get(ticker, 0.0)
        drift = abs(current_weight - target_weight)

        target_value = portfolio_value * target_weight
        current_value = portfolio_value * current_weight
        trade_value = target_value - current_value

        live_price = live_prices.get(ticker, 0.0)
        if live_price > 0:
            shares_to_trade = round(trade_value / live_price)

            if shares_to_trade != 0:
                trades[ticker] = {
                    "ticker": ticker,
                    "current_weight": current_weight,
                    "target_weight": target_weight,
                    "drift": drift,
                    "shares": abs(shares_to_trade),
                    "action": "BUY" if shares_to_trade > 0 else "SELL",
                    "trade_value": abs(trade_value),
                    "price": live_price,
                    "priority": get_trade_priority(drift),
                }

    return trades


def get_trade_priority(drift: float) -> str:
    """
    Determine trade priority based on drift magnitude.

    Args:
        drift: Drift value (absolute)

    Returns:
        Priority level (CRITICAL, HIGH, MEDIUM, LOW)
    """
    if drift >= 0.03:
        return "CRITICAL"
    elif drift >= 0.02:
        return "HIGH"
    elif drift >= 0.015:
        return "MEDIUM"
    else:
        return "LOW"


def calculate_turnover(trades: Dict[str, Dict]) -> float:
    """
    Calculate portfolio turnover from trades.

    Args:
        trades: Dictionary of trade recommendations

    Returns:
        Turnover ratio
    """
    total_trade_value = sum(trade["trade_value"] for trade in trades.values())
    return total_trade_value


def classify_market_regime(sharpe: float, var_95: float) -> str:
    """
    Classify market regime based on risk metrics.

    Args:
        sharpe: Sharpe ratio
        var_95: Value at Risk (95%)

    Returns:
        Market regime classification
    """
    if sharpe >= 2.0 and var_95 >= -0.02:
        return "LOW_VOL"
    elif sharpe >= 1.0 and var_95 >= -0.025:
        return "MODERATE"
    elif sharpe >= 0.5 and var_95 >= -0.035:
        return "HIGH_VOL"
    else:
        return "CRISIS"
