# Dokploy API - Documentación Completa

> Basado en documentación oficial: https://docs.dokploy.com/docs/api
> Última actualización: 2026-04-11

---

## Autenticación

### Header Requerido
```
x-api-key: YOUR_API_KEY
```

**IMPORTANTE:** No usar `Authorization: Bearer`. Dokploy usa `x-api-key`.

### Generar API Key

**Via Web UI:**
1. Ir a `/settings/profile`
2. Sección **API/CLI**
3. Click **Generate API Key**

**Via API (requiere sesión):**
```bash
POST /api/user.createApiKey
{
  "name": "Production Key",
  "prefix": "prod",
  "metadata": {
    "organizationId": "org_xxx"
  },
  "expiresIn": 31536000000,  // 1 año en ms
  "rateLimitEnabled": true,
  "rateLimitTimeWindow": 60000,  // 1 minuto
  "rateLimitMax": 100
}
```

### Rate Limiting

Los API keys pueden tener rate limiting configurado:

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `rateLimitEnabled` | Activar rate limiting | `true` |
| `rateLimitTimeWindow` | Ventana de tiempo (ms) | `60000` (1 min) |
| `rateLimitMax` | Máximo requests por ventana | `100` |
| `remaining` | Requests iniciales disponibles | `1000` |
| `refillAmount` | Requests a recargar | `100` |
| `refillInterval` | Intervalo de recarga (ms) | `3600000` (1 hora) |

---

## Roles y Permisos

Dokploy tiene 3 roles de usuario:

| Rol | Permisos |
|-----|----------|
| **Owner** | Acceso completo a todo |
| **Admin** | Gestionar recursos, usuarios, settings (excepto billing) |
| **Member** | Ver y gestionar recursos asignados |

### Procedimientos Protegidos

- `adminProcedure`: Requiere Owner o Admin
- `protectedProcedure`: Requiere cualquier usuario autenticado
- `publicProcedure`: No requiere autenticación

---

## Organizaciones

Dokploy soporta múltiples organizaciones (v0.19.0+).

Los API keys están scoped a una organización específica.

**Obtener organizaciones:**
```bash
GET /api/user.checkUserOrganizations?userId=USER_ID
```

---

## Endpoints por Categoría

### Projects

#### Listar todos los proyectos
```bash
GET /api/project.all
```

**Respuesta:** Array de proyectos
```json
[
  {
    "projectId": "string",
    "name": "string",
    "description": "string",
    "createdAt": "2024-01-01T00:00:00Z",
    "organizationId": "string",
    "env": "string",
    "environments": [
      {
        "name": "production",
        "environmentId": "string",
        "isDefault": true,
        "applications": [...],
        "postgres": [...],
        "mysql": [...],
        "redis": [...],
        "compose": [...]
      }
    ]
  }
]
```

#### Crear proyecto
```bash
POST /api/project.create
{
  "name": "My Project",
  "description": "Production environment"
}
```

### Applications

#### Listar aplicaciones
```bash
GET /api/application.all
```

#### Crear aplicación
```bash
POST /api/application.create
{
  "name": "My App",
  "environmentId": "env_xxx",
  "description": "Production app"
}
```

#### Deploy aplicación
```bash
POST /api/application.deploy
{
  "applicationId": "app_xxx",
  "title": "Deploy v1.2.0",
  "description": "Production deployment"
}
```

#### Restart aplicación
```bash
POST /api/application.restart
{
  "applicationId": "app_xxx"
}
```

#### Stop aplicación
```bash
POST /api/application.stop
{
  "applicationId": "app_xxx"
}
```

### Docker Compose

#### Listar compose projects
```bash
GET /api/compose.all
```

#### Crear compose
```bash
POST /api/compose.create
{
  "name": "My Stack",
  "environmentId": "env_xxx",
  "composeType": "docker-compose",  // o "stack"
  "composeData": "version: '3.8'\nservices:\n..."
}
```

#### Deploy compose
```bash
POST /api/compose.deploy
{
  "composeId": "compose_xxx"
}
```

### Databases

#### PostgreSQL
```bash
GET /api/postgres.all          # Listar
POST /api/postgres.create      # Crear
POST /api/postgres.deploy      # Deploy
POST /api/postgres.start       # Start
POST /api/postgres.stop        # Stop
```

