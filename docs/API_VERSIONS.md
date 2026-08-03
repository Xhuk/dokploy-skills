# Dokploy API Versions & Compatibility

> Not all Dokploy servers expose the same endpoints the same way. Identify support first, then automate.

---

## Two API Layers

Dokploy installs commonly expose one or both of these layers:

### 1. OpenAPI / REST

**Characteristics:**
- Endpoints: `/api/project.all`, `/api/application.deploy`
- Request body: direct JSON `{ "key": "value" }`
- Response: direct JSON array/object, or a light wrapper
- Auth: `x-api-key`

**Example:**
```bash
GET /api/project.all
Response: [{"projectId": "xxx", "name": "My Project"}]
```

### 2. tRPC

**Characteristics:**
- Endpoints: `/api/trpc/<procedure>` (sometimes with `?batch=1` for reads)
- Mutation body: wrapped `{"json": <payload>}`
- Response: often wrapped `{"result":{"data":{"json": ...}}}`
- Auth: same `x-api-key`

**Example:**
```bash
POST /api/trpc/application.deploy
Body: {"json":{"applicationId":"APP_ID","title":"Smoke deploy"}}
```

---

## Critical Rule

Do **not** overfit to a single label like "this server is REST" or "this server is tRPC".

Real mixed installs often look like this:
- `GET /api/project.all` works
- `GET /api/application.all` returns `404`
- `POST /api/application.deploy` works on REST
- the equivalent tRPC mutation is missing or behaves differently

Compatibility must be treated as:

1. **server-level** for orientation (probe readers)
2. **endpoint-level** for every mutation you automate

---

## How to Identify Support

### Method 1: Probe a stable reader, then the mutation

```bash
# Stable reader first
curl -H "x-api-key: YOUR_KEY" https://your-dokploy.com/api/project.all

# If 404, try tRPC reader
curl -H "x-api-key: YOUR_KEY" \
  "https://your-dokploy.com/api/trpc/project.all?batch=1"
```

Then probe the mutation you actually need:

```bash
# REST deploy
curl -X POST -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"applicationId":"APP_ID","title":"Smoke deploy"}' \
  https://your-dokploy.com/api/application.deploy

# tRPC deploy fallback
curl -X POST -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"json":{"applicationId":"APP_ID","title":"Smoke deploy"}}' \
  https://your-dokploy.com/api/trpc/application.deploy
```

### Method 2: Check Dokploy version on the host

```bash
docker images | grep dokploy
# or
docker logs dokploy | head -20
```

Heuristic only:
- **v0.9.x or earlier**: more often REST-oriented
- **v0.10.x or later**: more often tRPC-oriented

Never trust the heuristic alone — probe endpoints.

### Method 3: Browser DevTools

1. Open Dokploy dashboard
2. Open Network tab
3. Inspect request URLs:
   - `/api/trpc/` → tRPC path in use
   - `/api/` without `/trpc/` → REST/OpenAPI path in use

---

## Example: Mixed Compatibility Profile

Based on real multi-app production installs (anonymized):

| Aspect | Observation |
|--------|-------------|
| **Reader support** | REST `project.all` is the most reliable discovery path |
| **Mutation support** | Mixed — validate per endpoint |
| **Projects** | `/api/project.all` |
| **Deploy** | Prefer `/api/application.deploy`, then tRPC fallback |
| **Token formats** | `dokploy_...`, custom prefixes, or legacy tokens |

**Working CLI pattern:**
```bash
dokploy projects list
dokploy apps list
dokploy apps deploy --id APP_ID
dokploy user info
```

**Observed gaps on some installs:**
- no `application.all`
- no `application.restart`
- REST deploy works while tRPC deploy is absent (or the reverse)

---

## CLI Auto-Detection Algorithm

Implement conservatively:

```text
1. Try stable REST reader: GET /api/project.all
2. If 404, try tRPC reader
3. For each mutation, try REST first
4. On REST 404/405/400/500 for that mutation, try tRPC with {"json": payload}
5. If list/detail endpoints are missing, extract from project.all
6. Cache per-endpoint success mode for the session
```

Do not flip the whole client to "tRPC mode" after one failure.

---

## Token Formats

| Format | Example | Notes |
|--------|---------|-------|
| Standard | `dokploy_a1b2c3...` | Common on newer installs |
| Prefixed | `prod_dkp_live_...` | Custom naming via createApiKey |
| Legacy/custom | site-specific prefixes | Still use `x-api-key` |

Token format does **not** determine REST vs tRPC. Always probe endpoints.

Never print full tokens in logs, commits, or chat.

---

## Resource Nesting Variants

`project.all` may return either:

1. **Environment-aware:** `projects[].environments[].{applications,compose,postgres,...}`
2. **Legacy flat:** `projects[].{applications,compose,postgres,...}`

Agent code must iterate both shapes when resolving IDs.

---

## Troubleshooting

### `404` on every endpoint

Possible causes:
1. Wrong base URL / path (extra `/api`, missing domain, wrong port)
2. Reverse proxy routing mismatch
3. Very old Dokploy with different procedure names

Check on the host:
```bash
docker ps
docker logs dokploy
```

### `401 Unauthorized` with a key that "looks right"

- Expired key
- Key belongs to another organization/user
- Wrong header (`Authorization: Bearer` instead of `x-api-key`)
- Trailing whitespace when loading from env files

### `403 Forbidden`

User/role attached to the key lacks permission for that mutation.

### Mutation returns `500` with "Invalid JSON"

Often means the server expected the other body shape:
- REST wants bare JSON
- tRPC wants `{"json": ...}`

Retry the alternate layer before declaring failure.

---

## Summary Matrix

| Profile | Typical discovery | Typical deploy |
|---------|-------------------|----------------|
| REST-leaning | `/api/project.all` | `/api/application.deploy` |
| tRPC-leaning | `/api/trpc/project.all` | `/api/trpc/application.deploy` |
| Mixed (common) | REST readers + endpoint-level mutation fallbacks | Probe REST, then tRPC |

**Always test the endpoint you need before scripting a fleet operation.**

See also: [REST_OPERATIONS.md](./REST_OPERATIONS.md)
