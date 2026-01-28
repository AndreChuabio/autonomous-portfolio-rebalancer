# Sentiment Analysis Architecture

## Overview

The sentiment system uses a **two-agent architecture** to separate data enrichment from decision support:

1. **SentimentAnalyzerAgent** - Enriches raw articles with AI-generated sentiment scores
2. **SentimentExplainerAgent** - Interprets sentiment data to explain rebalancing decisions

## Why Two Agents?

| Aspect | SentimentAnalyzerAgent | SentimentExplainerAgent |
|--------|----------------------|------------------------|
| **Purpose** | Data enrichment | Decision support |
| **When runs** | Scheduled/on-demand | During rebalancing workflow |
| **Input** | Raw article text | Enriched sentiment scores |
| **Output** | Sentiment scores → Neo4j | Natural language explanations |
| **Frequency** | Periodic (daily/weekly) | Every rebalancing cycle |

### Benefits of Separation

- **Performance**: Rebalancing workflow doesn't wait for article analysis
- **Caching**: Sentiment scores cached in Neo4j, analyzed once
- **Flexibility**: Can run analyzer independently to improve coverage
- **Knowledge accumulation**: Database gets smarter over time

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SENTIMENT PIPELINE                        │
└─────────────────────────────────────────────────────────────┘

Phase 1: Data Ingestion (External)
──────────────────────────────────
RSS Feeds, Alpha Vantage → Neo4j
Articles stored with: title, summary, url, date, source


Phase 2: Enrichment (SentimentAnalyzerAgent)
──────────────────────────────────────────────
python main.py --analyze-sentiment

┌──────────────┐
│ Read Articles│  ← Query Neo4j for articles without sentiment
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ AI Analysis  │  ← Copilot analyzes: score, themes, reasoning
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Write Scores │  → Store sentiment back to Neo4j
└──────────────┘


Phase 3: Decision Support (SentimentExplainerAgent)
────────────────────────────────────────────────────
python main.py --run

┌──────────────┐
│ Read Scores  │  ← Query enriched sentiment from Neo4j
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Explain      │  ← Generate natural language context
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Report       │  → Show sentiment context for positions
└──────────────┘
```

## Data Flow

### Neo4j Schema

```cypher
# Current (Gemini API)
(:Article {url, title, summary, date})
  -[:SENTIMENT {score, label, date}]-> (:Stock)

# Proposed (Feedback Loop)
(:Article {url, title, summary, date})
  -[:SENTIMENT_GEMINI {score, label, date}]-> (:Stock)
  -[:SENTIMENT_COPILOT {
      score,
      label,
      confidence,
      reasoning,
      themes,
      trading_impact,
      analyzed_by,
      analyzed_at
   }]-> (:Stock)
```

### MCP Operations

**Current (Read-only):**
- `get_stock_sentiment(symbol)` - Aggregate sentiment stats
- `get_recent_articles(symbol, limit, sentiment_filter)` - Articles with Gemini scores
- `get_sentiment_timeline(symbol, days)` - Historical sentiment trend
- `search_articles_by_keyword(keyword)` - Find relevant articles

**Needed (Write operations):**
- `write_article_sentiment(url, symbol, score, label, reasoning, themes, analyzed_by)`
- `has_copilot_sentiment(url)` - Check if already analyzed
- `compare_sentiment_sources(symbol)` - Gemini vs Copilot comparison

## Implementation Status

### ✅ Complete
- [x] SentimentExplainerAgent (src/agents/sentiment_explainer_agent.py)
- [x] Integration with rebalance workflow
- [x] CLI for running explanations (--run)
- [x] Tested with AAPL (48 articles) and NVDA (41 articles)

### 🚧 In Progress
- [x] SentimentAnalyzerAgent (src/agents/sentiment_analyzer_agent.py)
- [x] CLI for running analysis (--analyze-sentiment)
- [ ] MCP write operations in yfinance server
- [ ] Neo4j schema enhancement for dual sentiment sources

### 📋 TODO
- [ ] Implement MCP `write_article_sentiment` tool
- [ ] Add caching logic (skip already-analyzed articles)
- [ ] Ingest sentiment for energy stocks (XOM, CVX, COP, XLE - currently 0 articles)
- [ ] Improve coverage for MSFT, META, GOOGL
- [ ] Ensemble approach (compare Gemini vs Copilot scores)
- [ ] Historical sentiment backtesting

## Usage

### Enriching Database (Data Enrichment)

```bash
# Analyze all portfolio tickers (default 30 days lookback)
python main.py --analyze-sentiment

# Analyze specific tickers with custom lookback
python main.py --analyze-sentiment --tickers AAPL NVDA XOM --days 7

# Force re-analysis of existing sentiment
python main.py --analyze-sentiment --force
```

### Using Sentiment (Decision Support)

```bash
# Run rebalancing workflow (automatically uses sentiment)
python main.py --run

# Sentiment context shown after decision phase
# Example output:
# ─────────────────────────────────────────────
# SENTIMENT CONTEXT
# ─────────────────────────────────────────────
# AAPL: Neutral (0.00) - 48 articles analyzed
#   Recent headlines suggest competition concerns...
```

## Performance Considerations

### Analyzer Agent
- **Runtime**: ~2-5 seconds per article (AI analysis)
- **Frequency**: Run daily or weekly to keep fresh
- **Caching**: Only analyzes new/unscored articles
- **Parallel**: Can analyze multiple tickers in parallel

### Explainer Agent  
- **Runtime**: ~1-2 seconds (reads cached scores)
- **Frequency**: Every rebalancing cycle
- **Caching**: Reads pre-computed sentiment from Neo4j
- **Parallel**: Queries multiple tickers efficiently

## Architecture Evolution

### Phase 1: Read-Only (Current)
- Gemini API pre-computes sentiment
- Agents read from Neo4j
- No feedback loop

### Phase 2: Feedback Loop (In Progress)
- Add SentimentAnalyzerAgent
- Write Copilot sentiment to Neo4j
- Compare Gemini vs Copilot scores

### Phase 3: Full Automation (Future)
- Scheduled analyzer runs (cron/Airflow)
- Real-time article ingestion
- Sentiment drift alerts
- Multi-LLM ensemble (Gemini + Copilot + Claude)

## Error Handling

### Analyzer Agent
- Gracefully skip articles without text
- Continue on single-article failures
- Log errors with article URL and ticker
- Return partial results if some tickers fail

### Explainer Agent
- Fallback to "no sentiment data" message
- Continue workflow even without sentiment
- Show coverage gaps (e.g., "0 articles for XOM")

## Next Steps

1. **Implement MCP Write Operations** (yfinance server)
   - Add `write_article_sentiment` tool
   - Update Neo4j schema for dual sentiment sources
   - Add caching checks

2. **Enhance Data Coverage** (article ingestion)
   - Add RSS feeds for energy stocks
   - Improve MSFT, META, GOOGL coverage
   - Consider benchmark ETF sentiment

3. **Production Deployment**
   - Schedule analyzer runs (daily 6am)
   - Monitor sentiment coverage metrics
   - Alert on large sentiment shifts

4. **Advanced Features**
   - Sentiment disagreement analysis (Gemini vs Copilot)
   - Theme extraction and trending
   - Trading signal generation from sentiment
   - Backtest sentiment-based strategies
