# Contributing to Xantus

Thank you for your interest in contributing to Xantus! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

- Use the GitHub Issues tracker
- Describe the bug in detail
- Include steps to reproduce
- Mention your environment (OS, Python version, etc.)

### Suggesting Features

- Use GitHub Issues with the "enhancement" label
- Clearly describe the feature and its use case
- Explain why this feature would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b username/feature/your-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin username/feature/your-feature`)
7. Open a Pull Request

## Development Setup

1. Clone the repository with submodules:
   ```bash
   git clone --recurse-submodules https://github.com/onamfc/rag-chat
   cd xantus
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Setup MCP (optional but recommended):
   ```bash
   ./setup_mcp.sh
   ```

5. Configure your environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

## Testing

Before submitting a PR:
- Test your changes with different configurations
- Verify both local (Ollama) and cloud (Anthropic/OpenAI) providers work
- Test document upload, chat, and deletion features
- Ensure MCP integration still works if you modified related code

## Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense ("Add", "Fix", "Update")
- Reference issues when applicable (#123)

## Questions?

Feel free to open an issue for questions or discussions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
