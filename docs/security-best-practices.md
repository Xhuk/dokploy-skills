# Dokploy Security Best Practices

Essential security guidelines for production Dokploy deployments.

---

## 🔐 Overview

Security in Dokploy involves multiple layers:
1. **VPS/Server Security**
2. **Docker Security**
3. **Application Security**
4. **Network Security**
5. **Secrets Management**

---

## 🛡️ VPS Security

### Initial Server Setup

```bash
# 1. Update system
apt update && apt upgrade -y

# 2. Create non-root user
adduser deployer
usermod -aG sudo deployer

# 3. Configure SSH
# Edit /etc/ssh/sshd_config:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3

# 4. Setup firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 5. Install fail2ban
apt install fail2ban -y
systemctl enable fail2ban

# 6. Automatic security updates
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades
```

### Docker Security

```bash
# Run Docker security scan
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image <your-image>

# Enable Docker content trust
export DOCKER_CONTENT_TRUST=1
```

---

## 📦 Container Security

### Dockerfile Best Practices

```dockerfile
# Use specific versions, not 'latest'
FROM node:18.17-alpine

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Set working directory
WORKDIR /app

# Copy package files first (better caching)
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY --chown=nextjs:nodejs . .

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Start application
CMD ["node", "server.js"]
```

### docker-compose Security

```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    
    # Security: Run as non-root
    user: "1001:1001"
    
    # Security: Read-only root filesystem
    read_only: true
    
    # Security: No new privileges
    security_opt:
      - no-new-privileges:true
    
    # Security: Drop capabilities
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    
    # Security: Resource limits
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    
    # Security: Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # Security: Restart policy
    restart: unless-stopped
    
    # Security: No privileged mode
    privileged: false
    
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
    
    volumes:
      # Security: Specific paths only
      - ../files/uploads:/app/uploads:rw
      - ../files/logs:/app/logs:rw
    
    networks:
      - dokploy-network
      - internal
    
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls.certResolver=letsencrypt"
      
      # Security Headers
      - "traefik.http.middlewares.security-headers.headers.stsSeconds=31536000"
      - "traefik.http.middlewares.security-headers.headers.forceSTSHeader=true"
      - "traefik.http.middlewares.security-headers.headers.stsIncludeSubdomains=true"
      - "traefik.http.middlewares.security-headers.headers.stsPreload=true"
      - "traefik.http.middlewares.security-headers.headers.customFrameOptionsValue=DENY"
      - "traefik.http.middlewares.security-headers.headers.contentTypeNosniff=true"
      - "traefik.http.middlewares.security-headers.headers.browserXssFilter=true"
      - "traefik.http.routers.app.middlewares=security-headers"

networks:
  dokploy-network:
    external: true
  internal:
    driver: bridge
    internal: true  # No external access
```

---

## 🔑 Secrets Management

### Environment Variables

```bash
# ✅ Good: Use Dokploy UI for secrets
# Set in Dokploy Dashboard > Project > Environment

# ❌ Bad: Never commit secrets
cp .env.example .env
echo ".env" >> .gitignore

# ✅ Good: Encrypt sensitive files
dokploy secrets encrypt .env
```

### Secret Rotation

```bash
# Generate new secrets
dokploy secrets rotate --project myapp

# Update environment
dokploy deploy --project myapp
```

---

## 🌐 Network Security

### Network Architecture

```
Internet
    │
    ▼
┌─────────────────┐
│  Cloudflare     │  ← DDoS protection, WAF
│  (Optional)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  UFW/Firewall   │  ← Port filtering
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Traefik        │  ← SSL termination, rate limiting
│  (Dokploy)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Your App       │  ← Internal network
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Database       │  ← Internal network only
└─────────────────┘
```

### Network Configuration

```yaml
# docker-compose.yml
networks:
  # External: For Traefik routing
  dokploy-network:
    external: true
  
  # Internal: App <-> Database only
  backend:
    driver: bridge
    internal: true  # No internet access
    ipam:
      config:
        - subnet: 172.20.0.0/16
  
  # Isolated: Sensitive services
  database:
    driver: bridge
    internal: true
    attachable: false
```

---

## 🚀 Application Security

### Security Headers

Configure via Traefik labels:

```yaml
labels:
  # HSTS
  - "traefik.http.middlewares.security.headers.stsSeconds=31536000"
  - "traefik.http.middlewares.security.headers.forceSTSHeader=true"
  
  # Content Security
  - "traefik.http.middlewares.security.headers.contentSecurityPolicy=default-src 'self'"
  
  # XSS Protection
  - "traefik.http.middlewares.security.headers.browserXssFilter=true"
  
  # Clickjacking
  - "traefik.http.middlewares.security.headers.customFrameOptionsValue=DENY"
  
  # MIME Sniffing
  - "traefik.http.middlewares.security.headers.contentTypeNosniff=true"
  
  # Referrer Policy
  - "traefik.http.middlewares.security.headers.referrerPolicy=strict-origin-when-cross-origin"
```

### Rate Limiting

```yaml
labels:
  # Rate limiting
  - "traefik.http.middlewares.rate-limit.ratelimit.average=100"
  - "traefik.http.middlewares.rate-limit.ratelimit.burst=50"
  - "traefik.http.routers.app.middlewares=rate-limit"
```

---

## 📊 Security Monitoring

### Log Monitoring

```bash
# Watch for suspicious activity
dokploy logs --project myapp | grep -E "(error|fail|unauthorized)"

# Set up alerts
dokploy monitor alerts --config alerts.yaml
```

### Security Scanning

```bash
# Run security scan
dokploy security scan --project myapp

# Continuous scanning
dokploy security scan --watch
```

---

## ✅ Security Checklist

### Before Production

- [ ] VPS: Non-root user configured
- [ ] VPS: SSH key auth only
- [ ] VPS: Firewall enabled (ports 22, 80, 443 only)
- [ ] VPS: Automatic security updates
- [ ] VPS: Fail2ban installed
- [ ] Docker: Running as non-root user
- [ ] Docker: Read-only root filesystem
- [ ] Docker: Resource limits set
- [ ] Docker: Health checks configured
- [ ] Docker: No privileged containers
- [ ] App: Secrets in environment variables (not code)
- [ ] App: Security headers configured
- [ ] App: Rate limiting enabled
- [ ] Network: dokploy-network configured
- [ ] Network: Internal network for database
- [ ] SSL: Let's Encrypt certificates
- [ ] SSL: HSTS enabled
- [ ] Backups: Automated backup schedule
- [ ] Monitoring: Alerts configured
- [ ] Logs: Centralized logging

---

## 🚨 Incident Response

### If Compromised

1. **Isolate**
   ```bash
   # Stop all services
   docker-compose stop
   
   # Block traffic
   ufw deny from <suspicious-ip>
   ```

2. **Investigate**
   ```bash
   # Check logs
   docker logs <container>
   
   # Check connections
   netstat -tulpn
   ```

3. **Recover**
   ```bash
   # Restore from backup
   dokploy backup restore --date <backup-date>
   
   # Rotate all secrets
   dokploy secrets rotate --all
   
   # Redeploy
   dokploy deploy
   ```

---

## 📚 Additional Resources

- [Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Last Updated**: 2026-04-11
