# Contributing to fastapi-saas-kit

Thank you for your interest in contributing! This guide will help you get started.

## How to Contribute

### Reporting Bugs

- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include steps to reproduce, expected behavior, and actual behavior
- Include your Python version and OS

### Suggesting Features

- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Explain the use case and why it would benefit the community

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Run linting: `ruff check src/ tests/`
6. Commit with a clear message
7. Push and open a Pull Request

## Development Setup

```bash
git clone https://github.com/Devil-nkp/fastapi-saas-kit.git
cd fastapi-saas-kit
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
cp .env.example .env
pytest
```

## Code Style

- Follow PEP 8 conventions
- Use type hints for all function signatures
- Write docstrings for public functions and classes
- Keep functions focused and small
- Use `ruff` for linting

## Testing

- Write tests for all new features
- Maintain or improve test coverage
- Use pytest fixtures from `conftest.py`
- Mock external dependencies

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add Redis cache adapter
fix: correct quota reset timezone handling
docs: update authentication guide
test: add org isolation tests
```

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

Open a [discussion](https://github.com/Devil-nkp/fastapi-saas-kit/discussions) or create an issue.
