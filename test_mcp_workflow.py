"""
Full sentiment analysis workflow with MCP integration
"""

from src.agents.sentiment_analyzer_agent import SentimentAnalyzerAgent
from src.utils.mcp_client import MCPClient


def analyze_and_write_sentiment(ticker: str, limit: int = 3):
    """
    Fetch articles, analyze with FinBERT, and write back to Neo4j.

    Args:
        ticker: Stock symbol
        limit: Number of articles to analyze
    """
    print(f"\n{'='*60}")
    print(f"SENTIMENT ANALYSIS WORKFLOW FOR {ticker}")
    print(f"{'='*60}\n")

    # Initialize analyzer
    mcp_client = MCPClient()
    analyzer = SentimentAnalyzerAgent(mcp_client)

    # Note: Article fetching and writing happens via MCP tools
    # This script demonstrates the workflow, but actual MCP calls
    # need to be made by Copilot during execution

    print(f"Step 1: Fetch recent articles for {ticker}")
    print(
        f"   → Calling: mcp_mcp-yfinance-_get_recent_articles({ticker}, limit={limit})")
    print(f"   → Copilot will execute this MCP call...\n")

    # Placeholder for articles (in real execution, Copilot fetches these)
    print(f"Step 2: For each article without copilot_sentiment:")
    print(f"   → Check: mcp_mcp-yfinance-_has_copilot_sentiment(url)")
    print(f"   → If not analyzed, run FinBERT analysis")
    print(f"   → Write results: mcp_mcp-yfinance-_write_article_sentiment(...)\n")

    print(f"Step 3: Summary")
    print(f"   → Report: X articles analyzed, Y skipped (cached)")

    print(f"\n{'='*60}")
    print(f"WORKFLOW REQUIRES COPILOT MCP INTERACTION")
    print(f"{'='*60}")
    print("\nTo execute this workflow:")
    print("1. Copilot fetches articles via MCP")
    print("2. For each article:")
    print("   a. Check if already analyzed (has_copilot_sentiment)")
    print("   b. If not, call analyzer.analyze_article()")
    print("   c. Write results via write_article_sentiment")
    print("3. Return summary of analyzed/skipped counts")

    return {
        "ticker": ticker,
        "status": "ready",
        "note": "Requires Copilot MCP tool invocation"
    }


if __name__ == "__main__":
    # Test for AAPL
    result = analyze_and_write_sentiment("AAPL", limit=5)
    print(f"\nResult: {result}")
