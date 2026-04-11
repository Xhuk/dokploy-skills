# Dokploy API Reference

> Based on official Dokploy documentation: https://docs.dokploy.com/docs/api

---

## Authentication

Dokploy uses **API Key Authentication** via the `x-api-key` header.

```bash
# CORRECT
-H "x-api-key: your_api_key_here"

# INCORRECT - Dokploy does NOT use this
-H "Authorization: Bearer token"
```

### Generating API Keys

1. Go to `/settings/profile` in your Dokploy dashboard
2. Navigate to **API/CLI Section**
3. Click **Generate API Key**
4. Copy the key (format: `prefix_dkp_live_...` or custom)

---

## Base URL

```
https://your-dokploy-instance.com/api/
```

---

## Core Endpoints

### Projects

#### List All Projects
```bash
GET /api/project.all
```

**Example:**
```bash
curl -X GET "https://dokploy.example.com/api/project.all" \
  -H "x-api-key: your_api_key"
```

#### Create Project
```bash
POST /api/project.create
```

**Body:**
```json
{
  "name": "My Project",
  "description": "Production environment"
}
```

---

### Applications

#### List Applications
```bash
GET /api/application.all
```

#### Create Application
```bash
POST /api/application.create
```

**Body:**
```json
{
  "name": "My App",
  "environmentId": "env_abc123",
  "description": "Production application"
}
```

#### Deploy Application
```bash
POST /api/application.deploy
```

**Body:**
```json
{
  "applicationId": "app_xyz789",
  "title": "Deploy v1.2.0",
  "description": "Production deployment"
}
```

#### Restart Application
```bash
POST /api/application.restart
```

**Body:**
```json
{
  "applicationId": "app_xyz789"
}
```

#### Stop Application
```bash
POST /api/application.stop
```

---

### Docker Compose

#### List Compose Projects
```bash
GET /api/compose.all
```

#### Create Compose
```bash
POST /api/compose.create
```

#### Deploy Compose
```bash
POST /api/compose.deploy
```

---

### Databases

#### PostgreSQL
```bash
GET /api/postgres.all
POST /api/postgres.create
POST /api/postgres.deploy
```

#### MySQL
```bash
GET /api/mysql.all
POST /api/mysql.create
```

#### MongoDB
```bash
GET /api/mongo.all
POST /api/mongo.create
```

#### Redis
```bash
GET /api/redis.all
POST /api/redis.create
```

#### MariaDB
```bash
GET /api/mariadb.all
POST /api/mariadb.create
```

---

### API Key Management

#### Create API Key
```bash
POST /api/user.createApiKey
```

**Body:**
```json
{
  "name": "Production API Key",
  "prefix": "prod",
  "expiresIn": 31536000000,
  "metadata": {
    "organizationId": "org_abc123"
  },
  "rateLimitEnabled": true,
  "rateLimitTimeWindow": 60000,
  "rateLimitMax": 100
}
```

#### List API Keys
```bash
GET /api/user.get
```

Keys are returned in the user object.

#### Delete API Key
```bash
POST /api/user.deleteApiKey
```

**Body:**
```json
{
  "apiKeyId": "key_xyz789"
}
```

---

### User & Organization

#### Get Current User
```bash
GET /api/user.get
```

#### Check Organizations
```bash
GET /api/user.checkUserOrganizations?userId=string
```

#### Get Container Metrics
```bash
GET /api/user.getContainerMetrics?url=string&token=string&appName=string&dataPoints=string
```

---

## Response Format

All API responses follow this structure:

```json
{
  "result": {
    "data": {
      // Response data here
    }
  }
}
```

For tRPC endpoints (most common):

```json
{
  "result": {
    "data": {
      "json": [
        // Array of projects/applications/etc
      ]
    }
  }
}
```

---

## Rate Limiting

API keys can be configured with rate limits:

- `rateLimitEnabled`: Enable rate limiting (boolean)
- `rateLimitTimeWindow`: Time window in milliseconds (e.g., 60000 = 1 minute)
- `rateLimitMax`: Maximum requests per time window
- `remaining`: Initial number of requests available
- `refillAmount`: Number of requests to add on each refill
- `refillInterval`: Milliseconds between refills

---

## Security Best Practices

1. **Store keys securely**: Use environment variables
2. **Use descriptive names**: Name keys based on purpose
3. **Set expiration dates**: For temporary access
4. **Enable rate limiting**: Always for production keys
5. **Use separate keys per environment**: dev, staging, prod

---

## Environment Variables

```bash
# Recommended setup
export DOKPLOY_URL="https://dokploy.example.com"
export DOKPLOY_API_KEY="your_api_key_here"

# Usage
curl -H "x-api-key: $DOKPLOY_API_KEY" "$DOKPLOY_URL/api/project.all"
```

---

## Error Handling

### Common Status Codes

- `200`: Success
- `401`: Unauthorized - Invalid or missing API key
- `403`: Forbidden - Insufficient permissions
- `404`: Not found - Endpoint or resource doesn't exist
- `429`: Rate limited - Too many requests

### Error Response

```json
{
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

---

## Official Documentation

- **Main Docs**: https://docs.dokploy.com/docs/api
- **Authentication**: https://docs.dokploy.com/docs/api/reference-security
- **User API**: https://docs.dokploy.com/docs/api/reference-user
- **Application API**: https://docs.dokploy.com/docs/api/reference-application

---

**Last Updated**: Based on Dokploy docs as of 2026-04-11
