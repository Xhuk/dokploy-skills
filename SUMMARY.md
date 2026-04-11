# Dokploy Skills - Repository Summary

Complete toolkit for managing Dokploy deployments with security-first approach.

---

## Repository Structure

```
dokploy-skills/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
│
├── cli/
│   ├── dokploy.py              # Main CLI tool (13.5KB)
│   └── ai-env-detector.py      # AI environment detector (6.8KB)
│
├── docs/
│   ├── ai-integration.md       # AI assistant integration guide (6.2KB)
│   └── security-best-practices.md  # Security hardening guide (9.5KB)
│
├── templates/
│   └── nodejs-postgres/        # Node.js + PostgreSQL template
│       ├── .env.example        # Environment variables template
│       ├── docker-compose.yml  # Docker Compose with security
│       ├── Dockerfile          # Hardened container image
│       └── dokploy.yaml        # Dokploy configuration
│
├── CONTRIBUTING.md             # Contributing guidelines
├── install.ps1                 # Windows installer (8.6KB)
├── install.sh                  # Linux/macOS installer (7.8KB)
├── LICENSE                     # MIT License
├── README.md                   # Main documentation (9.5KB)
├── requirements.txt            # Python dependencies
├── setup.py                    # Python package setup
└── SUMMARY.md                  # This file
```

---

## Key Features

### 1. Universal Installation

- **Curl one-liner** for Linux/macOS
- **PowerShell one-liner** for Windows
- **Auto-detects** AI assistant environment
- **Adapts installation** method per environment

### 2. AI Assistant Integration

| Assistant | Detection Method | Install Command |
|-----------|-----------------|-----------------|
| Claude Code | `CLAUDE_CODE` env, `.claude/` dir | `/plugin marketplace add` |
| Kimi | `KIMI_CLI` env, `.kimi/` dir | `/skill install` |
| Cursor | `CURSOR` env, `.cursor/` dir | `git clone` + rules |
| Windsurf | `WINDSURF` env, `.windsurf/` dir | `git clone` + rules |
| Codex | `CODEX_CLI` env, `.codex/` dir | `git clone` |
| Qoder | `QODER` env, `.qoder/` dir | `/plugin install` |
| Copilot | `COPILOT` env, `.github/copilot/` | Workspace import |

### 3. Security-First Templates

Every template includes:
- Non-root containers (UID 1001)
- Read-only root filesystem
- Dropped capabilities (only CHOWN, SETGID, SETUID)
- Resource limits (CPU/memory)
- Health checks
- Internal networks for databases
- Security headers (HSTS, CSP, XSS)

### 4. CLI Commands

```bash
# Project management
dokploy init --name <app> --type <template>
dokploy template list
dokploy template generate --type <type>

# Security
dokploy security scan [--project <name>] [--fail-on-warning]

# Deployment
dokploy deploy --project <name> [--env <environment>]
dokploy logs --project <name> [--service <svc>] [--follow]
dokploy health --project <name>

# Backup
dokploy backup --project <name> [--destination <path>]
```

---

## Installation Methods

### Method 1: One-Line Install (Recommended)

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/Xhuk/dokploy-skills/main/install.sh | bash
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -Command "& {$script='https://raw.githubusercontent.com/Xhuk/dokploy-skills/main/install.ps1'; Invoke-WebRequest $script -OutFile install.ps1; .\install.ps1}"
```

### Method 2: AI Assistant Integration

**Claude Code:**
```
/plugin marketplace add Xhuk/dokploy-skills
```

**Kimi:**
```
/skill install Xhuk/dokploy-skills
```

**Others:**
See [docs/ai-integration.md](docs/ai-integration.md)

### Method 3: Manual Installation

```bash
# Clone repository
git clone https://github.com/Xhuk/dokploy-skills.git
cd dokploy-skills

# Install
pip install -e .

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install -e .
```

---

## Available Templates

| Template | Stack | Security Features |
|----------|-------|-------------------|
| `nodejs-postgres` | Node.js 18 + PostgreSQL 15 | Non-root, read-only fs, health checks |
| `nextjs-fullstack` | Next.js + PostgreSQL | + CSP headers, rate limiting |
| `python-fastapi` | Python 3.11 + PostgreSQL | + Uvicorn security |
| `python-django` | Django + PostgreSQL | + Django security settings |
| `go-api` | Go + PostgreSQL | + Minimal attack surface |
| `rust-api` | Rust + PostgreSQL | + Memory safety |

---

## Security Measures

### Container Security
- Non-root user execution
- Read-only root filesystem
- Capability dropping
- Resource limits
- Security options (no-new-privileges)

### Network Security
- Internal Docker networks
- Dokploy-Traefik integration
- TLS/SSL termination
- Security headers (HSTS, CSP, XSS)

### Operational Security
- Environment variables for secrets
- Health check endpoints
- Automatic restarts
- Backup automation

---

## File Sizes

| File | Size | Description |
|------|------|-------------|
| `cli/dokploy.py` | 13.5 KB | Main CLI with all commands |
| `cli/ai-env-detector.py` | 6.8 KB | Environment detection |
| `docs/security-best-practices.md` | 9.5 KB | Security guide |
| `docs/ai-integration.md` | 6.2 KB | AI integration docs |
| `README.md` | 9.5 KB | Main documentation |
| `install.sh` | 7.8 KB | Linux/macOS installer |
| `install.ps1` | 8.6 KB | Windows installer |
| **Total** | **~65 KB** | Complete toolkit |

---

## Requirements

- **Python**: 3.8+
- **Git**: 2.0+
- **pip**: 20.0+
- **Dokploy**: Latest version
- **Docker**: 20.10+
- **Docker Compose**: 1.29+

---

## Quick Start Workflow

```bash
# 1. Install
curl -fsSL https://raw.githubusercontent.com/Xhuk/dokploy-skills/main/install.sh | bash

# 2. Initialize project
dokploy init --name myapp --type nodejs-postgres
cd myapp

# 3. Configure
cp .env.example .env
# Edit .env with your values

# 4. Security scan
dokploy security scan

# 5. Deploy
dokploy deploy --env production

# 6. Monitor
dokploy logs --follow
dokploy health
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Template requirements
- Pull request process

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Links

- **Repository**: https://github.com/Xhuk/dokploy-skills
- **Issues**: https://github.com/Xhuk/dokploy-skills/issues
- **Dokploy Docs**: https://docs.dokploy.com/

---

**Last Updated**: 2026-04-11
**Version**: 1.0.0
