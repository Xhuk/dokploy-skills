# Contributing to Dokploy Skills

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone repository
git clone https://github.com/Xhuk/dokploy-skills.git
cd dokploy-skills

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install dev dependencies
pip install flake8 pytest black
```

## Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to functions
- Keep functions small and focused

## Adding Templates

Templates should include:

1. `docker-compose.yml` - Docker Compose configuration
2. `Dockerfile` - Container build instructions
3. `dokploy.yaml` - Dokploy-specific configuration
4. `.env.example` - Example environment variables
5. `README.md` - Template-specific documentation

### Template Requirements

- Use non-root containers
- Include health checks
- Set resource limits
- Use internal networks for databases
- Follow security best practices

## Testing

```bash
# Run security scan on template
dokploy security scan --project myapp

# Validate docker-compose
docker-compose config

# Test CLI
dokploy template list
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit PR with clear description

## Security

If you discover a security issue, please email the maintainers directly rather than opening a public issue.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
