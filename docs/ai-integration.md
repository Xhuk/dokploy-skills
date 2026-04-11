# AI Assistant Integration Guide

How to integrate Dokploy Skills with different AI assistants and environments.

---

## Quick Install

### Universal Installer (Auto-detects environment)

```bash
# Linux/macOS
curl -fsSL https://raw.githubusercontent.com/Xhuk/dokploy-skills/main/install.sh | bash

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -Command "& {$script='https://raw.githubusercontent.com/Xhuk/dokploy-skills/main/install.ps1'; Invoke-WebRequest $script -OutFile install.ps1; .\install.ps1}"
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/Xhuk/dokploy-skills.git
cd dokploy-skills
pip install -e .
```

---

## Per-Assistant Integration

### Claude Code

**Install Command:**
```
/plugin marketplace add Xhuk/dokploy-skills
```

**CLAUDE.md Integration:**
```markdown
# Dokploy Skills

Use this skill for managing Dokploy deployments.

## Commands
- dokploy init --name <app> --type <template>
- dokploy security scan
- dokploy deploy --env production

## Security Rules
- Always run security scan before deploying
- Use non-root containers
- Store secrets in environment variables
```

**Environment Variables:**
```bash
export CLAUDE_CODE=1
```

---

### Kimi Code

**Install Command:**
```
/skill install Xhuk/dokploy-skills
```

**SKILLS.md Integration:**
```markdown
## Dokploy Skills
Repository: Xhuk/dokploy-skills
Description: Advanced toolkit for Dokploy deployments
Commands:
  - dokploy init
  - dokploy security scan
  - dokploy deploy
```

**Environment Variables:**
```bash
export KIMI_CLI=1
```

---

### Cursor

**Project Rules:**
Create `.cursor/rules/dokploy.md`:

```markdown
# Dokploy Skills

When working with deployments:

1. Always use `dokploy security scan` before deploying
2. Use templates from dokploy-skills/templates/
3. Follow security best practices:
   - Non-root containers
   - Read-only filesystems
   - Internal networks for databases
   - Environment variables for secrets

## Commands
- Initialize: dokploy init --name <app> --type <template>
- Security: dokploy security scan --fail-on-warning
- Deploy: dokploy deploy --env production
```

**Environment Variables:**
```bash
export CURSOR=1
```

---

### Windsurf

**Project Rules:**
Create `.windsurf/rules/dokploy.md`:

```markdown
# Dokploy Skills

Deployment guidelines:
- Use dokploy CLI for all deployments
- Run security scans before production
- Use provided templates for consistency
```

**Environment Variables:**
```bash
export WINDSURF=1
```

---

### Codex (OpenAI)

**Integration:**
```bash
# Add to .codex/config
{
  "skills": [
    "Xhuk/dokploy-skills"
  ]
}
```

**Environment Variables:**
```bash
export CODEX_CLI=1
```

---

### Qoder

**Install Command:**
```
/plugin install Xhuk/dokploy-skills
```

**Environment Variables:**
```bash
export QODER=1
```

---

### GitHub Copilot

**Integration:**
Use Copilot Workspace to import the repository or add to `.github/copilot/skills.md`.

**Environment Variables:**
```bash
export COPILOT=1
```

---

## Local Installation

### Without AI Detection

```bash
# Direct pip install
pip install git+https://github.com/Xhuk/dokploy-skills.git

# Or clone and install
git clone https://github.com/Xhuk/dokploy-skills.git
cd dokploy-skills
pip install -e .
```

### Development Mode

```bash
# Clone for development
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

## Environment Detection

The installer automatically detects your AI environment using:

1. **Environment Variables:**
   - `CLAUDE_CODE`, `ANTHROPIC_API_KEY`
   - `KIMI_CLI`
   - `CODEX_CLI`
   - `CURSOR`
   - `WINDSURF`
   - `QODER`
   - `COPILOT`

2. **Directory Markers:**
   - `.claude/`
   - `.kimi/`
   - `.codex/`
   - `.cursor/`
   - `.windsurf/`
   - `.qoder/`
   - `.github/copilot/`

### Force Environment

```bash
# Force specific environment
export KIMI_CLI=1
curl -fsSL https://raw.githubusercontent.com/Xhuk/dokploy-skills/main/install.sh | bash
```

---

## Post-Installation

### Verify Installation

```bash
# Check CLI is available
dokploy --version

# Test commands
dokploy template list
dokploy security scan
```

### Add to Shell (Linux/macOS)

```bash
# Add to PATH if not already there
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
# or
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# Reload
source ~/.bashrc  # or source ~/.zshrc
```

### Add to PATH (Windows)

```powershell
# Add to User PATH
[Environment]::SetEnvironmentVariable(
    "PATH",
    "$env:PATH;$env:USERPROFILE\dokploy-skills",
    "User"
)
```

---

## Troubleshooting

### Python Not Found

```bash
# Install Python 3.8+
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# macOS
brew install python

# Windows: Download from python.org
```

### Permission Denied

```bash
# Linux/macOS - Use --user flag
pip install --user -e .

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Git Not Found

```bash
# Install Git
# Ubuntu/Debian
sudo apt install git

# macOS
brew install git

# Windows: Download from git-scm.com
```

---

## Docker Installation

For isolated environments:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install git+https://github.com/Xhuk/dokploy-skills.git

ENTRYPOINT ["dokploy"]
```

```bash
# Build and run
docker build -t dokploy-skills .
docker run -it dokploy-skills template list
```

---

## Uninstallation

```bash
# Remove package
pip uninstall dokploy-skills

# Remove directory
rm -rf ~/.dokploy-skills

# Remove from PATH (edit ~/.bashrc or ~/.zshrc)
```

---

**Need Help?** Open an issue at https://github.com/Xhuk/dokploy-skills/issues
