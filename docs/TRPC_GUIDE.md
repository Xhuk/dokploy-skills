# Dokploy tRPC API Guide

> Dokploy uses tRPC (TypeScript RPC) instead of traditional REST API.

---

## What is tRPC?

tRPC provides end-to-end type safety between client and server. Unlike REST with fixed URLs, tRPC uses **procedures** that are called remotely.

---

## Endpoint Structure

### tRPC URL Format

```
https://your-dokploy.com/api/trpc/[PROCEDURE]?batch=1
```

**Examples:**
- List projects: `/api/trpc/project.all?batch=1`
- Deploy app: `/api/trpc/application.deploy?batch=1`
- Get user: `/api/trpc/user.get?batch=1`

### Request Format

**GET requests** (no body):
```bash
curl -H "x-api-key: YOUR_KEY" \
  https://dokploy.com/api/trpc/project.all?batch=1
```

**POST requests** (with body):
```bash
curl -X POST \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"0": {"applicationId": "app_xxx"}}' \
  https://dokploy.com/api/trpc/application.deploy?batch=1
```

**Important:** The `?batch=1` parameter is required. The body must be wrapped in `{"0": {...}}`.

---

## Response Format

### Success Response

```json
[
  {
    "result": {
      "data": {
        "json": [
          // Your data here
        ]
      }
    }
  }
]
```

### Error Response

```json
[
  {
    "error": {
      "message": "Error description",
      "code": "ERROR_CODE"
    }
  }
]
```

---

## Common Procedures

### Projects

| Action | Procedure | Method |
|--------|-----------|--------|
| List all | `project.all` | GET |
| Create | `project.create` | POST |

### Applications

| Action | Procedure | Method |
|--------|-----------|--------|
| List all | `application.all` | GET |
| Create | `application.create` | POST |
| Deploy | `application.deploy` | POST |
| Restart | `application.reload` | POST |
| Stop | `application.stop` | POST |
| Start | `application.start` | POST |
| Remove | `application.remove` | POST |

### Compose

| Action | Procedure | Method |
|--------|-----------|--------|
| List all | `compose.all` | GET |
| Create | `compose.create` | POST |
| Deploy | `compose.deploy` | POST |

### Databases

| Type | List | Create | Deploy |
|------|------|--------|--------|
| PostgreSQL | `postgres.all` | `postgres.create` | `postgres.deploy` |
| MySQL | `mysql.all` | `mysql.create` | `mysql.deploy` |
| MongoDB | `mongo.all` | `mongo.create` | `mongo.deploy` |
| Redis | `redis.all` | `redis.create` | `redis.deploy` |
| MariaDB | `mariadb.all` | `mariadb.create` | `mariadb.deploy` |

### User

| Action | Procedure | Method |
|--------|-----------|--------|
| Get info | `user.get` | GET |
| Create API key | `user.createApiKey` | POST |
| Delete API key | `user.deleteApiKey` | POST |

---

## JavaScript/Node.js Example

```javascript
const DOKPLOY_URL = "https://your-dokploy.com";
const API_KEY = "your_api_key";

async function callDokploy(procedure, payload = null, method = 'POST') {
    const url = `${DOKPLOY_URL}/api/trpc/${procedure}?batch=1`;
    
    const options = {
        method: method,
        headers: {
            'x-api-key': API_KEY,
            'Content-Type': 'application/json'
        }
    };
    
    if (payload && method === 'POST') {
        options.body = JSON.stringify({"0": payload});
    }
    
    const response = await fetch(url, options);
    const result = await response.json();
    
    // Extract data from batch format
    if (Array.isArray(result) && result[0]?.result?.data) {
        return result[0].result.data.json || result[0].result.data;
    }
    
    return result;
}

// Usage examples:

// List projects
const projects = await callDokploy('project.all', null, 'GET');

// Deploy application
await callDokploy('application.deploy', {
    applicationId: 'app_xxx',
    title: 'Deploy v1.0'
});

// Restart application
await callDokploy('application.reload', {
    applicationId: 'app_xxx'
});
```

---

## Python Example

```python
import requests

class DokployClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.headers = {'x-api-key': api_key}
    
    def call(self, procedure, payload=None, method='POST'):
        url = f"{self.base_url}/api/trpc/{procedure}?batch=1"
        
        if method == 'GET':
            resp = requests.get(url, headers=self.headers)
        else:
            data = {"0": payload} if payload else None
            resp = requests.post(url, headers=self.headers, json=data)
        
        result = resp.json()
        
        # Extract from batch format
        if isinstance(result, list) and len(result) > 0:
            item = result[0]
            if 'result' in item and 'data' in item['result']:
                return item['result']['data'].get('json', item['result']['data'])
        
        return result

# Usage
client = DokployClient('https://your-dokploy.com', 'your_key')

# List projects
projects = client.call('project.all', method='GET')

# Deploy
client.call('application.deploy', {
    'applicationId': 'app_xxx',
    'title': 'Deploy v1.0'
})
```

---

## Finding Available Procedures

Since Dokploy doesn't have a public Swagger UI for tRPC, you can find procedures by:

1. **Source Code**: Check the [Dokploy GitHub](https://github.com/Dokploy/dokploy) server routers

2. **Browser DevTools**:
   - Open Dokploy dashboard
   - Open Network tab (F12)
   - Perform an action (e.g., click "Deploy")
   - Look for requests to `/api/trpc/[procedure]`

3. **Pattern**: Most procedures follow the pattern `[resource].[action]`:
   - `project.all`
   - `application.deploy`
   - `compose.create`
   - `postgres.start`

---

## REST vs tRPC

| Feature | REST | tRPC |
|---------|------|------|
| URL | `/api/project.all` | `/api/trpc/project.all?batch=1` |
| Body | Direct JSON | Wrapped in `{"0": {...}}` |
| Response | Direct JSON | Wrapped in `[{"result": {"data": {"json": ...}}}]` |
| Type Safety | Manual | End-to-end |

The CLI auto-detects which format your Dokploy server uses.

---

## References

- **tRPC Docs**: https://trpc.io/docs
- **Dokploy GitHub**: https://github.com/Dokploy/dokploy
- **Dokploy Docs**: https://docs.dokploy.com/docs/api
