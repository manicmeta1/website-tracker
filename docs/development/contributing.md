# Contributing to Website Tracker

Thank you for your interest in contributing to Website Tracker! This guide will help you get started with contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/website-tracker.git
cd website-tracker
```

3. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

4. Install development dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

Run the test suite using pytest:
```bash
python -m pytest
```

For coverage report:
```bash
python -m pytest --cov=./ --cov-report=xml
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write docstrings for functions and classes
- Include tests for new features

## Pull Request Process

1. Update documentation for any new features
2. Add or update tests as needed
3. Ensure all tests pass
4. Update CHANGELOG.md with your changes
5. Submit a pull request to the `main` branch

## Commit Messages

Follow conventional commits format:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- test: Adding or updating tests
- refactor: Code refactoring
- chore: Maintenance tasks

## Need Help?

- Check existing issues and pull requests
- Create a new issue for discussion
- Join our community discussions