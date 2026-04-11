# Dokploy API Versions

> Not all Dokploy servers use the same API format. This guide helps you identify which version you have.

---

## Two API Formats

Dokploy has evolved through different API architectures:

### 1. REST API (Older versions, some custom installs)

**Characteristics:**
- Endpoints: `/api/project.all`, `/api/application.deploy`
- Request body: Direct JSON `{ "key": "value" }`
- Response: Direct JSON array or object
- Token format: Any (depends on setup)

**Example:**
```bash
GET /api/project.all
Response: [{"projectId": "xxx", "name": "My Project"}]
```

### 2. tRPC API (v0.10+, standard installs)

**Characteristics:**
- Endpoints: `/api/trpc/project.all?batch=1`
- Request body: Wrapped `{"0": { "key": "value" }}`
- Response: Wrapped `[{"result": {"data": {"json": [...]}}}]`
- Token format: Usually `dokploy_...` prefix

**Example:**
```bash
GET /api/trpc/project.all?batch=1
Response: [{"result": {"data": {"json": [{"projectId": "xxx"}]}}}]
```

---

## How to Identify Your Version

### Method 1: Test the URL

```bash
# Test REST
curl -H "x-api-key: YOUR_KEY" https://your-dokploy.com/api/project.all

# If 404, try tRPC
curl -H "x-api-key: YOUR_KEY" https://your-dokploy.com/api/trpc/project.all?batch=1
```

### Method 2: Check Dokploy Version

SSH into your server:
```bash
docker images | grep dokploy
# or
docker logs dokploy | head -20
```

- **v0.9.x or earlier**: Likely REST
- **v0.10.x or later**: Likely tRPC

### Method 3: Browser DevTools

1. Open Dokploy dashboard
2. Open Network tab (F12)
3. Look at the URLs:
   - Contains `/api/trpc/` = **tRPC**
   - Contains `/api/` without `/trpc/` = **REST**

---

## VetGroom Server (Your Case)

Based on testing:

| Aspect | Value |
|--------|-------|
| **URL** | https://internal.vetgroom.com.mx |
| **Format** | REST (not tRPC) |
| **Projects** | `/api/project.all` |
| **Deploy** | `/api/application.deploy` |
| **Token** | `sfox_...` (custom format) |

**Working Commands:**
```bash
# Projects
dokploy projects list

# Applications
dokploy apps list
dokploy apps deploy --id APP_ID

# User
dokploy user info
```

**NOT Working:**
- `dokploy apps restart` (endpoint not available in this version)

---

## CLI Auto-Detection

The Dokploy CLI auto-detects the API format:

```python
# 1. Try REST first (GET /api/project.all)
# 2. If 404, try tRPC (GET /api/trpc/project.all?batch=1)
# 3. Use whichever works
```

You don't need to configure this manually.

---

## Token Formats

Dokploy API keys can have different formats depending on version and configuration:

| Format | Example | Version |
|--------|---------|---------|
| `dokploy_...` | `dokploy_a1b2c3...` | Standard v0.10+ |
| Custom prefix | `prod_dkp_live_...` | Custom configured |
| No prefix | `sfox_TSjkTfz...` | Custom/legacy |

**Important:** The token format doesn't determine API type. Always test the endpoints.

---

## Troubleshooting

### "404 Not Found" on all endpoints

Your Dokploy might be:
1. Using a different base path (e.g., `/api/v2/`)
2. Behind a reverse proxy with different routing
3. A very old version with different endpoints

**Check:**
```bash
# SSH to server and check
docker ps
docker logs dokploy
```

### "401 Unauthorized" but key is correct

- Key might be expired
- Key might be for different organization
- Server might use different auth method

---

## Summary

| Your Server | Format | Base URL |
|-------------|--------|----------|
| VetGroom | REST | `https://internal.vetgroom.com.mx/api/` |
| Standard v0.10+ | tRPC | `https://dokploy.com/api/trpc/` |

**Always test first, don't assume based on documentation.**
