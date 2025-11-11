# Merge-05: Deployment & Production Readiness

**Prerequisites:** Testing complete, all tests passing  
**Objective:** Deploy integrated system to production

---

## 🎯 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Production                            │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────────────┐ │
│  │                  │         │                          │ │
│  │  Next.js App     │◄────────┤  FastAPI Agents Service │ │
│  │  (Vercel/Netlify)│  HTTPS  │  (Railway/Render/Fly.io)│ │
│  │                  │         │                          │ │
│  │  Port: 443       │         │  Port: 8000              │ │
│  └──────────────────┘         └──────────────────────────┘ │
│         │                                │                  │
│         │                                │                  │
│         ▼                                ▼                  │
│  ┌──────────────────┐         ┌──────────────────────────┐ │
│  │  Supabase        │         │  Observability Stack     │ │
│  │  (PostgreSQL)    │         │  (Datadog/Sentry)        │ │
│  └──────────────────┘         └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Options

### Option A: Vercel + Railway (Recommended)

**Next.js App → Vercel**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project root
cd apps/web
vercel

# Configure environment variables in Vercel dashboard
# - NEXT_PUBLIC_AGENTS_API_URL=https://your-agents.railway.app
# - NEXT_PUBLIC_AGENTS_WS_URL=wss://your-agents.railway.app
```

**FastAPI Agents → Railway**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy agents service
cd apps/agents
railway login
railway init
railway up

# Configure environment variables in Railway dashboard
# - CORS_ORIGINS=https://your-app.vercel.app
# - OPENAI_API_KEY=...
# - DATABASE_URL=...
```

### Option B: Netlify + Render

**Next.js App → Netlify**
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
cd apps/web
netlify deploy --prod
```

**FastAPI Agents → Render**
- Create `render.yaml` in project root
- Push to GitHub
- Connect Render to repository

### Option C: Docker + Cloud Run/ECS

**Create Dockerfiles**

`apps/web/Dockerfile`:
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
```

`apps/agents/Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`docker-compose.yml` (for local testing):
```yaml
version: '3.8'

services:
  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_AGENTS_API_URL=http://agents:8000
      - NEXT_PUBLIC_AGENTS_WS_URL=ws://agents:8000
    depends_on:
      - agents

  agents:
    build:
      context: ./apps/agents
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CORS_ORIGINS=http://localhost:3000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./apps/agents:/app

  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=opencut
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## ⚙️ Configuration

### Environment Variables

**Web App (`.env.production`)**
```bash
# Agents API
NEXT_PUBLIC_AGENTS_API_URL=https://agents.your-domain.com
NEXT_PUBLIC_AGENTS_WS_URL=wss://agents.your-domain.com

# Database (Supabase)
DATABASE_URL=postgresql://...
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...

# Auth (Better Auth)
BETTER_AUTH_SECRET=...
BETTER_AUTH_URL=https://your-app.com

# Analytics (optional)
NEXT_PUBLIC_VERCEL_ANALYTICS_ID=...
```

**Agents Service (`.env.production`)**
```bash
# CORS
CORS_ORIGINS=https://your-app.vercel.app,https://www.your-app.com

# AI APIs
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Database
DATABASE_URL=postgresql://...

# Observability
SENTRY_DSN=...
DATADOG_API_KEY=...

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
```

---

## 🔒 Security Checklist

### HTTPS/WSS
- [ ] Force HTTPS on web app
- [ ] Use WSS (not WS) for WebSocket in production
- [ ] Configure SSL certificates (Let's Encrypt)

### CORS Configuration
```python
# apps/agents/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "https://www.your-app.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Keys
- [ ] Never commit API keys to git
- [ ] Use environment variables
- [ ] Rotate keys regularly
- [ ] Implement rate limiting

### WebSocket Security
```python
# Add authentication to WebSocket
@router.websocket("/stream")
async def voice_stream_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    # Verify token before accepting connection
    user = await verify_token(token)
    if not user:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    await manager.connect(websocket)
    # ...
```

---

## 📊 Monitoring & Observability

### Datadog Integration

**Web App (Next.js)**
```typescript
// apps/web/src/instrumentation.ts
import { datadogRum } from '@datadog/browser-rum';

export function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    // Server-side monitoring
    const tracer = require('dd-trace').init({
      service: 'opencut-web',
      env: process.env.NODE_ENV
    });
  }
  
  if (typeof window !== 'undefined') {
    // Browser monitoring
    datadogRum.init({
      applicationId: process.env.NEXT_PUBLIC_DD_APP_ID!,
      clientToken: process.env.NEXT_PUBLIC_DD_CLIENT_TOKEN!,
      site: 'datadoghq.com',
      service: 'opencut-web',
      env: process.env.NODE_ENV,
      sessionSampleRate: 100,
      trackInteractions: true
    });
  }
}
```

**Agents Service (FastAPI)**
```python
# apps/agents/main.py
from ddtrace import tracer, patch_all

