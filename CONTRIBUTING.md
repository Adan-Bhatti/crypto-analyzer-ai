# Contributing to Crypto Analyzer AI

Thank you for your interest in contributing! 🚀

## Getting Started

1. **Fork** this repository and clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/crypto-analyzer-ai.git
   cd crypto-analyzer-ai
   ```

2. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up your environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install flake8
   cp .env.example .env
   ```

## Development Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) (max line length: 120)
- Add docstrings to new functions and classes
- For ML changes, include performance metrics (accuracy, F1) in your PR description
- Test with at least one cryptocurrency (e.g., BTC-USD) before submitting

## Submitting a Pull Request

1. Push your branch and open a PR against `main`
2. Fill in the PR template completely
3. Ensure the CI workflow passes

## Reporting Issues

Please use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) template.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md).
