# Contributing to Legal Debate System

Thank you for your interest in contributing to the Legal Debate System! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. Please be respectful and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Legal-debate-system-with-multi-agent-architecture.git
   cd Legal-debate-system-with-multi-agent-architecture
   ```

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip and virtualenv
- Git
- Google Gemini API key (for testing with real LLM)

### Installation

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest black isort flake8 mypy  # Development tools
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

4. **Verify installation**:
   ```bash
   pytest tests/
   ```

## Making Changes

### Project Structure

```
legal-debate-system/
├── src/
│   ├── app/          # Streamlit UI components
│   ├── core/         # Business logic (orchestrator, messages)
│   └── utils/        # Utilities (LLM client, helpers)
├── tests/            # Test suite
├── app.py            # Main entrypoint (kept for compatibility)
└── pyproject.toml    # Project configuration
```

### Guidelines

- **Keep changes focused**: Each PR should address a single concern
- **Write tests**: Add tests for new features and bug fixes
- **Update documentation**: Update README.md and docstrings as needed
- **Follow the code style**: Use black, isort, and flake8
- **Add type hints**: Use type annotations where appropriate

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_smoke.py

# Run tests in verbose mode
pytest tests/ -v
```

### Test Categories

- **Smoke tests** (`test_smoke.py`): Basic functionality tests
- **Orchestrator tests** (`test_orchestrator.py`): Debate flow tests
- **Integration tests**: Tests requiring external APIs (mark with `@pytest.mark.integration`)

### Deterministic Testing

Use `MockLLM` for tests that don't require real API calls:

```python
from src.utils.llm_client import MockLLM

def test_something():
    mock_llm = MockLLM()
    response = mock_llm.invoke([])
    # Test with predictable response
```

## Code Style

We use several tools to maintain code quality:

### Black (Code Formatting)

```bash
# Format code
black src/ tests/

# Check without modifying
black --check src/ tests/
```

### isort (Import Sorting)

```bash
# Sort imports
isort src/ tests/

# Check only
isort --check-only src/ tests/
```

### Flake8 (Linting)

```bash
# Run linter
flake8 src/ tests/ --max-line-length=100
```

### Mypy (Type Checking)

```bash
# Run type checker
mypy src/ --ignore-missing-imports
```

### Run All Checks

```bash
# Format and check everything
black src/ tests/ && \
isort src/ tests/ && \
flake8 src/ tests/ --max-line-length=100 && \
mypy src/ --ignore-missing-imports && \
pytest tests/
```

## Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Make your changes** and commit:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

3. **Run all checks locally**:
   ```bash
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   pytest tests/
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to any related issues
   - Screenshots for UI changes

6. **Address review feedback** promptly

7. **Wait for CI checks** to pass:
   - Black formatting
   - Flake8 linting
   - Mypy type checking
   - Pytest tests

## Areas for Contribution

We welcome contributions in the following areas:

### Features

- Real case law database integration
- Additional legal domains (civil, constitutional, international)
- Multi-language support
- Export to PDF/Word
- Advanced evaluation metrics
- Real-time collaboration features

### Improvements

- Performance optimizations
- Better error handling
- Enhanced UI/UX
- More comprehensive tests
- Documentation improvements

### Bug Fixes

- Check the issues page for known bugs
- Report new bugs with detailed reproduction steps

## Documentation

When adding new features:

- Update README.md with usage examples
- Add docstrings to all public functions/classes
- Update CONTRIBUTING.md if the dev workflow changes
- Add inline comments for complex logic

## Questions?

If you have questions:

1. Check existing documentation
2. Search closed issues/PRs
3. Open a new issue with the "question" label

## Thank You!

Your contributions make this project better. We appreciate your time and effort! 🎉

---

**Remember**: This is an educational tool. Legal arguments generated by the AI should not be considered actual legal advice.