# Enable auto-instrumentation
patch_all()

# Track custom metrics
from datadog import statsd

@app.on_event("startup")
async def startup_event():
    statsd.increment('opencut.agents.startup')
```

### Sentry Error Tracking

**Web App**
```typescript
// apps/web/sentry.client.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  integrations: [
    new Sentry.BrowserTracing(),
  ]
});
```

**Agents Service**
```python
# apps/agents/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "production")
)
```

---

## 🔧 Performance Optimization

### CDN Configuration
- [ ] Enable CDN for static assets
- [ ] Configure cache headers
- [ ] Implement image optimization (Next.js Image)

### Database Optimization
- [ ] Enable connection pooling
- [ ] Configure query caching
- [ ] Set up read replicas

### WebSocket Scaling
```python
# Use Redis for multi-instance WebSocket support
from redis import Redis
from fastapi_socketio import SocketManager

redis_client = Redis.from_url(os.getenv("REDIS_URL"))
socket_manager = SocketManager(
    app=app,
    client_manager=redis_client
)
```

---

## 🚦 Health Checks

### Web App
```typescript
// apps/web/src/app/api/health/route.ts
export async function GET() {
  const checks = {
    database: await checkDatabase(),
    agents: await checkAgentsAPI(),
    timestamp: new Date().toISOString()
  };
  
  const isHealthy = Object.values(checks).every(c => c === true);
  
  return Response.json(checks, { 
    status: isHealthy ? 200 : 503 
  });
}
```

### Agents Service
```python
# apps/agents/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "observability": get_observability().get_degradation_metrics(),
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## 📋 Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing
- [ ] TypeScript compiles without errors
- [ ] Linting passing
- [ ] No console.log in production code

### Security
- [ ] Environment variables configured
- [ ] CORS properly configured
- [ ] HTTPS/WSS enforced
- [ ] API keys secured
- [ ] Rate limiting enabled

### Performance
- [ ] Bundle size optimized
- [ ] Images optimized
- [ ] Database queries optimized
- [ ] Caching configured

### Monitoring
- [ ] Error tracking configured (Sentry)
- [ ] Performance monitoring (Datadog)
- [ ] Logging configured
- [ ] Alerts set up

### Documentation
- [ ] README updated
- [ ] API documentation current
- [ ] Environment variables documented
- [ ] Deployment runbook created

---

## 🔍 Context for Implementation

### Perplexity Searches

**Query 1: Deployment Strategies**
```
Next.js + FastAPI deployment best practices 2025:
- Microservice deployment patterns
- Vercel + Railway integration
- WebSocket deployment considerations
- SSL/TLS configuration
- Environment variable management
```

**Query 2: Production Monitoring**
```
Production monitoring for microservices:
- Datadog APM setup for Next.js and FastAPI
- Sentry error tracking configuration
- Health check implementation
- Log aggregation strategies
- Alert configuration best practices
```

---

## 🎉 Go Live Procedure

### 1. Final Testing
```bash
# Run full test suite
cd apps/web && npm test
cd apps/agents && pytest

# Run E2E tests
npm run test:e2e
```

### 2. Deploy Agents Service First
```bash
cd apps/agents
railway up  # or equivalent
# Wait for health check to pass
curl https://agents.your-domain.com/health
```

### 3. Deploy Web App
```bash
cd apps/web
vercel --prod
# Verify deployment
curl https://your-app.vercel.app/api/health
```

### 4. Smoke Test
- [ ] Visit production URL
- [ ] Switch to LangGraph mode
- [ ] Send test message
- [ ] Verify agent responds
- [ ] Check generated asset appears
- [ ] Drag asset to timeline

### 5. Monitor
- [ ] Check Datadog dashboards
- [ ] Review Sentry for errors
- [ ] Monitor logs for issues
- [ ] Watch performance metrics

---

**Status:** Ready for deployment  
**Next:** Execute deployment procedure
