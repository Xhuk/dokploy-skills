# Dokploy Skills

Advanced toolkit for managing Dokploy deployments with security best practices and automation.

---

## Quick Install

### One-Line Installers (Auto-detects your environment)

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/Xhuk/dokploy-skills/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -Command "& {$script='https://raw.githubusercontent.com/Xhuk/dokploy-skills/main/install.ps1'; Invoke-WebRequest $script -OutFile install.ps1; .\install.ps1}"
```

**Windows (CMD):**
```cmd
powershell -ExecutionPolicy Bypass -File install.ps1
```

---

## AI Assistant Integration

Dokploy Skills auto-detects your AI environment and provides the appropriate integration method.

| AI Assistant | Install Command | Config File |
|--------------|-----------------|-------------|
| **Claude Code** | `/plugin marketplace add Xhuk/dokploy-skills` | `CLAUDE.md` |
| **Kimi** | `/skill install Xhuk/dokploy-skills` | `SKILLS.md` |
| **Cursor** | `git clone` + project rules | `.cursor/rules/dokploy.md` |
| **Windsurf** | `git clone` + project rules | `.windsurf/rules/dokploy.md` |
| **Codex** | `git clone` | `.codex/config` |
| **Qoder** | `/plugin install Xhuk/dokploy-skills` | `.qoder/skills.md` |
| **Generic** | `pip install git+https://github.com/Xhuk/dokploy-skills.git` | - |

### Force Environment Detection

```bash
# Set environment variable before installing
export KIMI_CLI=1
curl -fsSL https://raw.githubusercontent.com/Xhuk/dokploy-skills/main/install.sh | bash
```

See [docs/ai-integration.md](docs/ai-integration.md) for detailed integration instructions.

---

## Overview

