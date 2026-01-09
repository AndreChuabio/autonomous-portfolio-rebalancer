"""
Quick test of FinBERT sentiment analyzer
"""

from src.agents.sentiment_analyzer_agent import SentimentAnalyzerAgent
from src.utils.mcp_client import MCPClient

# Test article data
test_article = {
    "title": "The AI Throne Shifts: Alphabet Briefly Overtakes Apple as Monetization Momentum Rewrites Market Hierarchy",
    "summary": "Alphabet Inc. briefly surpassed Apple Inc. in market capitalization on January 7, 2026, signaling a shift in investor focus from hardware to AI monetization",
    "source": "alpha_vantage",
    "url": "https://example.com/article"
}

print("Initializing Sentiment Analyzer...")
mcp_client = MCPClient()
analyzer = SentimentAnalyzerAgent(mcp_client)

print("\nAnalyzing test article for AAPL...")
print(f"Title: {test_article['title'][:80]}...")
print(f"Summary: {test_article['summary']}")

# Analyze the article
sentiment = analyzer.analyze_article(test_article, "AAPL")

print("\n" + "="*60)
print("FINBERT ANALYSIS RESULTS")
print("="*60)
print(f"Score: {sentiment.score:.3f} (-1=bearish, +1=bullish)")
print(f"Label: {sentiment.label}")
print(f"Confidence: {sentiment.confidence:.2f}")
print(f"\nReasoning:")
print(f"  {sentiment.reasoning}")
print(f"\nThemes: {', '.join(sentiment.themes)}")
print(f"Trading Impact: {sentiment.trading_impact}")
print(f"Analyzed by: {sentiment.analyzed_by}")
print("="*60)
