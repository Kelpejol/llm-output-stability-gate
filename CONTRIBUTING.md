# Contributing to LLM Output Stability Gate

Thanks for your interest in contributing! This document provides guidelines for contributions.

## How to Contribute

### Reporting Bugs

- Check if the bug already exists in [Issues](https://github.com/kelpejol/llm-output-stability-gate/issues)
- Use the bug report template
- Include reproduction steps, expected vs actual behavior
- Add relevant logs and environment info

### Suggesting Features

- Check existing [Issues](https://github.com/kelpejol/llm-output-stability-gate/issues) and [Discussions](https://github.com/kelpejol/llm-output-stability-gate/discussions)
- Describe the problem you're solving
- Explain your proposed solution
- Consider backward compatibility

### Pull Requests

1. **Fork the repository**

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clear, documented code
   - Add tests for new features
   - Update documentation if needed

4. **Test your changes**
   ```bash
   pytest -v
   black gate/ tests/
   ruff check gate/ tests/
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new evaluation metric"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/llm-output-stability-gate.git
cd llm-output-stability-gate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .

# Set up OpenAI API key (for tests that require it)
export OPENAI_API_KEY=your_key_here

# Run tests
pytest
```

## Code Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for functions
- Format with Black: `black gate/ tests/`
- Lint with Ruff: `ruff check gate/ tests/`

## Commit Messages

Use conventional commit format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Example: `feat(evaluator): add support for custom UQLM scorers`

## Testing Guidelines

### Running Tests

```bash
# Run all tests (skips tests requiring API key)
pytest

# Run specific test file
pytest tests/test_policy.py

# Run with coverage
pytest --cov=gate

# Run tests that require API key (if you have one)
pytest -m requires_api_key
```

### Writing Tests

- Write tests for all new features
- Mock external API calls when possible
- Use `@pytest.mark.requires_api_key` for tests needing OpenAI
- Aim for >80% code coverage

### Test Structure

```python
class TestNewFeature:
    """Tests for new feature."""
    
    def test_success_case(self):
        """Test successful execution."""
        result = my_function("input")
        assert result == "expected"
    
    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            my_function("invalid")
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation if endpoints change
- Include examples in docstrings

## Security

- Never commit API keys or secrets
- Use `.env` for local development
- Report security issues privately via email
- Follow security best practices

## Questions?

- Open a [Discussion](https://github.com/kelpejol/llm-output-stability-gate/discussions)
- Check existing [Issues](https://github.com/kelpejol/llm-output-stability-gate/issues)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards others

Thank you for contributing! 🎉
