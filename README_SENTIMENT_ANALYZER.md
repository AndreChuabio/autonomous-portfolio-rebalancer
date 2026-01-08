# SentimentAnalyzerAgent - Quick Start

## What is this?

The **SentimentAnalyzerAgent** enriches your Neo4j database with AI-generated sentiment scores. It's separate from the **SentimentExplainerAgent** that runs during rebalancing.

## Two-Agent Architecture

```
SentimentAnalyzerAgent      SentimentExplainerAgent
(Data Enrichment)           (Decision Support)
        │                           │
        │ Writes sentiment          │ Reads sentiment
        ▼                           ▼
    Neo4j Database          Rebalancing Workflow
```

## Usage

### Run Analysis (Default: All Portfolio Tickers, 30 Days)
```bash
python main.py --analyze-sentiment
```

### Analyze Specific Tickers
```bash
python main.py --analyze-sentiment --tickers AAPL NVDA XOM
```

### Custom Lookback Period
```bash
python main.py --analyze-sentiment --days 7
```

### Force Re-analysis (Ignore Existing Sentiment)
```bash
python main.py --analyze-sentiment --force
```

## Current Status

**Implementation Status: 🚧 Partial**

✅ **Complete:**
- CLI interface (`--analyze-sentiment`)
- Agent structure and workflow
- Error handling and reporting
- Integration with portfolio system

⏳ **Pending:**
- MCP write operation: `write_article_sentiment`
- Neo4j schema enhancement for Copilot sentiment
- Actual article analysis (currently placeholder)

## What Happens When You Run It?

**Current Behavior (Placeholder):**
1. Queries portfolio tickers
2. Simulates analysis workflow
3. Shows what WOULD be analyzed
4. Returns summary with 0 analyzed (no write operation yet)

**Future Behavior (After MCP Implementation):**
1. Queries Neo4j for articles without Copilot sentiment
2. For each article:
   - Analyzes title/summary using AI
   - Generates sentiment score, themes, reasoning
   - Writes back to Neo4j
3. Returns summary with actual analysis count

## Next Steps for Full Implementation

### 1. MCP Server Enhancement (yfinance server)

Add write operation to [mcp_mcp-yfinance-] server:

```python
def write_article_sentiment(
    url: str,
    symbol: str,
    score: float,
    label: str,
    confidence: float,
    reasoning: str,
    themes: List[str],
    trading_impact: str,
    analyzed_by: str = "copilot"
) -> bool:
    """Write sentiment analysis back to Neo4j."""
    # Cypher query to create/update sentiment relationship
    pass
```

### 2. Neo4j Schema Enhancement

```cypher
# Add new relationship type for Copilot sentiment
MATCH (a:Article {url: $url})-[:MENTIONS]->(s:Stock {symbol: $symbol})
CREATE (a)-[:SENTIMENT_COPILOT {
  score: $score,
  label: $label,
  confidence: $confidence,
  reasoning: $reasoning,
  themes: $themes,
  trading_impact: $trading_impact,
  analyzed_by: $analyzed_by,
  analyzed_at: datetime()
}]->(s)
```

### 3. Update SentimentAnalyzerAgent

Uncomment actual MCP calls in `analyze_ticker()` method:

```python
# Replace placeholder with:
articles = self.mcp_client.get_recent_articles(ticker, days)
for article in articles:
    if not force_reanalyze and article.has_copilot_sentiment:
        skipped += 1
        continue
    
    sentiment = self.analyze_article(article, ticker)
    self.mcp_client.write_article_sentiment(
        url=article.url,
        symbol=ticker,
        **sentiment.__dict__
    )
    analyzed += 1
```

## Deployment Recommendations

### Option A: Scheduled Runs (Recommended)
```bash
# Add to cron (daily at 6am)
0 6 * * * cd /path/to/project && python main.py --analyze-sentiment
```

### Option B: On-Demand (Development)
```bash
# Run manually when needed
python main.py --analyze-sentiment --tickers AAPL NVDA --days 7
```

### Option C: Pre-Workflow
```bash
# Run before rebalancing to ensure fresh sentiment
python main.py --analyze-sentiment && python main.py --run
```

## Performance Expectations

- **Articles per ticker**: 10-50 (varies by coverage)
- **Analysis time**: ~2-5 seconds per article
- **Total runtime**: 2-10 minutes for full portfolio (13 tickers)
- **Caching**: Only analyzes new articles (after initial run)

## Files Created

- [src/agents/sentiment_analyzer_agent.py](src/agents/sentiment_analyzer_agent.py) - Main agent implementation
- [SENTIMENT_ARCHITECTURE.md](SENTIMENT_ARCHITECTURE.md) - Detailed architecture documentation
- [README_SENTIMENT_ANALYZER.md](README_SENTIMENT_ANALYZER.md) - This file

## Questions?

See [SENTIMENT_ARCHITECTURE.md](SENTIMENT_ARCHITECTURE.md) for complete technical details.
