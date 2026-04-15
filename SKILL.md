# Dokploy Skill

**ID**: dokploy-deployment  
**Version**: 1.3.0  
**Source**: https://docs.dokploy.com/docs/api  
**Category**: DevOps / Deployment  

---

## CRITICAL: Authentication

Dokploy uses **API Key Authentication** via the `x-api-key` header.

```bash
# CORRECT
-H "x-api-key: your_api_key_here"

# INCORRECT - Dokploy does NOT use this
-H "Authorization: Bearer token"
```

---

## API Overview

Dokploy exposes **two API layers** that can behave differently per endpoint:

### 1. OpenAPI/REST Endpoints
**Pattern:** `GET|POST /api/<procedure>`

Used by most read endpoints (`project.all`, `application.one`, etc.).  
**Body:** plain JSON object.

```bash
curl -H "x-api-key: KEY" \
  -X POST https://dokploy.example.com/api/application.stop \
  -d '{"applicationId":"APP_ID"}'
```

### 2. tRPC Endpoints
**Pattern:** `GET|POST /api/trpc/<procedure>`

Used by many mutations on some installs.  
**Body:** must be wrapped in `{"json": <payload>}`.

```bash
curl -H "x-api-key: KEY" \
  -X POST https://dokploy.example.com/api/trpc/application.deploy \
  -d '{"json":{"applicationId":"APP_ID","title":"v1.2.0"}}'
```

**Critical:** Do not assume one layer works for every endpoint on every server.

Real-world pattern:
- one Dokploy server can expose `GET /api/project.all`
- but return `404` for `GET /api/application.all`
- while still accepting `POST /api/application.deploy`
- and rejecting the equivalent tRPC route, or vice versa

Treat compatibility as **endpoint-level**, not just "this server is REST" or "this server is tRPC".

**Base URL:** `https://your-dokploy-instance.com/`

**Authentication Header:** `x-api-key`

**Documentation:** https://docs.dokploy.com/docs/api

---

## Before Any Operation

**MANDATORY**: Verify API key is configured:
1. Check environment: `$env:DOKPLOY_API_KEY`
2. Or check file: `secrets/dokploy.env`
3. Header must be: `x-api-key: $API_KEY`

---

## Core Operations

### 1. List Projects

```bash
GET /api/project.all
```

**Returns:** Array of projects with nested environments, applications, and databases.

**Example Response:**
```json
[
  {
    "projectId": "proj_xxx",
    "name": "My Project",
    "description": "",
    "organizationId": "org_xxx",
    "environments": [
      {
        "name": "production",
        "environmentId": "env_xxx",
        "applications": [...],
        "postgres": [...],
        "redis": [...]
      }
    ]
  }
]
```

### 2. Deploy Application

```bash
POST /api/application.deploy
```

**Body:**
```json
{
  "applicationId": "app_xxx",
  "title": "Deploy v1.2.0"
}
```

Fallback if REST returns `404`, `405`, `400`, or `500`:

```bash
POST /api/trpc/application.deploy
{
  "json": {
    "applicationId": "app_xxx",
    "title": "Deploy v1.2.0"
  }
}
```

### 3. List Applications

```bash
GET /api/application.all
```

Fallback when unavailable:
- extract applications from `GET /api/project.all`
- read `projects[].environments[].applications[]`

### 4. Restart Application

```bash
POST /api/application.restart
```

**Body:**
```json
{
  "applicationId": "app_xxx"
}
```

Fallback when unavailable:
- try `POST /api/application.stop`
- then `POST /api/application.start`

### 5. Update Application Source/Config

```bash
POST /api/application.update
```

**Body:** (plain JSON — tRPC fallback also supported)
```json
{
  "applicationId": "app_xxx",
  "repository": "my-repo",
  "branch": "main",
  "dockerfile": "Dockerfile",
  "buildPath": "."
}
```

### 6. Docker Compose Operations

```bash
# List compose projects
GET /api/compose.all

# Deploy compose
POST /api/compose.deploy
{
  "composeId": "compose_xxx"
}
```

### 7. Database Operations

```bash
# PostgreSQL
GET /api/postgres.all
POST /api/postgres.create
POST /api/postgres.deploy

# MySQL
GET /api/mysql.all
POST /api/mysql.create

# MongoDB
GET /api/mongo.all
POST /api/mongo.create

# Redis
GET /api/redis.all
POST /api/redis.create

# MariaDB
GET /api/mariadb.all
POST /api/mariadb.create
```

---

## User & API Key Management

### Get Current User
```bash
GET /api/user.get
```

