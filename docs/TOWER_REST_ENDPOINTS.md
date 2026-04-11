# Tower REST API Endpoints - VetGroom

> Endpoints REST específicos para el Control Tower de VetGroom
> Base URL: https://internal.vetgroom.com.mx/api/
> Auth: x-api-key header

---

## Endpoints Confirmados (Funcionan)

### Projects

```bash
# Listar todos los proyectos
GET /api/project.all

# Obtener un proyecto específico
GET /api/project.one?projectId=PROJECT_ID
```

**Ejemplo respuesta project.all:**
```json
[
  {
    "projectId": "mue_yrzkPauqycW95F-7_",
    "name": "Vetgroom",
    "description": "",
    "organizationId": "DLQMF6iamFJ2mNkxfN0nb",
    "environments": [
      {
        "name": "production",
        "environmentId": "En3GLvZ4qBCv2qA4_ctur",
        "applications": [
          {
            "applicationId": "YHy1wKu4JCBlSFLytFsAW",
            "name": "VetGroom app",
            "applicationStatus": "done"
          }
        ]
      }
    ]
  }
]
```

---

### Applications

```bash
# Listar aplicaciones (cuando existe endpoint)
GET /api/application.all

# Obtener aplicación específica
GET /api/application.one?applicationId=APP_ID

# Desplegar aplicación
POST /api/application.deploy
Body: {"applicationId": "APP_ID", "title": "Deploy v1.0"}

# Reconstruir aplicación
POST /api/application.rebuild
Body: {"applicationId": "APP_ID"}

# Detener aplicación
POST /api/application.stop
Body: {"applicationId": "APP_ID"}

# Iniciar aplicación
POST /api/application.start
Body: {"applicationId": "APP_ID"}
```

**Nota:** En VetGroom, `application.all` no está disponible. Extraer de `project.all`.

---

### Deployments

```bash
# Listar deployments (todos o por app)
GET /api/deployment.all
GET /api/deployment.all?applicationId=APP_ID

# Obtener logs de deployment
GET /api/deployment.getLogs?deploymentId=DEPLOY_ID
```

---

### Compose (Docker Compose)

```bash
# Listar proyectos compose
GET /api/compose.all

# Desplegar compose
POST /api/compose.deploy
Body: {"composeId": "COMPOSE_ID"}
```

**Nota:** En VetGroom, extraer de `project.all` → `environments[].compose`.

---

### User

```bash
# Obtener información del usuario
GET /api/user.get
```

**Respuesta incluye:**
- Información personal
- Organización
- API keys
- Permisos

---

## Aplicaciones VetGroom (Mapeo)

| Surface | App Name | App ID | Status |
|---------|----------|--------|--------|
| relay | VetGroom relay | 1KYKWHuLvdluMHjgc-8Oz | done |
| landing | VetGroom landing | mSPOUXoDyZRCjWiJepUcu | done |
| app | VetGroom app | YHy1wKu4JCBlSFLytFsAW | done |
| founder | VetGroom founder | JWt8iO0eeUF0-kUdpZjVZ | done |
| web | VetGroom web app | fKjF_pBKohe8E4oDeQuSO | error |

---

## Workflows Comunes

### 1. Descubrir Apps por Surface

```bash
# 1. Listar proyectos
GET /api/project.all

# 2. Encontrar proyecto "Vetgroom"
# 3. Extraer apps del environment "production"
# 4. Filtrar por nombre (relay, landing, app, founder, web)
```

### 2. Desplegar una Surface

```bash
# Deploy de "VetGroom app"
POST /api/application.deploy
{
  "applicationId": "YHy1wKu4JCBlSFLytFsAW",
  "title": "Deploy landing to production"
}
```

### 3. Consultar Historial de Deploys

```bash
# Listar deployments de una app
GET /api/deployment.all?applicationId=YHy1wKu4JCBlSFLytFsAW

# Obtener logs de un deployment específico
GET /api/deployment.getLogs?deploymentId=DEPLOY_ID
```

### 4. Rollback (Reconstruir versión anterior)

```bash
# Obtener deployments ordenados por fecha
GET /api/deployment.all?applicationId=APP_ID

# El "rollback" en Dokploy es reconstruir:
POST /api/application.rebuild
{
  "applicationId": "APP_ID"
}

# O redeploy con título descriptivo:
POST /api/application.deploy
{
  "applicationId": "APP_ID",
  "title": "Rollback to previous stable"
}
```

---

## Endpoints No Disponibles en VetGroom

| Endpoint | Estado | Alternativa |
|----------|--------|-------------|
| `/api/application.all` | ❌ 404 | Extraer de `project.all` |
| `/api/application.restart` | ❌ 404 | Usar `stop` + `start` o `rebuild` |
| `/api/compose.all` | ❌ 404 | Extraer de `project.all` |
| `/api/trpc/*` | ❌ 404 | Usar `/api/*` (REST) |

---

## Ejemplo: Script de Deploy por Surface

```python
#!/usr/bin/env python3
import requests

DOCKPLOY_URL = "https://internal.vetgroom.com.mx"
API_KEY = "sfox_..."

headers = {"x-api-key": API_KEY}

def get_apps():
    """Extraer apps de project.all"""
    resp = requests.get(f"{DOCKPLOY_URL}/api/project.all", headers=headers)
    projects = resp.json()
    
    apps = {}
    for proj in projects:
        for env in proj.get("environments", []):
            for app in env.get("applications", []):
                name = app.get("name", "").lower()
                if "relay" in name:
                    apps["relay"] = app
                elif "landing" in name:
                    apps["landing"] = app
                elif "founder" in name:
                    apps["founder"] = app
                elif "web" in name:
                    apps["web"] = app
                elif "app" in name and "web" not in name:
                    apps["app"] = app
    return apps

def deploy_surface(surface_name, title=""):
    """Desplegar una surface específica"""
    apps = get_apps()
    
    if surface_name not in apps:
        print(f"Surface '{surface_name}' no encontrada")
        return False
    
    app_id = apps[surface_name]["applicationId"]
    
    resp = requests.post(
        f"{DOCKPLOY_URL}/api/application.deploy",
        headers=headers,
        json={"applicationId": app_id, "title": title}
    )
    
    return resp.status_code == 200

# Uso
deploy_surface("landing", "Deploy via Tower")
deploy_surface("app", "Production deploy v1.2.0")
```

---

## Referencias

- Documentación oficial: https://docs.dokploy.com/docs/api
- Swagger (si habilitado): https://internal.vetgroom.com.mx/api-docs
- Project API: https://docs.dokploy.com/docs/api/reference-project
- Application API: https://docs.dokploy.com/docs/api/reference-application
- Deployment API: https://docs.dokploy.com/docs/api/reference-deployment
