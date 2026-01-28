# Example Workflow Output

This document shows example outputs from running the autonomous rebalancing workflow.

## Full Workflow Execution

```bash
$ python main.py --run
```

### Output

```
===============================================================
AUTONOMOUS REBALANCING AGENT: PORT_A_TechGrowth
Cycle: 2026-01-28 14:30:00 | Portfolio Basis: $1,000,000
===============================================================

[PHASE 1: MONITOR AGENT] 
Status: TRIGGERED
Trigger Reason: Max drift 4.2% exceeds 3% threshold

Portfolio Snapshot:
- Total Value: $1,042,300
- Positions: 13
- Max Position Drift: 4.2% (AAPL)
- Max Sector Drift: 3.1% (TECHNOLOGY)
- VaR_95: -1.8%
- Sharpe Ratio: 2.1
- Beta: 1.23
- Market Regime: MODERATE

Top Drifts:
1. AAPL: +4.2% (target: 10.0%, current: 14.2%)
2. NVDA: -3.1% (target: 8.0%, current: 4.9%)
3. META: +2.8% (target: 7.0%, current: 9.8%)

Monitor Decision: → TRIGGER ANALYZER AGENT

---

[PHASE 2: ANALYZER AGENT]
Evaluating rebalancing scenarios...

Scenario 1: FULL_REBALANCE
- Trades: 9
- Turnover: $52,400 (5.2%)
- Max Drift After: 0.0%
- Score: 6.8/10
- Reasoning: Comprehensive correction but high transaction costs

Scenario 2: PARTIAL_REBALANCE
- Trades: 4
- Turnover: $21,300 (2.1%)
- Max Drift After: 1.2%
- Score: 8.7/10
- Reasoning: Optimal balance of drift correction and cost efficiency

Scenario 3: SECTOR_REBALANCE
- Trades: 5
- Turnover: $28,100 (2.8%)
- Max Drift After: 2.1%
- Score: 7.2/10
- Reasoning: Focus on sector allocation, some position drift remains

Scenario 4: DEFER
- Trades: 0
- Turnover: $0 (0.0%)
- Max Drift After: 4.2%
- Score: 3.5/10
- Reasoning: High drift warrants action, deferring not optimal

Recommendation: PARTIAL_REBALANCE (Confidence: 87%)

---

[PHASE 3: DECISION AGENT]
Autonomous Decision: EXECUTE SCENARIO 2 - PARTIAL REBALANCE

Reasoning:
- Max drift (4.2%) exceeds critical threshold (3.0%)
- Market regime is MODERATE (favorable for rebalancing)
- Partial rebalance offers best risk/reward trade-off
- Recent market volatility: 0.15 (within normal range)
- VaR acceptable: -1.8% (within -3.0% limit)

Execution Plan:

Priority  | Ticker | Action | Shares |      Value | Rationale
---------------------------------------------------------------
CRITICAL  | AAPL   | SELL   |     25 |   -$6,430  | 4.2% overweight
HIGH      | NVDA   | BUY    |     35 |   +$6,475  | 3.1% underweight
HIGH      | META   | SELL   |      5 |   -$3,210  | 2.8% overweight
MEDIUM    | QQQ    | BUY    |      8 |   +$3,520  | Sector rebalance

Execution Timing: IMMEDIATE
- Market conditions favorable
- VaR within acceptable range
- No recent rebalancing (last: 12 days ago)

Total: 4 trades, $21,300 turnover (2.1% of portfolio)

Adaptive Adjustments:
- Threshold increased to 3.5% for next 5 days
- Will monitor NVDA closely (high beta: 1.8)
- Next rebalancing cooldown: 3 days minimum

Risk Assessment After Rebalancing:
- Expected VaR: -1.7% (improved from -1.8%)
- Expected Sharpe: 2.2 (improved from 2.1)
- Expected Max Drift: 1.2% (improved from 4.2%)

===============================================================
AGENT STATUS: DECISION FINALIZED - READY FOR EXECUTION
===============================================================

Next Steps:
1. Review execution plan above
2. Execute trades manually or via paper trading MCP
3. Monitor execution and log outcomes
```

