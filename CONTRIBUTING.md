# Contributing to Mood Lifter Hooks

Thank you for your interest in contributing to Mood Lifter Hooks! This project aims to bring encouragement and positivity to developers' coding sessions.

## Code of Conduct

- Be respectful and inclusive
- Keep messages positive and uplifting
- Avoid controversial or potentially offensive content
- Focus on encouragement and motivation

## How to Contribute

### Reporting Issues

1. Check if the issue already exists
2. Provide clear description and steps to reproduce
3. Include relevant system information (OS, Python version, ollama version)

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add/update tests if applicable
5. Run code quality checks:
   ```bash
   black hooks/ lib/
   ruff check hooks/ lib/
   pytest  # if tests exist
   ```
6. Commit with clear message: `git commit -m "Add feature: description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request with detailed description

### Development Setup

Using uv (recommended):
```bash
git clone https://github.com/your-fork/mood-lifter-hooks.git
cd mood-lifter-hooks
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Message Guidelines

When adding new messages:
- Keep them under 100 characters
- Include appropriate emojis (but don't overdo it)
- Ensure they're encouraging and positive
- Consider different contexts (morning/evening, different events)
- Test with and without ollama

### Priority Areas for Contribution

1. **Message Variety**: Add more fallback messages
2. **Language Support**: Translate messages to other languages
3. **External APIs**: Integrate joke/quote APIs (see CLAUDE.md)
4. **JW Daily Text**: Implement daily text integration
5. **Testing**: Add comprehensive test suite
6. **Documentation**: Improve setup guides and examples

### Testing Your Changes

Before submitting:
1. Test hooks manually with Claude Code
2. Verify messages display correctly
3. Ensure no context pollution
4. Test with ollama unavailable (fallback mode)
5. Check different event types work as expected

## Questions?

Feel free to open an issue for discussion or clarification.

Thank you for helping make coding sessions more uplifting! 🌟