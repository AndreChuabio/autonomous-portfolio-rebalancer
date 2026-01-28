# Contributing to Autonomous Portfolio Rebalancer

Thank you for your interest in contributing to this project. This is a portfolio project demonstrating autonomous agent architecture for quantitative finance applications.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- MongoDB instance (for portfolio data)
- MCP yfinance server (for market data)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AndreChuabio/autonomous-portfolio-rebalancer.git
cd autonomous-portfolio-rebalancer
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download spaCy model (for sentiment analysis):
```bash
python -m spacy download en_core_web_sm
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v

# Run with verbose output
pytest -vv
```

## Code Style

This project follows PEP8 style guidelines with the following tools:

- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting

Format your code before committing:

```bash
black src tests
isort src tests
flake8 src tests
```

## Project Structure

```
autonomous-portfolio-rebalancer/
├── src/
│   ├── agents/          # Agent implementations
│   ├── models/          # Data models
│   ├── utils/           # Utility functions
│   └── workflows/       # Orchestration logic
├── tests/               # Test suite
├── config/              # Configuration files
└── docs/                # Documentation
```

## Making Changes

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and add tests

3. Run the test suite:
```bash
pytest
```

4. Format your code:
```bash
black src tests
isort src tests
```

5. Commit your changes:
```bash
git add .
git commit -m "Add: descriptive commit message"
```

6. Push to your fork and create a Pull Request

## Commit Message Guidelines

Use clear, descriptive commit messages:

- `Add: new feature or functionality`
- `Fix: bug fix`
- `Update: improvements to existing features`
- `Refactor: code restructuring`
- `Docs: documentation changes`
- `Test: adding or updating tests`

## Pull Request Process

1. Update documentation for any new features
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## Testing Guidelines

- Write unit tests for all new functions
- Add integration tests for workflows
- Aim for 70%+ code coverage
- Use fixtures in conftest.py for common test data
- Mock external dependencies (MCP calls, API requests)

## Questions or Issues?

- Open an issue on GitHub
- Email: andre102599@gmail.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
