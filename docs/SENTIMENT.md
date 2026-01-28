# Sentiment Analysis System

The sentiment analysis system enriches portfolio decisions with AI-powered news analysis using FinBERT.

## Quick Start

### Analyze All Portfolio Tickers (30 days)
```bash
python main.py --analyze-sentiment
```

### Analyze Specific Tickers
```bash
python main.py --analyze-sentiment --tickers AAPL NVDA --days 7
```

### Force Re-analysis
```bash
python main.py --analyze-sentiment --force
```

## Architecture Overview

The system uses a two-agent architecture:

1. **SentimentAnalyzerAgent** - Enriches articles with AI sentiment scores
2. **SentimentExplainerAgent** - Uses sentiment to explain rebalancing decisions

### Why Two Agents?

- **Performance**: Rebalancing doesn't wait for article analysis
- **Caching**: Sentiment scores cached in Neo4j
- **Flexibility**: Can run analyzer independently

## Technical Approach

### FinBERT Model
- Pre-trained financial BERT from ProsusAI
- Fine-tuned on 4,900+ financial news articles
- 3-class classification: positive, negative, neutral

### Hybrid Scoring
```
Final Score = (70% FinBERT) + (30% Keyword Analysis)
```

### Theme Extraction
- Uses spaCy NLP for named entity recognition
- Identifies key themes: earnings, AI, regulation, expansion, etc.

## Implementation Status

**Complete:**
- Agent architecture and workflow
- FinBERT integration and hybrid scoring
- CLI interface
- Theme extraction and reasoning generation

**In Progress:**
- MCP write operations to Neo4j
- Full integration with live article data

## Performance

- Analysis time: 2-5 seconds per article
- Full portfolio: 2-10 minutes (13 tickers)
- Caching: Only analyzes new articles after initial run

## Documentation

- [Technical Specification](SENTIMENT_TECHNICAL_SPEC.md) - Detailed methodology
- [Architecture Documentation](SENTIMENT_ARCHITECTURE.md) - System design
- [Implementation Notes](IMPLEMENTATION.md) - Development history

## Next Steps

1. Complete MCP write operation for Neo4j
2. Add Neo4j schema for copilot sentiment
3. Schedule daily sentiment enrichment runs
