# Contributing Guide

## Code Style

- Follow PEP 8 conventions
- Use type hints for all function parameters and returns
- Document public methods and classes with docstrings
- Format code with Black
- Check types with mypy

## Development Workflow

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Run full test suite and checks
5. Submit pull request

## Testing

- Write tests for new features
- Maintain >80% code coverage
- Use pytest for testing
- Run tests before committing

## Git Commits

- Use clear, descriptive commit messages
- Reference issues when applicable
- Keep commits focused on single changes

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Include usage examples for new features
- Update API.md for endpoint changes

## Adding New Tools

1. Create file in `src/tools/`
2. Implement tool function
3. Add to `src/tools/__init__.py`
4. Write tests
5. Update documentation

## Adding New Integrations

1. Create module in `src/integrations/`
2. Implement integration class
3. Add API endpoints if needed
4. Add to `src/api/`
5. Include setup documentation

## Questions or Issues?

Create an issue in the repository with detailed information about your question or problem.
