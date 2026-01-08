"""
Place Real Orders in Paper Invest Account
Uses actual MCP yfinance server (not mock client).

Run this manually through the MCP interface to place real orders.
"""

import time

# Portfolio allocation based on PORT_A_TechGrowth
# With $23,101.62 buying power

ORDERS = [
    # Technology (9.75% each)
    {"symbol": "AAPL", "shares": 9},
    {"symbol": "MSFT", "shares": 6},
    {"symbol": "GOOGL", "shares": 13},
    {"symbol": "NVDA", "shares": 12},
    {"symbol": "META", "shares": 7},
    {"symbol": "XLK", "shares": 12},

    # Energy (2.47% each)
    {"symbol": "XOM", "shares": 5},
    {"symbol": "CVX", "shares": 4},
    {"symbol": "COP", "shares": 5},
    {"symbol": "XLE", "shares": 7},

    # Benchmarks (10.54% each)
    {"symbol": "SPY", "shares": 5},
    {"symbol": "QQQ", "shares": 7},
    {"symbol": "IWM", "shares": 14},
]

print("=" * 70)
print("PAPER INVEST ORDER PLACEMENT")
print("=" * 70)
print("\nIMPORTANT: This script requires manual execution through MCP.")
print("The orders below need to be placed using mcp_mcp-yfinance-_place_buy_order\n")

for i, order in enumerate(ORDERS, 1):
    print(f"{i}. BUY {order['shares']} shares of {order['symbol']}")

print("\n" + "=" * 70)
print(f"Total: {len(ORDERS)} orders to place")
print("=" * 70)
print("\nTo execute these orders, use the Copilot interface to call:")
print("mcp_mcp-yfinance-_place_buy_order for each ticker")
print("\nAdd 12-second delay between orders to avoid rate limits.")
