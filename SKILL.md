---
name: dokploy-skills
description: >-
  Expert Dokploy operations for self-hosted PaaS deploy, discover, rebuild,
  compose, databases, and API troubleshooting. Use when the user mentions
  Dokploy, dokploy apps/projects/compose, x-api-key deploys, Traefik routes on
  Dokploy, or REST vs tRPC Dokploy API compatibility.
---

# Dokploy Skill (Expert)

**ID**: dokploy-skills  
**Version**: 1.4.0  
**Source**: https://docs.dokploy.com/docs/api  
**Category**: DevOps / Deployment  

Use this skill to operate Dokploy like a practiced platform engineer: discover IDs safely, choose the right API layer per endpoint, deploy/rebuild/compose with verification, and recover from mixed-install quirks without leaking secrets.

---

## CRITICAL: Authentication

Dokploy uses **API Key Authentication** via the `x-api-key` header.

```bash
# CORRECT
-H "x-api-key: your_api_key_here"

# INCORRECT - Dokploy does NOT use this for API keys
-H "Authorization: Bearer token"
```

**Never** print API keys, dump `secrets/dokploy.env`, or commit tokens.

---

## Mental Model

Dokploy is a self-hosted PaaS (Heroku/Vercel/Netlify alternative) that manages:

```text
Organization
└── Project
    └── Environment(s)          # newer installs
        ├── applications[]      # Dockerfile / Nixpacks / build packs
        ├── compose[]           # docker-compose stacks
        ├── postgres|mysql|mongo|mariadb|redis[]
        └── domains / Traefik routes
```

Older installs nest `applications`, `compose`, and databases **directly under the project** (no `environments[]`). Always handle both shapes when parsing `project.all`.

| Resource | When to use |
|----------|-------------|
| **Application** | Single service with one build context (API, web, worker) |
| **Compose** | Multi-service stack defined in `docker-compose.yml` |
| **Managed DB** | Dokploy-provisioned postgres/mysql/mongo/redis/mariadb |
| **Deployment** | History + logs for an application operation |

---

## API Overview (Two Layers)

### 1. OpenAPI / REST

**Pattern:** `GET|POST /api/<procedure>`  
**Body:** plain JSON object.

```bash
curl -H "x-api-key: KEY" \
  -X POST https://dokploy.example.com/api/application.stop \
  -d '{"applicationId":"APP_ID"}'
```

### 2. tRPC

**Pattern:** `GET|POST /api/trpc/<procedure>`  
**Body:** must be wrapped in `{"json": <payload>}` for mutations.

```bash
curl -H "x-api-key: KEY" \
  -X POST https://dokploy.example.com/api/trpc/application.deploy \
  -d '{"json":{"applicationId":"APP_ID","title":"v1.2.0"}}'
```

### Compatibility rule (memorize this)

Do **not** assume one layer works for every endpoint on every server.

Real-world pattern:
- `GET /api/project.all` works
- `GET /api/application.all` returns `404`
- `POST /api/application.deploy` works on REST
- equivalent tRPC may be missing — or the reverse

Treat compatibility as **endpoint-level**. Details: `docs/API_VERSIONS.md`.

**Base URL:** `https://your-dokploy-instance.com/`  
**Docs:** https://docs.dokploy.com/docs/api  
**Swagger (if enabled):** `/swagger`

---

## Before Any Operation

1. Resolve `DOKPLOY_URL` and `DOKPLOY_API_KEY` (or `DOKPLOY_TOKEN`) from env or `secrets/dokploy.env`.
2. Confirm auth with a cheap reader: `GET /api/project.all`.
3. Resolve target IDs by name from that payload — do not hardcode customer app IDs in shared skills.
4. Prefer the local CLI (`cli/dokploy.py`) when installed; it already implements REST→tRPC fallbacks.

```bash
dokploy projects list
dokploy apps list
dokploy apps deploy --id APP_ID --title "reason"
```

---

## Expert Decision Tree

```text
Need to act on Dokploy?
├─ Missing credentials? → stop; ask for URL+key or OpenBao path; never invent
├─ Unknown app/project ID?
│  └─ GET project.all → match name → cache applicationId/composeId
├─ Deploy / rebuild / update?
│  ├─ Try REST /api/<procedure>
│  └─ On 404/405/400/500 → try /api/trpc/<procedure> with {"json":...}
├─ List apps/compose missing?
│  └─ Extract from project.all (environments[] or flat)
├─ Restart missing?
│  └─ stop + start (or rebuild if cold restart is OK)
└─ After mutation → check applicationStatus + public HTTP route
```

---

## Core Operations

### 1. List Projects (canonical discovery)

```bash
GET /api/project.all
```

Returns projects with nested environments/apps/DBs (shape varies by version).

### 2. Deploy Application

```bash
POST /api/application.deploy
{"applicationId":"app_xxx","title":"Deploy v1.2.0"}
```

tRPC fallback:

```bash
POST /api/trpc/application.deploy
{"json":{"applicationId":"app_xxx","title":"Deploy v1.2.0"}}
```

### 3. List / Get Applications

```bash
GET /api/application.all
GET /api/application.one?applicationId=APP_ID
```

Fallback: extract from `project.all`.

### 4. Restart / Stop / Start / Rebuild

```bash
POST /api/application.restart   # body: {"applicationId":"..."}
POST /api/application.stop
POST /api/application.start
POST /api/application.rebuild
```

