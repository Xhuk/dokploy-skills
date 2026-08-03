# Dokploy Skills

Official API client and tools for [Dokploy](https://dokploy.com/) - Self-hosted PaaS alternative to Heroku, Vercel, and Netlify.

Based on official Dokploy API documentation: https://docs.dokploy.com/docs/api

---

## Quick Install

```bash
# Clone and install
git clone https://github.com/Xhuk/dokploy-skills.git
cd dokploy-skills
pip install -e .
```

---

## Configuration

Create `secrets/dokploy.env`:

```env
DOKPLOY_URL=https://your-dokploy-instance.com
DOKPLOY_API_KEY=your_api_key_here
```

**Get your API key:**
1. Go to `https://your-dokploy-instance.com/settings/profile`
2. Navigate to **API/CLI Section**
3. Click **Generate API Key**
4. Copy the key

---

## API Authentication (Important!)

Dokploy uses **`x-api-key`** header (NOT `Authorization: Bearer`):

```bash
# CORRECT
-H "x-api-key: your_api_key"

# INCORRECT
-H "Authorization: Bearer token"
```

---

## CLI Usage

### List Projects
```bash
dokploy projects list
```

### List Applications
```bash
dokploy apps list
```

### Deploy Application
```bash
dokploy apps deploy --id APPLICATION_ID
```

### Restart Application
```bash
dokploy apps restart --id APPLICATION_ID
```

### List Docker Compose
```bash
dokploy compose list
```

### Deploy Compose
```bash
dokploy compose deploy --id COMPOSE_ID
```

---

## Agent Skill

Cursor / Codex agents should load [`SKILL.md`](SKILL.md) for expert Dokploy operations (discovery, REST↔tRPC fallbacks, deploy verification, rollback posture).

## API Reference

| Doc | Purpose |
|-----|---------|
| [docs/REST_OPERATIONS.md](docs/REST_OPERATIONS.md) | Day-to-day REST playbook + fallbacks |
| [docs/API_VERSIONS.md](docs/API_VERSIONS.md) | REST vs tRPC compatibility |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | Broader endpoint catalogue |

### Key Endpoints

| Resource | Endpoint | Method |
|----------|----------|--------|
| List Projects | `/api/project.all` | GET |
| Create Project | `/api/project.create` | POST |
| List Apps | `/api/application.all` | GET |
| Deploy App | `/api/application.deploy` | POST |
| Restart App | `/api/application.restart` | POST |
| List Compose | `/api/compose.all` | GET |
| Deploy Compose | `/api/compose.deploy` | POST |

**Note:** Some installs omit list/restart endpoints — extract resources from `project.all` and use stop+start. See `docs/API_VERSIONS.md`.

---

## Security Features

All templates include:

- **Non-root containers**: Run as unprivileged users
- **Read-only filesystems**: Where possible
- **Capability dropping**: Minimal Linux capabilities
- **Resource limits**: CPU and memory constraints
- **Health checks**: Automatic monitoring
- **Network isolation**: Internal networks for databases
- **Security headers**: Via Traefik

---

## Available Templates

| Template | Stack |
|----------|-------|
| `nodejs-postgres` | Node.js + PostgreSQL |
| `nextjs-fullstack` | Next.js + PostgreSQL |
| `python-fastapi` | Python + PostgreSQL |
| `python-django` | Django + PostgreSQL |
| `go-api` | Go + PostgreSQL |

---

## Official Documentation

- **Main Docs**: https://docs.dokploy.com/docs/api
- **Authentication**: https://docs.dokploy.com/docs/api/reference-security
- **User API**: https://docs.dokploy.com/docs/api/reference-user
- **Application API**: https://docs.dokploy.com/docs/api/reference-application

---

## License

MIT License
