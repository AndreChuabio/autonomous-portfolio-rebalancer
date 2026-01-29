# Autonomous Portfolio Rebalancing Agent

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> An intelligent, multi-agent system for autonomous portfolio rebalancing

A proof-of-concept agentic workflow that monitors portfolio drift, evaluates multiple rebalancing scenarios, and makes autonomous trading decisions based on market conditions and risk metrics. Built with a 3-phase architecture (Monitor → Analyze → Decide) that mimics human portfolio management decision-making.

**Status**: Active Development - Portfolio Project

## Key Features

- **Autonomous Decision-Making**: Makes trading decisions, not just recommendations
- **Real-Time Market Integration**: MongoDB portfolio data + live yfinance prices via MCP
- **Multi-Scenario Evaluation**: Compares 4 rebalancing strategies with risk scoring
- **Adaptive Thresholds**: Dynamically adjusts based on market regime and volatility
- **Risk-Aware**: VaR, Sharpe ratio, beta analysis integrated into decision logic
- **Sentiment Analysis**: FinBERT-powered news analysis for context-aware decisions
- **Comprehensive Testing**: Full pytest suite with unit and integration tests

## Architecture

The system implements a three-phase agentic workflow:

### Phase 1: Monitor Agent
- Tracks portfolio drift vs target allocations
- Detects market regime changes (low vol, moderate, high vol, crisis)
- Triggers deeper analysis when thresholds are exceeded
- Autonomous Goal: Maintain situational awareness and decide when action is needed

### Phase 2: Analyzer Agent
- Evaluates multiple rebalancing scenarios:
  - Full Rebalance: Correct all positions
  - Partial Rebalance: Fix only high-drift positions
  - Sector Rebalance: Focus on sector allocation
  - Defer: Wait for better conditions
- Simulates impact on risk metrics (VaR, Sharpe, beta)
- Scores scenarios based on trade-offs
- Autonomous Goal: Find optimal rebalancing strategy

### Phase 3: Decision Agent
- Makes final autonomous decision (not just recommendations)
- Adapts thresholds dynamically based on market volatility
- Determines execution timing (immediate, gradual, defer)
- Prioritizes positions for rebalancing
- Autonomous Goal: Make risk-adjusted decisions that optimize portfolio health

## Project Structure

```
autonomous-portfolio-rebalancer/
├── main.py                     # CLI entry point
├── pytest.ini                  # Test configuration
├── requirements.txt            # Python dependencies
├── .github/
│   └── workflows/             # CI/CD pipelines
├── config/
│   └── settings.py            # Configuration and thresholds
├── docs/                      # Documentation
├── examples/                  # Example outputs
├── src/
│   ├── agents/               # Agent implementations
│   ├── workflows/            # Orchestration logic
│   ├── models/               # Data models
│   └── utils/                # Utilities and calculations
└── tests/                    # Test suite
```

## Quick Start

### Prerequisites

- Python 3.10+
- MongoDB instance with portfolio data
- MCP yfinance server (for live market data)

### Installation

```bash
# Clone the repository
git clone https://github.com/AndreChuabio/finance-agentic-workflow.git
cd finance-agentic-workflow

# Install dependencies
pip install -r requirements.txt

# Run your first autonomous cycle
python main.py --run
```

## Usage

### Run One Rebalancing Cycle

Execute a complete Monitor → Analyzer → Decision workflow:

```bash
python main.py --run
```

Output: Autonomous decision with specific trade recommendations, dollar amounts, and execution timing.

### Export Decision to File

Save decision as JSON for analysis/logging:

```bash
python main.py --run --export decision_2024_12_12.json
```

### View Decision History

Review past autonomous decisions:

```bash
python main.py --history --limit 10
```

## Portfolio Configuration

Portfolio: PORT_A_TechGrowth  
Basis: $1,000,000

### Target Allocation

Technology Sector (55%)
- AAPL: 10%
- MSFT: 10%
- GOOGL: 10%
- NVDA: 8%
- META: 7%
- XLK: 10%

Energy Sector (12%)
- XOM: 4%
- CVX: 4%
- COP: 2%
- XLE: 2%

Benchmarks (33%)
- SPY: 15%
- QQQ: 13%
- IWM: 5%