### Create API Key
```bash
POST /api/user.createApiKey
{
  "name": "Production Key",
  "prefix": "prod",
  "metadata": {
    "organizationId": "org_xxx"
  },
  "expiresIn": 31536000000,
  "rateLimitEnabled": true,
  "rateLimitTimeWindow": 60000,
  "rateLimitMax": 100
}
```

**Response:**
```json
{
  "result": {
    "data": {
      "key": "prod_dkp_live_abc123...",
      "id": "key_xxx"
    }
  }
}
```

### Delete API Key
```bash
POST /api/user.deleteApiKey
{
  "apiKeyId": "key_xxx"
}
```

---

## Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Owner** | Full access to all resources and settings |
| **Admin** | Manage resources, users, settings (no billing) |
| **Member** | View and manage assigned resources only |

**Note:** API keys inherit permissions of the user who created them.

---

## Rate Limiting

API keys support rate limiting to prevent abuse:

| Setting | Description | Example |
|---------|-------------|---------|
| `rateLimitEnabled` | Enable rate limiting | `true` |
| `rateLimitTimeWindow` | Time window (ms) | `60000` (1 min) |
| `rateLimitMax` | Max requests per window | `100` |
| `remaining` | Initial request limit | `1000` |
| `refillAmount` | Requests to refill | `100` |
| `refillInterval` | Refill interval (ms) | `3600000` (1 hour) |

---

## Security Best Practices

### 1. Store Keys Securely
```bash
# Good: Environment variables
export DOKPLOY_API_KEY="your_key"

# Bad: Hardcoded in scripts
# Never commit API keys to git
```

### 2. Use Descriptive Names
```json
{
  "name": "GitHub Actions - Production",
  "prefix": "gh-prod"
}
```

### 3. Set Expiration
```json
{
  "name": "Temporary Key",
  "expiresIn": 604800000  // 7 days
}
```

### 4. Enable Rate Limiting
```json
{
  "rateLimitEnabled": true,
  "rateLimitTimeWindow": 60000,
  "rateLimitMax": 100
}
```

### 5. Separate Keys per Environment
- Development key
- Staging key
- Production key

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue |
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | Check user permissions |
| 404 | Not Found | Verify endpoint/resource exists |
| 429 | Rate Limited | Wait before retrying |
| 500 | Server Error | Check Dokploy status |

### Error Response Format
```json
{
  "error": {
    "message": "Description",
    "code": "ERROR_CODE"
  }
}
```

### Compatibility Rule

When an endpoint returns `404`, do not conclude "the whole API format is wrong".

Instead:
1. confirm auth with `GET /api/project.all`
2. test the specific endpoint on REST
3. only then test the same operation on tRPC
4. if both fail, use a documented fallback such as extracting from `project.all`

---

## Response Format

Most endpoints return:

```json
{
  "result": {
    "data": {
      "json": [
        // Array of results
      ]
    }
  }
}
```

**Note:** Some endpoints (like `project.all`) return arrays directly without the wrapper.

---

## Getting API Key

### Via Web UI
1. Go to `/settings/profile`
2. Navigate to **API/CLI Section**
3. Click **Generate API Key**
4. Copy the key (format: `prefix_dkp_live_...`)

### Via API (requires existing auth)
```bash
POST /api/user.createApiKey
```

---

## Swagger Documentation

Access Swagger UI at:
```
https://your-dokploy-instance.com/swagger
```

Steps:
1. Navigate to `/swagger`
2. Click **Authorize**
3. Enter your API key
4. Explore available endpoints

---

## Official Resources

- **Main Docs**: https://docs.dokploy.com/docs/api
- **Authentication**: https://docs.dokploy.com/docs/api/reference-security
- **User API**: https://docs.dokploy.com/docs/api/reference-user
- **Application API**: https://docs.dokploy.com/docs/api/reference-application
- **GitHub**: https://github.com/Dokploy/dokploy

---

## Version History

- **1.3.0** (2026-04-15): Endpoint-level compatibility guidance
  - Corrected `application.deploy` guidance to prefer REST first, then tRPC fallback
  - Added fallback rule for `application.one` / `application.all` via `project.all`
  - Documented that Dokploy compatibility varies per endpoint, not only per server version

- **1.2.0** (2026-04-14): Seamless REST + tRPC hybrid support
  - Documented tRPC vs REST API layers
  - Added `update_application`, `restart_application`, `list_containers`
  - CLI automatically falls back to tRPC when REST mutations fail
  - Fixed `application.deploy` to use correct tRPC JSON wrapper

- **1.1.0** (2026-04-11): Updated with official API documentation
  - Correct authentication: `x-api-key` header
  - Complete endpoint reference
  - Rate limiting documentation
  - Roles and permissions
  - Security best practices

- **1.0.0** (2026-04-11): Initial skill

---

**REMEMBER**: Always use `x-api-key` header, never `Authorization: Bearer`.
