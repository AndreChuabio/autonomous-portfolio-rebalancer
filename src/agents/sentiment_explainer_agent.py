"""
Sentiment Explainer Agent - Provides news-based context for rebalancing decisions.

Queries Neo4j via MCP to explain WHY positions are being rebalanced based on 
recent sentiment and news events.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.utils.mcp_client import MCPClient
from src.models.portfolio import Position


@dataclass
class SentimentContext:
    """Sentiment context for a ticker."""
    ticker: str
    recent_sentiment: float
    sentiment_trend: str  # "improving", "deteriorating", "stable"
    article_count: int
    key_headlines: List[str]
    bearish_count: int
    bullish_count: int
    neutral_count: int
    explanation: str


class SentimentExplainerAgent:
    """
    Agent that provides sentiment-based explanations for rebalancing decisions.

    Role: Enhance decision transparency by linking portfolio actions to news/sentiment.
    """

    def __init__(self, mcp_client: MCPClient):
        """Initialize Sentiment Explainer Agent with MCP client."""
        self.mcp_client = mcp_client

    def explain_rebalancing(self, positions_to_change: Dict[str, float],
                            all_tickers: List[str]) -> Dict[str, SentimentContext]:
        """
        Generate sentiment-based explanations for rebalancing actions.

        Args:
            positions_to_change: Dict of ticker -> weight_change (e.g., {"AAPL": -0.05})
            all_tickers: List of all tickers in portfolio

        Returns:
            Dict mapping ticker to sentiment context
        """
        print("\n[SENTIMENT EXPLAINER] Generating news-based context...")

        sentiment_contexts = {}

        for ticker in positions_to_change.keys():
            context = self._analyze_ticker_sentiment(ticker)
            sentiment_contexts[ticker] = context

        return sentiment_contexts

    def _analyze_ticker_sentiment(self, ticker: str, days: int = 7) -> SentimentContext:
        """
        Analyze recent sentiment for a ticker.

        Args:
            ticker: Stock ticker symbol
            days: Days of history to analyze

        Returns:
            SentimentContext with analysis
        """
        try:
            articles_data = self.mcp_client.call_tool(
                "mcp_mcp-yfinance-_get_recent_articles",
                symbol=ticker,
                limit=10
            )

            stats_data = self.mcp_client.call_tool(
                "mcp_mcp-yfinance-_get_sentiment_statistics"
            )

            sentiment_avg, bullish, bearish, neutral, article_count = self._parse_stats(
                stats_data, ticker
            )

            key_headlines = self._extract_key_headlines(articles_data, limit=3)

            sentiment_trend = self._determine_trend(
                sentiment_avg, bearish, bullish)

            explanation = self._generate_explanation(
                ticker, sentiment_avg, sentiment_trend,
                bullish, bearish, neutral, key_headlines
            )

            return SentimentContext(
                ticker=ticker,
                recent_sentiment=sentiment_avg,
                sentiment_trend=sentiment_trend,
                article_count=article_count,
                key_headlines=key_headlines,
                bearish_count=bearish,
                bullish_count=bullish,
                neutral_count=neutral,
                explanation=explanation
            )

        except Exception as e:
            print(f"Warning: Could not fetch sentiment for {ticker}: {e}")
            return self._create_fallback_context(ticker)

    def _parse_stats(self, stats_data: str, ticker: str) -> tuple:
        """Parse sentiment statistics from MCP response."""
        lines = stats_data.strip().split('\n')

        for line in lines:
            if ticker in line:
                parts = line.split('|')
                if len(parts) >= 7:
                    try:
                        total = int(parts[1].strip())
                        avg_score = float(parts[2].strip())
                        bullish = int(parts[5].strip())
                        bearish = int(parts[6].strip())
                        neutral = int(parts[7].strip())
                        return avg_score, bullish, bearish, neutral, total
                    except (ValueError, IndexError):
                        pass

        return 0.0, 0, 0, 0, 0

    def _extract_key_headlines(self, articles_data: str, limit: int = 3) -> List[str]:
        """Extract top headlines from articles data."""
        headlines = []
        lines = articles_data.split('\n')

        for line in lines:
            if line.startswith('**') and '**' in line[2:]:
                headline = line.split('**')[1].strip()
                if headline and len(headline) > 10:
                    headlines.append(headline)
                if len(headlines) >= limit:
                    break

        return headlines

    def _determine_trend(self, avg_sentiment: float, bearish: int, bullish: int) -> str:
        """Determine sentiment trend from distribution."""
        if bearish > bullish * 1.5:
            return "deteriorating"
        elif bullish > bearish * 1.5:
            return "improving"
        elif avg_sentiment > 0.1:
            return "improving"
        elif avg_sentiment < -0.1:
            return "deteriorating"
        else:
            return "stable"

    def _generate_explanation(self, ticker: str, sentiment: float, trend: str,
                              bullish: int, bearish: int, neutral: int,
                              headlines: List[str]) -> str:
        """Generate natural language explanation."""
        total = bullish + bearish + neutral

        if total == 0:
            return f"No recent sentiment data available for {ticker}."

        sentiment_desc = "neutral"
        if sentiment > 0.15:
            sentiment_desc = "bullish"
        elif sentiment < -0.15:
            sentiment_desc = "bearish"

        explanation = f"{ticker} sentiment is {sentiment_desc} "
        explanation += f"(score: {sentiment:.3f}) with trend {trend}. "

        if bearish > 0:
            explanation += f"Recent coverage shows {bearish} bearish, "
            explanation += f"{bullish} bullish, {neutral} neutral articles. "

        if headlines:
            explanation += f"Key headlines: '{headlines[0]}'"
            if len(headlines) > 1:
                explanation += f", '{headlines[1]}'"

        return explanation

    def _create_fallback_context(self, ticker: str) -> SentimentContext:
        """Create fallback context when data unavailable."""
        return SentimentContext(
            ticker=ticker,
            recent_sentiment=0.0,
            sentiment_trend="unknown",
            article_count=0,
            key_headlines=[],
            bearish_count=0,
            bullish_count=0,
            neutral_count=0,
            explanation=f"No sentiment data available for {ticker}."
        )

    def format_sentiment_report(self, contexts: Dict[str, SentimentContext]) -> str:
        """
        Format sentiment contexts into readable report.

        Args:
            contexts: Dict of ticker -> SentimentContext

        Returns:
            Formatted report string
        """
        if not contexts:
            return "No sentiment data to report."

        report = "\n" + "=" * 63
        report += "\nSENTIMENT-BASED REBALANCING CONTEXT"
        report += "\n" + "=" * 63

        for ticker, context in contexts.items():
            report += f"\n\n{ticker} ({context.article_count} articles):"
            report += f"\n  Sentiment: {context.recent_sentiment:.3f} ({context.sentiment_trend})"
            report += f"\n  Distribution: {context.bullish_count} bullish, "
            report += f"{context.bearish_count} bearish, {context.neutral_count} neutral"

            if context.key_headlines:
                report += "\n  Recent Headlines:"
                for headline in context.key_headlines[:2]:
                    report += f"\n    - {headline[:80]}..."

            report += f"\n  Explanation: {context.explanation}"

        report += "\n" + "=" * 63

        return report