## Key Thresholds

Configurable in [config/settings.py](config/settings.py):

Drift Thresholds:
- Critical: 3% (triggers immediate analysis)
- High: 2.5%
- Medium: 1.5%

Risk Thresholds:
- VaR Warning: -3%
- VaR Critical: -4%
- Sharpe Warning: 1.0
- Sharpe Critical: 0.0

Operational:
- Max Turnover: 20% per cycle
- Rebalance Cooldown: 3 days
- Beta Threshold: 1.5

## MCP Tools Used

The agent uses the following MCP yfinance tools:

- `query_portfolio_holdings()` - Get portfolio snapshot from MongoDB
- `query_risk_metrics()` - Get latest risk metrics (VaR, Sharpe, beta)
- `get_stock_info(symbol)` - Get current live prices
- `get_portfolio_balance()` - Get paper trading account status
- `place_buy_order()` / `place_sell_order()` - Execute trades (optional)

## Agentic Behavior

### Autonomous Decision-Making

Unlike traditional rule-based systems, this agent:

1. Decides When to Act: Monitor Agent determines if conditions warrant deeper analysis (not just reporting metrics)

2. Evaluates Trade-offs: Analyzer Agent scores scenarios considering:
   - Transaction costs vs drift reduction
   - Market regime appropriateness
   - Risk/return impact

3. Makes Final Decisions: Decision Agent chooses optimal scenario and execution timing based on:
   - Drift severity
   - Market volatility
   - Recent rebalancing history
   - Adaptive thresholds

4. Learns from History: Tracks decision outcomes and adapts thresholds for future cycles

### Adaptive Thresholds

The system dynamically adjusts rebalancing thresholds:

- Increases thresholds after rebalancing (prevents thrashing)
- Lowers thresholds in stable market conditions
- Raises thresholds during high volatility
- Overrides normal rules in crisis detection

## Example Output

Sample workflow execution showing the 3-phase decision process:

```
[PHASE 1: MONITOR] → Detected 4.2% drift (AAPL overweight)
[PHASE 2: ANALYZER] → Evaluated 4 scenarios, recommended partial rebalance
[PHASE 3: DECISION] → Execute 4 trades, $16.7K turnover (1.67%)
```

See [examples/EXAMPLE_OUTPUT.md](examples/EXAMPLE_OUTPUT.md) for detailed workflow output with full decision reasoning, trade plans, and risk analysis.

## Tech Stack

- **Languages**: Python 3.10+
- **Data**: MongoDB (portfolio history), yfinance (live prices via MCP)
- **ML/AI**: FinBERT (sentiment analysis), spaCy (NLP)
- **Architecture**: Multi-agent system with autonomous decision-making
- **Testing**: pytest, pytest-cov, pytest-mock
- **Containerization**: Docker, Docker Compose
- **Risk Analysis**: NumPy, Pandas for quantitative calculations

## Development Roadmap

- [ ] Continuous monitoring mode with scheduled cycles
- [ ] Live trade execution integration
- [ ] Machine learning for regret score calculation
- [ ] Multi-portfolio support
- [ ] Real-time alert notifications (Slack/email)
- [ ] Performance attribution analysis
- [ ] Tax-loss harvesting integration
- [ ] Backtesting framework with historical data

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v
```

## Documentation

- [Sentiment Analysis](docs/SENTIMENT.md) - AI-powered news analysis
- [Architecture Details](docs/SENTIMENT_ARCHITECTURE.md) - System design
- [Technical Specification](docs/SENTIMENT_TECHNICAL_SPEC.md) - FinBERT methodology
- [Implementation Notes](docs/IMPLEMENTATION.md) - Development history
- [Docker Setup](DOCKER.md) - Containerization guide

## Contributing

This is a portfolio project demonstrating autonomous agent architecture for quantitative finance applications. Feedback and suggestions welcome.

## License

MIT License - See LICENSE file for details

## Contact

Andre Chuabio  
Email: andre102599@gmail.com  
GitHub: https://github.com/AndreChuabio  
LinkedIn: https://linkedin.com/in/andrechuabio

---

Built as a demonstration of autonomous agent architecture, real-time financial data integration, and risk-aware decision-making systems.