## Sentiment Analysis Example

```bash
$ python main.py --analyze-sentiment --tickers AAPL NVDA --days 7
```

### Output

```
============================================================
SENTIMENT ANALYZER AGENT
Analyzing articles for 2 tickers...
Lookback period: 7 days
Force re-analyze: False

============================================================

Loading FinBERT model (first time only)...
Loading spaCy NLP model...

📊 Analyzing AAPL...
   Found 12 articles
   ✓ Analyzed 8 new articles
   ⏭️ Skipped 4 (already analyzed)

📊 Analyzing NVDA...
   Found 18 articles
   ✓ Analyzed 15 new articles
   ⏭️ Skipped 3 (already analyzed)

============================================================
SENTIMENT ANALYSIS SUMMARY
============================================================
Total analyzed: 23
Total skipped (already analyzed): 7
Errors: 0

Per-ticker breakdown:
  AAPL: ✓ 8 analyzed, 4 skipped
  NVDA: ✓ 15 analyzed, 3 skipped
============================================================
```

## Test Suite Example

```bash
$ pytest --cov=src --cov-report=term
```

### Output

```
========================= test session starts ==========================
platform darwin -- Python 3.10.11, pytest-7.4.0, pluggy-1.3.0
rootdir: /Users/andrechuabio/cursor_hacking/autonomous-portfolio-rebalancer
plugins: cov-4.1.0, mock-3.11.1
collected 42 items

tests/test_models.py ............                                 [ 28%]
tests/test_calculations.py ..........                             [ 52%]
tests/test_agents.py .............                                [ 83%]
tests/test_workflow.py .......                                    [100%]

---------- coverage: platform darwin, python 3.10.11 -----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/__init__.py                             0      0   100%
src/agents/__init__.py                      0      0   100%
src/agents/analyzer_agent.py              145     18    88%   67-72, 201-205
src/agents/decision_agent.py              178     22    88%   89-94, 223-228
src/agents/monitor_agent.py               132     15    89%   101-106
src/agents/sentiment_analyzer_agent.py    312     45    86%   Various
src/agents/sentiment_explainer_agent.py    89     12    87%   Various
src/models/__init__.py                      0      0   100%
src/models/decision.py                     98      4    96%   45-48
src/models/portfolio.py                    76      2    97%   67-68
src/utils/__init__.py                       0      0   100%
src/utils/calculations.py                  87      8    91%   123-130
src/utils/mcp_client.py                    54     12    78%   Various
src/workflows/__init__.py                   0      0   100%
src/workflows/rebalance_workflow.py       167     28    83%   Various
---------------------------------------------------------------------
TOTAL                                    1338    166    88%

========================= 42 passed in 3.42s ===========================
```

## CLI Help

```bash
$ python main.py --help
```

### Output

```
usage: main.py [-h] [--run] [--monitor] [--history] [--export FILEPATH]
               [--analyze-sentiment] [--tickers TICKERS [TICKERS ...]]
               [--days DAYS] [--force] [--limit LIMIT]

Autonomous Rebalancing Agent for PORT_A_TechGrowth

options:
  -h, --help            show this help message and exit
  --run                 Execute one complete rebalancing workflow cycle
  --monitor             Continuous monitoring mode (not yet implemented)
  --history             Show recent decision history
  --export FILEPATH     Export last decision to JSON file
  --analyze-sentiment   Run sentiment analysis on portfolio tickers (enriches Neo4j)
  --tickers TICKERS [TICKERS ...]
                        Specific tickers to analyze (default: all portfolio tickers)
  --days DAYS           Lookback period for sentiment analysis (default: 30 days)
  --force               Force re-analysis of articles with existing sentiment
  --limit LIMIT         Number of decisions to show in history (default: 10)

Examples:
  python main.py --run              Execute one rebalancing workflow cycle
  python main.py --history          Show recent decision history
  python main.py --export decision.json  Export last decision to file
  python main.py --analyze-sentiment     Analyze sentiment for all portfolio tickers
  python main.py --analyze-sentiment --tickers AAPL NVDA --days 7  Analyze specific tickers
```