#### MySQL
```bash
GET /api/mysql.all
POST /api/mysql.create
POST /api/mysql.deploy
```

#### MongoDB
```bash
GET /api/mongo.all
POST /api/mongo.create
POST /api/mongo.deploy
```

#### Redis
```bash
GET /api/redis.all
POST /api/redis.create
POST /api/redis.deploy
```

#### MariaDB
```bash
GET /api/mariadb.all
POST /api/mariadb.create
POST /api/mariadb.deploy
```

### User / API Keys

#### Obtener usuario actual
```bash
GET /api/user.get
```

Respuesta incluye API keys del usuario.

#### Crear API Key
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

**Respuesta:**
```json
{
  "result": {
    "data": {
      "id": "key_xxx",
      "key": "prod_dkp_live_abc123...",
      "name": "Production Key",
      "createdAt": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### Eliminar API Key
```bash
POST /api/user.deleteApiKey
{
  "apiKeyId": "key_xxx"
}
```

#### Obtener métricas de contenedores
```bash
GET /api/user.getContainerMetrics?url=URL&token=TOKEN&appName=NAME&dataPoints=POINTS
```

### Domains & Certificates

#### Listar dominios
```bash
GET /api/domain.all
```

#### Crear dominio
```bash
POST /api/domain.create
{
  "applicationId": "app_xxx",
  "host": "app.example.com",
  "https": true,
  "port": 3000
}
```

### Deployments

#### Listar deployments
```bash
GET /api/deployment.all
```

#### Obtener logs de deployment
```bash
GET /api/deployment.getLogs?deploymentId=DEPLOY_ID
```

### Git Providers

#### Listar providers
```bash
GET /api/gitProvider.all
```

#### Crear GitHub provider
```bash
POST /api/gitProvider.create
{
  "name": "GitHub",
  "providerType": "github",
  "accessToken": "ghp_xxx"
}
```

---

## Formatos de Respuesta

### Respuesta Exitosa

```json
{
  "result": {
    "data": {
      "json": [
        // Datos aquí
      ]
    }
  }
}
```

### Respuesta de Error

```json
{
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE",
    "data": {
      "path": "field_name",
      "code": "invalid_type"
    }
  }
}
```

### Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | Éxito |
| 401 | Unauthorized - API key inválida |
| 403 | Forbidden - Sin permisos suficientes |
| 404 | Not Found - Endpoint o recurso no existe |
| 429 | Rate Limited - Demasiados requests |
| 500 | Error del servidor |

---

## Swagger UI

Dokploy incluye documentación Swagger accesible en:

```
https://your-dokploy-instance.com/swagger
```

Para usar:
1. Ve a `/swagger`
2. Click en **Authorize**
3. Ingresa tu API key
4. Explora los endpoints disponibles

---

## Mejores Prácticas

### 1. Almacenamiento Seguro
```bash
# Bien: Variables de entorno
export DOKPLOY_API_KEY="your_key"
curl -H "x-api-key: $DOKPLOY_API_KEY" ...

# Mal: Hardcoded
curl -H "x-api-key: your_key" ...  # NO HACER ESTO
```

### 2. Nombres Descriptivos
```json
{
  "name": "GitHub Actions - Production Deployments",
  "prefix": "gh-prod"
}
```

### 3. Expiración para Keys Temporales
```json
{
  "name": "Temporary Migration Key",
  "expiresIn": 604800000  // 7 días
}
```

### 4. Rate Limiting Siempre
```json
{
  "rateLimitEnabled": true,
  "rateLimitTimeWindow": 60000,
  "rateLimitMax": 100
}
```

### 5. Keys Separadas por Entorno
```json
// Development
{ "name": "Dev Environment", "prefix": "dev" }

// Production  
{ "name": "Production Environment", "prefix": "prod" }
```

---

## Referencias Oficiales

- **Documentación API**: https://docs.dokploy.com/docs/api
- **Autenticación**: https://docs.dokploy.com/docs/api/reference-security
- **User API**: https://docs.dokploy.com/docs/api/reference-user
- **Application API**: https://docs.dokploy.com/docs/api/reference-application
- **GitHub**: https://github.com/Dokploy/dokploy

---

**Nota**: Esta documentación está basada en la versión oficial de Dokploy. Los endpoints pueden variar según la versión instalada.
