"""
Sentiment Analyzer Agent - Enriches articles with AI-generated sentiment scores.

This agent reads raw articles from Neo4j, analyzes their sentiment using AI reasoning,
and writes the scores back to Neo4j for use by the SentimentExplainerAgent.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArticleSentiment:
    """Structured sentiment analysis result."""
    score: float  # -1.0 to 1.0
    label: str  # bearish, neutral, bullish
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Why this sentiment
    themes: List[str]  # Key themes extracted
    trading_impact: str  # short_term_bearish, long_term_bullish, etc.
    analyzed_at: str  # ISO timestamp
    analyzed_by: str = "copilot"


class SentimentAnalyzerAgent:
    """
    Agent that analyzes article sentiment and enriches Neo4j with scores.

    This agent operates independently from the trading workflow, continuously
    enriching articles with sentiment data that can be consumed later.
    """

    def __init__(self, mcp_client):
        """
        Initialize sentiment analyzer.

        Args:
            mcp_client: MCP client for Neo4j operations
        """
        self.mcp_client = mcp_client
        self.analyzed_count = 0
        self.skipped_count = 0

    def analyze_all_tickers(self, tickers: List[str], days: int = 30,
                            force_reanalyze: bool = False) -> Dict[str, Any]:
        """
        Analyze articles for multiple tickers.

        Args:
            tickers: List of stock symbols to analyze
            days: How far back to analyze articles (default 30)
            force_reanalyze: Re-analyze even if sentiment exists

        Returns:
            Summary of analysis operation
        """
        print(f"\n🔬 SENTIMENT ANALYZER AGENT")
        print(f"Analyzing articles for {len(tickers)} tickers...")
        print(f"Lookback period: {days} days")
        print(f"Force re-analyze: {force_reanalyze}\n")

        results = {
            "analyzed": 0,
            "skipped": 0,
            "errors": 0,
            "by_ticker": {}
        }

        for ticker in tickers:
            try:
                ticker_result = self.analyze_ticker(
                    ticker, days, force_reanalyze)
                results["analyzed"] += ticker_result["analyzed"]
                results["skipped"] += ticker_result["skipped"]
                results["by_ticker"][ticker] = ticker_result
            except Exception as e:
                print(f"❌ Error analyzing {ticker}: {str(e)}")
                results["errors"] += 1
                results["by_ticker"][ticker] = {"error": str(e)}

        self._print_summary(results)
        return results

    def analyze_ticker(self, ticker: str, days: int = 30,
                       force_reanalyze: bool = False) -> Dict[str, Any]:
        """
        Analyze articles for a single ticker.

        Args:
            ticker: Stock symbol
            days: Lookback period
            force_reanalyze: Re-analyze existing sentiment

        Returns:
            Analysis results for this ticker
        """
        print(f"📊 Analyzing {ticker}...")

        # NOTE: This is where MCP server would be called
        # In actual implementation, this would:
        # 1. Call mcp_mcp-yfinance-_get_recent_articles(ticker, days)
        # 2. For each article without copilot_sentiment (or all if force_reanalyze):
        #    - Analyze article text (via AI assistant - that's me!)
        #    - Call mcp_mcp-yfinance-_write_article_sentiment(...)

        # For now, return placeholder showing what would happen
        result = {
            "ticker": ticker,
            "analyzed": 0,
            "skipped": 0,
            "needs_mcp_implementation": True,
            "message": "MCP write operations not yet implemented in server"
        }

        return result

    def analyze_article(self, article: Dict[str, Any], ticker: str) -> ArticleSentiment:
        """
        Analyze a single article and generate sentiment.

        This is where the AI analysis happens. The article text is examined
        for sentiment, themes, and trading implications.

        Args:
            article: Article data with title, summary, url, etc.
            ticker: Stock symbol this article relates to

        Returns:
            ArticleSentiment with detailed analysis
        """
        # Extract article content
        title = article.get("title", "")
        summary = article.get("summary", "")
        source = article.get("source", "unknown")

        # This is where AI analysis happens
        # In production, this function would be called BY the AI assistant
        # who would read the title/summary and provide structured analysis

        # For demonstration, show the expected output structure
        prompt_for_ai = f"""
Analyze this financial news article for {ticker}:

Title: {title}
Summary: {summary}
Source: {source}

Provide structured sentiment analysis:
1. Overall sentiment score (-1.0 to 1.0)
2. Label (bearish/neutral/bullish)
3. Confidence (0.0 to 1.0)
4. Reasoning (2-3 sentences explaining the sentiment)
5. Key themes (list of 2-5 themes)
6. Trading impact (e.g., "short_term_bearish", "long_term_bullish")
"""

        # Placeholder - in actual use, AI provides this
        return ArticleSentiment(
            score=0.0,
            label="neutral",
            confidence=0.5,
            reasoning="AI analysis would go here",
            themes=["needs_implementation"],
            trading_impact="neutral",
            analyzed_at=datetime.utcnow().isoformat(),
            analyzed_by="copilot"
        )

    def _print_summary(self, results: Dict[str, Any]):
        """Print analysis summary."""
        print("\n" + "="*60)
        print("📈 SENTIMENT ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total analyzed: {results['analyzed']}")
        print(f"Total skipped (already analyzed): {results['skipped']}")
        print(f"Errors: {results['errors']}")
        print("\nPer-ticker breakdown:")
        for ticker, ticker_result in results["by_ticker"].items():
            if "error" in ticker_result:
                print(f"  {ticker}: ❌ {ticker_result['error']}")
            else:
                analyzed = ticker_result.get("analyzed", 0)
                skipped = ticker_result.get("skipped", 0)
                print(f"  {ticker}: ✓ {analyzed} analyzed, {skipped} skipped")
        print("="*60 + "\n")


def analyze_sentiment_cli(tickers: Optional[List[str]] = None,
                          days: int = 30,
                          force: bool = False):
    """
    CLI entry point for sentiment analysis.

    Args:
        tickers: List of tickers to analyze (None = all portfolio tickers)
        days: Lookback period
        force: Force re-analysis of existing sentiment
    """
    from src.utils.mcp_client import MCPClient

    # Default to portfolio tickers if none specified
    if tickers is None:
        tickers = [
            "AAPL", "MSFT", "GOOGL", "NVDA", "META", "XLK",
            "XOM", "CVX", "COP", "XLE",
            "SPY", "QQQ", "IWM"
        ]

    mcp_client = MCPClient()
    analyzer = SentimentAnalyzerAgent(mcp_client)

    results = analyzer.analyze_all_tickers(
        tickers, days=days, force_reanalyze=force)

    return results
