# Dokploy REST Operations Playbook

> Practical REST playbook for agent and operator automation.
> Auth header: `x-api-key`
> Base URL pattern: `https://your-dokploy-instance.com/api/`

Some Dokploy installs also expose tRPC under `/api/trpc/...`. Prefer REST first; fall back to tRPC only for the specific failing endpoint. See [API_VERSIONS.md](./API_VERSIONS.md).

---

## Confirmed Stable Readers

### Projects

```bash
# List all projects (canonical discovery endpoint)
GET /api/project.all

# Get one project
GET /api/project.one?projectId=PROJECT_ID
```

**Example `project.all` shape (environment-aware installs):**

```json
[
  {
    "projectId": "proj_example",
    "name": "my-saas",
    "description": "",
    "organizationId": "org_example",
    "environments": [
      {
        "name": "production",
        "environmentId": "env_example",
        "applications": [
          {
            "applicationId": "app_example",
            "name": "api",
            "applicationStatus": "done"
          }
        ],
        "compose": [],
        "postgres": [],
        "redis": []
      }
    ]
  }
]
```

**Older shape (resources nested directly under project):**

```json
[
  {
    "projectId": "proj_example",
    "name": "Random",
    "applications": [],
    "compose": [],
    "postgres": [],
    "mysql": [],
    "mongo": [],
    "mariadb": [],
    "redis": []
  }
]
```

Agents must support both shapes when discovering apps, compose stacks, and databases.

---

### Applications

```bash
# List applications (when the endpoint exists)
GET /api/application.all

# Get one application
GET /api/application.one?applicationId=APP_ID

# Deploy
POST /api/application.deploy
Body: {"applicationId": "APP_ID", "title": "Deploy v1.0"}

# Rebuild
POST /api/application.rebuild
Body: {"applicationId": "APP_ID"}

# Stop / Start / Restart
POST /api/application.stop
POST /api/application.start
POST /api/application.restart
Body: {"applicationId": "APP_ID"}

# Update source/config
POST /api/application.update
Body: {
  "applicationId": "APP_ID",
  "repository": "my-repo",
  "branch": "main",
  "dockerfile": "Dockerfile",
  "buildPath": "."
}
```

**Fallback:** If `application.all` or `application.one` returns `404`, extract applications from `project.all`:

- environment-aware: `projects[].environments[].applications[]`
- legacy: `projects[].applications[]`

**Restart fallback:** If `application.restart` is missing, use `stop` then `start`, or `rebuild` when a cold rebuild is acceptable.

---

### Deployments

```bash
# List deployments (optionally filter by app)
GET /api/deployment.all
GET /api/deployment.all?applicationId=APP_ID

# Deployment logs
GET /api/deployment.getLogs?deploymentId=DEPLOY_ID
```

---

### Compose (Docker Compose)

```bash
GET /api/compose.all

POST /api/compose.deploy
Body: {"composeId": "COMPOSE_ID"}
```

**Fallback:** If `compose.all` is missing, extract from `project.all`:

- environment-aware: `projects[].environments[].compose[]`
- legacy: `projects[].compose[]`

---

### Databases

```bash
GET /api/postgres.all
POST /api/postgres.create
POST /api/postgres.deploy

GET /api/mysql.all
POST /api/mysql.create

GET /api/mongo.all
POST /api/mongo.create

GET /api/redis.all
POST /api/redis.create

GET /api/mariadb.all
POST /api/mariadb.create
```

Prefer discovering databases from `project.all` when dedicated list endpoints are incomplete.

---

### User

```bash
GET /api/user.get
```

Useful for validating auth and inspecting organization / API key metadata. Never print full API keys.

---

## Common Workflows

### 1. Discover apps by name or surface

```bash
# 1. GET /api/project.all
# 2. Find project by name (case-insensitive)
# 3. Pick environment (production / staging / dev)
# 4. Match applications by name substring or exact name
# 5. Cache applicationId for later mutations
```

Never hardcode application IDs in shared skills. Resolve them at runtime.

### 2. Deploy one application

```bash
POST /api/application.deploy
{
  "applicationId": "APP_ID",
  "title": "Deploy api to production"
}
```

If REST returns `404` / `405` / `400` / `500`, retry:

```bash
POST /api/trpc/application.deploy
{
  "json": {
    "applicationId": "APP_ID",
    "title": "Deploy api to production"
  }
}
```

### 3. Inspect deploy history and logs

```bash
GET /api/deployment.all?applicationId=APP_ID
GET /api/deployment.getLogs?deploymentId=DEPLOY_ID
```

### 4. Rollback posture

Dokploy does not expose a one-click "rollback to previous image" in every install. Practical options:

1. Redeploy a known-good git SHA/tag (update branch/tag, then deploy).
2. `application.rebuild` when rebuild semantics match the desired previous artifact.
3. Redeploy with an explicit title such as `Rollback to previous stable`.

Always verify the public route after the action.

### 5. Generic deploy-by-name helper

```python
#!/usr/bin/env python3
import os
import requests

DOKPLOY_URL = os.environ["DOKPLOY_URL"].rstrip("/")
API_KEY = os.environ["DOKPLOY_API_KEY"]
headers = {"x-api-key": API_KEY}

def iter_applications(projects):
    for proj in projects:
        envs = proj.get("environments")
        if isinstance(envs, list) and envs:
            for env in envs:
                for app in env.get("applications", []) or []:
                    yield proj, env, app
        else:
            for app in proj.get("applications", []) or []:
                yield proj, {"name": "default"}, app

def find_app(name_substr: str):
    projects = requests.get(f"{DOKPLOY_URL}/api/project.all", headers=headers, timeout=30).json()
    needle = name_substr.lower()
    matches = []
    for proj, env, app in iter_applications(projects):
        if needle in str(app.get("name", "")).lower():
            matches.append((proj, env, app))
    return matches

def deploy_app(application_id: str, title: str = ""):
    return requests.post(
        f"{DOKPLOY_URL}/api/application.deploy",
        headers=headers,
        json={"applicationId": application_id, "title": title},
        timeout=60,
    )
```

---

## Endpoints Often Missing on Mixed Installs

| Endpoint | Typical failure | Fallback |
|----------|-----------------|----------|
| `/api/application.all` | `404` | Extract from `project.all` |
| `/api/application.one` | `404` | Extract from `project.all` |
| `/api/application.restart` | `404` | `stop` + `start`, or `rebuild` |
| `/api/compose.all` | `404` | Extract from `project.all` |
| `/api/trpc/*` | `404` | Prefer `/api/*` REST |
| REST mutation | `404`/`405`/`400`/`500` | Try matching `/api/trpc/<procedure>` |

Treat compatibility as **endpoint-level**, not server-wide.

---

## Status Values

Common `applicationStatus` values:

| Status | Meaning |
|--------|---------|
| `done` | Healthy / last operation succeeded |
| `running` | Operation in progress (deploy/rebuild) |
| `error` | Last operation failed — inspect deployment logs |
| `idle` / `stopped` | Not serving (wording varies by version) |

---

## References

- Official API overview: https://docs.dokploy.com/docs/api
- Project API: https://docs.dokploy.com/docs/api/reference-project
- Application API: https://docs.dokploy.com/docs/api/reference-application
- Deployment API: https://docs.dokploy.com/docs/api/reference-deployment
- Swagger UI (if enabled): `https://your-dokploy-instance.com/swagger`
