"""
Batch analyze all articles for portfolio tickers
"""

# Portfolio tickers
PORTFOLIO_TICKERS = [
    # Tech
    "AAPL", "MSFT", "GOOGL", "NVDA", "META", "XLK",
    # Energy
    "XOM", "CVX", "COP", "XLE",
    # Benchmarks
    "SPY", "QQQ", "IWM"
]

print("Portfolio Sentiment Analysis")
print("=" * 60)
print(f"Analyzing {len(PORTFOLIO_TICKERS)} tickers")
print(f"Tickers: {', '.join(PORTFOLIO_TICKERS)}")
print("=" * 60)

# This script will guide Copilot to:
# 1. Fetch all articles for each ticker
# 2. Check which articles need analysis (no copilot_sentiment)
# 3. Analyze with FinBERT
# 4. Write results to Neo4j

print("\nEXECUTION PLAN:")
print("1. For each ticker:")
print("   - Fetch all articles via MCP")
print("   - Filter articles without copilot_sentiment")
print("   - Analyze each with FinBERT")
print("   - Write sentiment to Neo4j")
print("\n2. Generate summary report")
print("   - Total articles analyzed")
print("   - Breakdown by ticker")
print("   - Sentiment distribution")

print("\nNOTE: This requires Copilot to execute MCP tool calls")
print("Copilot will process articles in batches to enrich the database.")