**Dokploy Skills** is a comprehensive CLI toolkit and knowledge base for deploying and managing applications on [Dokploy](https://dokploy.com/) - a self-hosted platform-as-a-service alternative to Heroku and Vercel.

### Key Features

- **Security-First**: Templates and configurations with security hardening built-in
- **CLI Automation**: Command-line tools for common operations
- **Template Library**: Production-ready templates for popular frameworks
- **Best Practices**: Curated from production deployments
- **Anti-Attack Configs**: Rate limiting, CSP headers, non-root containers

---

## Quick Start

### 1. Initialize New Project

```bash
# Create new project from template
dokploy init --name myapp --type nodejs-postgres

# Navigate to project
cd myapp

# Configure environment
cp .env.example .env
# Edit .env with your values

# Run security scan
dokploy security scan

# Deploy
dokploy deploy --project myapp --env production
```

---

## Available Templates

| Template | Stack | Description |
|----------|-------|-------------|
| `nodejs-postgres` | Node.js + PostgreSQL | Express/Fastify API with database |
| `nextjs-fullstack` | Next.js + PostgreSQL | Full-stack Next.js with auth |
| `python-fastapi` | Python + PostgreSQL | Modern FastAPI backend |
| `python-django` | Django + PostgreSQL | Production Django setup |
| `go-api` | Go + PostgreSQL | High-performance API |
| `rust-api` | Rust + PostgreSQL | Memory-safe backend |

### Template Usage

```bash
# List available templates
dokploy template list

# Generate template
dokploy template generate --type nextjs-fullstack --output ./myapp
```

---

## CLI Commands

### Deployment

```bash
# Deploy to production
dokploy deploy --project myapp --env production

# Deploy to staging
dokploy deploy --project myapp --env staging

# View logs
dokploy logs --project myapp --follow

# Check health
dokploy health --project myapp
```

### Security

```bash
# Run security scan
dokploy security scan --project myapp

# Fail on warnings
dokploy security scan --fail-on-warning
```

### Backup

```bash
# Create backup
dokploy backup --project myapp

# Backup to S3
dokploy backup --project myapp --destination s3://mybucket/backups

# Schedule backups (cron)
dokploy backup schedule --project myapp --cron "0 2 * * *"
```

---

## Security Features

Every template includes:

- **Non-root containers**: Services run as unprivileged users
- **Read-only filesystems**: Immutable root where possible
- **Capability dropping**: Minimal Linux capabilities
- **Resource limits**: CPU and memory constraints
- **Health checks**: Automatic container health monitoring
- **Network isolation**: Internal networks for databases
- **Security headers**: HSTS, CSP, XSS protection via Traefik

### Security Checklist

Before production deployment:

- [ ] VPS firewall enabled (UFW)
- [ ] SSH key auth only
- [ ] Automatic security updates
- [ ] Non-root Docker containers
- [ ] Secrets in environment variables
- [ ] HTTPS with valid certificates
- [ ] Security headers configured
- [ ] Rate limiting enabled

See [docs/security-best-practices.md](docs/security-best-practices.md) for complete guide.

---

## Dokploy Configuration

### Required Environment Variables

```bash
# Database
DB_USER=myuser
DB_PASSWORD=secure_random_password
DB_NAME=myapp

# Domain
DOMAIN=app.example.com

# Project (for Traefik routing)
PROJECT_NAME=myapp
```

### Volume Mounts

Dokploy uses `../files/` for persistent storage:

```yaml
volumes:
  - ../files/uploads:/app/uploads
  - ../files/postgres:/var/lib/postgresql/data
```

### Network Configuration

```yaml
networks:
  # External: For Traefik
  dokploy-network:
    external: true
  # Internal: App to DB only
  backend:
    driver: bridge
    internal: true
```

---

## Project Structure

```
dokploy-skills/
├── cli/
│   ├── dokploy.py              # Main CLI tool
│   └── ai-env-detector.py      # AI environment detector
├── templates/
│   ├── nodejs-postgres/        # Node.js + PostgreSQL template
│   ├── nextjs-fullstack/       # Next.js template
│   └── python-fastapi/         # Python FastAPI
├── docs/
│   ├── security-best-practices.md
│   ├── ai-integration.md       # AI assistant integration
│   └── dokploy-guide.md
├── install.sh                  # Linux/macOS installer
├── install.ps1                 # Windows installer
├── setup.py                    # Python package setup
├── requirements.txt            # Dependencies
├── LICENSE                     # MIT License
├── CONTRIBUTING.md             # Contributing guide
└── README.md                   # This file
```

---

## Example: Node.js + PostgreSQL

### 1. Initialize

```bash
dokploy init --name myapi --type nodejs-postgres
cd myapi
```

### 2. Configure

Edit `.env`:
```bash
DB_USER=apiuser
DB_PASSWORD=$(openssl rand -base64 32)
DB_NAME=myapi
DOMAIN=api.example.com
PROJECT_NAME=myapi
```

### 3. Security Scan

```bash
dokploy security scan
```

### 4. Deploy

```bash
dokploy deploy --project myapi
```

---

## Advanced Usage

### Multi-Environment Setup

```yaml
# dokploy.yaml
environments:
  production:
    dokploy_url: https://dokploy.example.com
    domain: app.example.com
    
  staging:
    dokploy_url: https://dokploy.example.com
    domain: staging.example.com
```

```bash
# Deploy to staging
dokploy deploy --project myapp --env staging

# Deploy to production
dokploy deploy --project myapp --env production
```

### Custom Templates

```bash
# Create template from existing project
dokploy template create --from ./myproject --name custom-template

# Share template
cp -r templates/custom-template ./my-shared-templates/
```

---

## Local Installation (Development)

```bash
# Clone repository
git clone https://github.com/Xhuk/dokploy-skills.git
cd dokploy-skills

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Run tests
python -m pytest
```

---

## Requirements

- **Python**: 3.8+
- **Dokploy**: Latest version
- **Docker & Docker Compose**
- **VPS**: Ubuntu 20.04+ or Debian 11+

---

## Environment Detection

The installer automatically detects your AI environment:

```bash
# Check detected environment
python ai-env-detector.py

# Get install command only
python ai-env-detector.py --install-cmd

# JSON output
python ai-env-detector.py --format json
```

Detection methods:
- Environment variables (`CLAUDE_CODE`, `KIMI_CLI`, etc.)
- Directory markers (`.claude/`, `.kimi/`, etc.)

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Submit a pull request

### Adding Templates

1. Create directory in `templates/`
2. Include `docker-compose.yml`, `Dockerfile`, `dokploy.yaml`, `.env.example`
3. Follow security best practices
4. Document in README

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Resources

- [Dokploy Documentation](https://docs.dokploy.com/)
- [Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Made with security in mind** - Production-ready deployments without the headaches.

**Questions?** Open an issue at https://github.com/Xhuk/dokploy-skills/issues
