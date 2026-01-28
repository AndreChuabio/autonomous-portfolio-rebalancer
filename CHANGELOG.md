# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive pytest test suite with unit and integration tests
- GitHub Actions CI/CD pipeline for automated testing
- Code quality checks (black, isort, flake8)
- Test coverage reporting with pytest-cov
- CONTRIBUTING.md with development guidelines
- Docker build automation workflow
- Consolidated documentation structure in docs/ folder

### Changed
- Reorganized documentation files into docs/ directory
- Updated README with CI badges and realistic project status
- Enhanced requirements.txt with testing dependencies

### Removed
- Redundant documentation files (README_SENTIMENT_ANALYZER.md)
- Internal notes file (remaining_orders.md)

## [0.2.0] - 2026-01-23

### Added
- FinBERT-based sentiment analysis system
- SentimentAnalyzerAgent for data enrichment
- SentimentExplainerAgent for decision support
- Hybrid scoring (FinBERT + keyword analysis)
- Theme extraction using spaCy NLP
- Docker Compose setup with MongoDB and Neo4j
- Sentiment analysis CLI commands
- Comprehensive sentiment documentation

### Changed
- Enhanced decision agent with sentiment context
- Updated workflow to include sentiment analysis
- Improved main.py CLI with sentiment options

## [0.1.0] - 2023-12-12

### Added
- Initial implementation of 3-phase agentic workflow
- MonitorAgent for portfolio drift detection
- AnalyzerAgent for scenario evaluation
- DecisionAgent for autonomous decision-making
- RebalanceWorkflow orchestration
- Portfolio and decision data models
- Risk metrics calculations (VaR, Sharpe, Beta)
- Adaptive threshold management
- Market regime classification
- CLI interface with argparse
- Configuration system in config/settings.py
- MCP client for yfinance integration
- Decision history tracking
- JSON export functionality
- Comprehensive README and documentation
- MIT License
- .gitignore for Python projects

### Technical Details
- Python 3.10+ support
- MongoDB integration for portfolio data
- yfinance for live market data
- NumPy/Pandas for quantitative analysis
- Multi-scenario evaluation system
- Risk-aware decision logic

[Unreleased]: https://github.com/AndreChuabio/autonomous-portfolio-rebalancer/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/AndreChuabio/autonomous-portfolio-rebalancer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/AndreChuabio/autonomous-portfolio-rebalancer/releases/tag/v0.1.0