### 5. Update Application Source/Config

```bash
POST /api/application.update
{
  "applicationId": "app_xxx",
  "repository": "my-repo",
  "branch": "main",
  "dockerfile": "Dockerfile",
  "buildPath": "."
}
```

### 6. Compose

```bash
GET /api/compose.all
POST /api/compose.deploy
{"composeId":"compose_xxx"}
```

### 7. Databases

```bash
GET|POST /api/postgres.(all|create|deploy)
GET|POST /api/mysql.(all|create)
GET|POST /api/mongo.(all|create)
GET|POST /api/redis.(all|create)
GET|POST /api/mariadb.(all|create)
```

### 8. Deployments & Logs

```bash
GET /api/deployment.all?applicationId=APP_ID
GET /api/deployment.getLogs?deploymentId=DEPLOY_ID
```

---

## Status & Verification

| `applicationStatus` | Meaning |
|---------------------|---------|
| `done` | Last op succeeded / healthy |
| `running` | Deploy/rebuild in progress |
| `error` | Failed — pull deployment logs |
| `idle` / `stopped` | Not serving (wording varies) |

After deploy/rebuild:

1. Wait until status leaves `running` (poll `application.one` or re-read `project.all`).
2. `curl -I https://public-host/` (and app path if any).
3. For frontends, fetch HTML and confirm expected bundle/title changed.
4. On `error`, fetch `deployment.getLogs` before retrying blindly.

---

## Rollback Posture

Dokploy rarely offers a universal one-click image rollback. Expert options:

1. Point the app at a known-good git tag/SHA → `application.update` → `application.deploy`.
2. `application.rebuild` when rebuild reproduces the last good artifact.
3. Redeploy with title `Rollback to previous stable` and verify the public route.

Document what was rolled from/to (commit, title, timestamp) without pasting secrets.

---

## User & API Key Management

```bash
GET /api/user.get

POST /api/user.createApiKey
{
  "name": "Production Key",
  "prefix": "prod",
  "metadata": {"organizationId": "org_xxx"},
  "expiresIn": 31536000000,
  "rateLimitEnabled": true,
  "rateLimitTimeWindow": 60000,
  "rateLimitMax": 100
}

POST /api/user.deleteApiKey
{"apiKeyId":"key_xxx"}
```

| Role | Permissions |
|------|-------------|
| **Owner** | Full access |
| **Admin** | Manage resources/users/settings (no billing) |
| **Member** | Assigned resources only |

API keys inherit the creating user's permissions.

---

## Security Best Practices

1. Store keys in env / secret manager — never in git.
2. Separate keys per environment (dev / staging / prod).
3. Set expiration and rate limits on automation keys.
4. Use descriptive key names (`GitHub Actions - Production`).
5. Prefer non-root containers, health checks, and internal DB networks (see `templates/` and `docs/security-best-practices.md`).

---

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue / verify |
| 401 | Unauthorized | Check `x-api-key`, expiry, org |
| 403 | Forbidden | Check role permissions |
| 404 | Not Found | Probe alternate layer or `project.all` fallback |
| 429 | Rate Limited | Back off |
| 500 | Server Error | Check body; try alternate JSON/tRPC shape; check Dokploy logs |

### Compatibility recovery

When an endpoint returns `404`:

1. Confirm auth with `GET /api/project.all`
2. Retry the specific endpoint on REST
3. Only then try tRPC for that same operation
4. If list/detail is missing, extract from `project.all`

---

## Getting an API Key

1. Open `/settings/profile`
2. API/CLI section → Generate API Key
3. Copy once (format often `prefix_dkp_live_...` or `dokploy_...`)

---

## Deep References (read when needed)

| Doc | Use when |
|-----|----------|
| `docs/REST_OPERATIONS.md` | Day-to-day REST workflows & fallbacks |
| `docs/API_VERSIONS.md` | REST vs tRPC detection & mixed installs |
| `docs/API_REFERENCE.md` | Broader endpoint catalogue |
| `docs/COMPLETE_API.md` | Exhaustive procedure list |
| `docs/TRPC_GUIDE.md` | tRPC request/response wrapping |
| `docs/security-best-practices.md` | Hardening templates & runtime |
| `docs/ai-integration.md` | Installing this skill into AI tools |
| `cli/dokploy.py` | Hybrid CLI with automatic fallbacks |

Official:

- https://docs.dokploy.com/docs/api
- https://docs.dokploy.com/docs/api/reference-security
- https://docs.dokploy.com/docs/api/reference-user
- https://docs.dokploy.com/docs/api/reference-application
- https://github.com/Dokploy/dokploy

---

## Version History

- **1.4.0** (2026-08-02): Product-neutral expert skill
  - Removed product-specific tower mappings and private host examples
  - Added mental model, decision tree, verification, and rollback posture
  - Pointed operators at generic `docs/REST_OPERATIONS.md`
- **1.3.0** (2026-04-15): Endpoint-level compatibility guidance
- **1.2.0** (2026-04-14): Seamless REST + tRPC hybrid support
- **1.1.0** (2026-04-11): Official API documentation alignment
- **1.0.0** (2026-04-11): Initial skill

---

**REMEMBER**: Always use `x-api-key`, never print secrets, resolve IDs from `project.all`, and validate each mutation endpoint before fleet automation.
