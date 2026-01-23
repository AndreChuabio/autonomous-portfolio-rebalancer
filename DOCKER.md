# Docker Setup

This project includes Docker Compose configuration for running the autonomous portfolio rebalancer with MongoDB and Neo4j.

## Architecture

```
+-------------------+     +-------------------+     +-------------------+
|   Portfolio       |     |     MongoDB       |     |      Neo4j        |
|   Rebalancer      |---->|  (Holdings,       |     |  (Articles,       |
|   (Python App)    |     |   Risk Metrics)   |     |   Sentiment)      |
+-------------------+     +-------------------+     +-------------------+
        |                                                    ^
        |                                                    |
        +----------------------------------------------------+
                    Sentiment Analysis Data
```

## Prerequisites

- Docker Desktop installed and running (requires ~4GB RAM for ML models)
- At least 10GB disk space (PyTorch + transformers models)

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/AndreChuabio/autonomous-portfolio-rebalancer.git
cd autonomous-portfolio-rebalancer
```

2. Copy environment template:

```bash
cp .env.example .env
```

3. Start all services:

```bash
docker compose up
```

4. The first run will:
   - Download MongoDB and Neo4j images
   - Build the Python app (downloads PyTorch, transformers, spaCy models)
   - This may take 10-15 minutes on first run

## Services

| Service | Port | Description |
|---------|------|-------------|
| MongoDB | 27017 | Portfolio holdings and risk metrics |
| Neo4j | 7474 (HTTP), 7687 (Bolt) | Articles and sentiment data |
| App | - | Portfolio rebalancer (interactive CLI) |

## Accessing Neo4j Browser

Open http://localhost:7474 in your browser.
- Username: `neo4j`
- Password: `password123`

## Running the Rebalancer

The app container runs in interactive mode. To execute the workflow:

```bash
# Attach to running container
docker compose exec app python main.py

# Or run batch analysis
docker compose exec app python batch_analyze_portfolio.py
```

## Data Persistence

Docker volumes persist data between restarts:
- `mongo_data` - MongoDB documents
- `neo4j_data` - Neo4j graph database
- `neo4j_logs` - Neo4j logs

To reset all data:

```bash
docker compose down -v
```

## Development

Rebuild after code changes:

```bash
docker compose up --build
```

View logs:

```bash
docker compose logs -f app
```

## Resource Requirements

The FinBERT sentiment model requires significant resources:
- RAM: ~4GB minimum (8GB recommended)
- Disk: ~5GB for PyTorch + transformers
- CPU: Multi-core recommended for inference

For production, consider:
- Using GPU-enabled Docker images
- Pre-downloading models to a shared volume
- Running sentiment analysis as a separate service

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| MONGODB_URI | mongodb://root:example@mongodb:27017 | MongoDB connection |
| NEO4J_URI | bolt://neo4j:7687 | Neo4j Bolt connection |
| NEO4J_USERNAME | neo4j | Neo4j username |
| NEO4J_PASSWORD | password123 | Neo4j password |

## Integration with MCP Server

This rebalancer is designed to work with the [mcp-yfinance-server](https://github.com/AndreChuabio/mcp-yfinance-server) for live market data and paper trading. When using with Cursor or Claude Desktop:

1. Configure the MCP server to connect to the same MongoDB/Neo4j instances
2. Use the MCP tools for real-time portfolio data
3. The sentiment agents will enrich Neo4j with FinBERT analysis
