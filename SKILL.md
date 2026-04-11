# Dokploy Skill

**ID**: dokploy-deployment  
**Version**: 1.1.0  
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

**Base URL:** `https://your-dokploy-instance.com/api/`

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
  "title": "Deploy v1.2.0",
  "description": "Optional description"
}
```

### 3. List Applications

```bash
GET /api/application.all
```

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

### 5. Docker Compose Operations

```bash
# List compose projects
GET /api/compose.all

# Deploy compose
POST /api/compose.deploy
{
  "composeId": "compose_xxx"
}
```

### 6. Database Operations

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

- **1.1.0** (2026-04-11): Updated with official API documentation
  - Correct authentication: `x-api-key` header
  - Complete endpoint reference
  - Rate limiting documentation
  - Roles and permissions
  - Security best practices

- **1.0.0** (2026-04-11): Initial skill

---

**REMEMBER**: Always use `x-api-key` header, never `Authorization: Bearer`.
