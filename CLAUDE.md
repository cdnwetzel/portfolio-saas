# Portfolio AI SaaS Platform

## Project Overview

This is a production-grade, multi-tenant AI SaaS platform built on your personal infrastructure (2x A4500 GPUs + 300 Mbps fiber). The platform serves as both your professional portfolio showcase and a revenue-generating SaaS product.

**Status**: Scaffolding Phase Complete. Ready for implementation and deployment.

## Core Architecture

```
User Browser
    ↓
Cloudflare / SSL
    ↓
Cloud Ubuntu ($5/month)
├─ React Frontend (Shadcn UI)
├─ Nginx (Reverse Proxy)
├─ Redis (Caching/Rate-limiting)
├─ pgBouncer (Connection Pooling)
└─ FastAPI Proxy
    ↓ [WireGuard Tunnel]
    ↓
Home Gentoo Server (Your Hardware)
├─ vLLM (2x A4500 NVLink Inference)
├─ PostgreSQL (Multi-tenant Data)
├─ Qdrant (Vector DB)
└─ GitHub Webhook Receiver
```

## Key Features

- **Multi-Tenancy**: Row-level security, tenant isolation via JWT/API keys
- **GPU Inference**: vLLM on 2x A4500s, tensor parallelism across both cards
- **Scalable Edge Architecture**: Cloud frontend for low latency, home GPU for compute
- **Automated Data Sync**: GitHub webhooks trigger re-indexing of public repos
- **SaaS Ready**: Stripe integration, usage-based billing, API keys
- **Production Grade**: Docker, Alembic migrations, health checks, monitoring

## Directory Structure

```
portfolio-saas/
├── .github/workflows/          # CI/CD pipelines
├── alembic/                    # Database migrations
├── docs/                       # This documentation
│   ├── 01-architecture.md
│   ├── 02-backend-setup.md
│   ├── 03-frontend-setup.md
│   ├── 04-infrastructure.md
│   ├── 05-deployment.md
│   ├── 06-billing.md
│   └── 07-checklist.md
├── src/
│   ├── api/                    # API routes (chat, auth, billing, kb)
│   ├── core/                   # Config, security, database
│   ├── models/                 # SQLAlchemy models
│   ├── services/               # Business logic (inference, billing, RAG)
│   ├── middleware/             # Auth middleware, request tracking
│   └── main.py                 # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── pages/              # Dashboard, signup, login
│   │   ├── components/         # Reusable UI components
│   │   ├── lib/                # API client, utilities
│   │   └── styles/             # Tailwind + custom CSS
│   └── vite.config.ts
├── cloud/                      # Cloud Ubuntu deployment
│   ├── docker-compose.yml
│   ├── nginx.conf
│   ├── .env.example
│   └── deploy.sh
├── home/                       # Home Gentoo server config
│   ├── systemd/
│   ├── wg0.conf
│   └── requirements.txt
├── tests/                      # Unit and integration tests
├── docker-compose.yml          # Local dev environment
├── requirements.txt            # Python dependencies
├── .env.example
└── README.md
```

## Implementation Phases

### Phase 1: Foundation (Current)
- [x] Database schema design (PostgreSQL)
- [x] Multi-tenancy architecture
- [x] Auth middleware (JWT + API keys)
- [x] Docker orchestration
- [ ] **NEXT**: Create Alembic migrations
- [ ] **NEXT**: Implement auth endpoints (signup/login)
- [ ] **NEXT**: Deploy local dev environment

### Phase 2: Core API
- [ ] Chat streaming endpoints
- [ ] Knowledge base management
- [ ] Document upload/indexing
- [ ] RAG pipeline integration
- [ ] Usage tracking

### Phase 3: Frontend Dashboard
- [ ] Login/signup pages
- [ ] Dashboard overview
- [ ] Knowledge base management UI
- [ ] API key generation
- [ ] Billing/subscription UI

### Phase 4: Infrastructure
- [ ] WireGuard tunnel (Gentoo ↔ Cloud)
- [ ] Nginx configuration with SSL
- [ ] Docker deployment (Cloud)
- [ ] Database migrations
- [ ] Health checks

### Phase 5: Billing & Revenue
- [ ] Stripe product configuration
- [ ] Webhook handlers
- [ ] Usage billing calculations
- [ ] Invoice generation

### Phase 6: DevOps & Launch
- [ ] GitHub Actions CI/CD
- [ ] Automated deployment
- [ ] Monitoring setup
- [ ] DNS cutover
- [ ] Go-live

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **GPU Inference** | vLLM + PyTorch | LLM serving on 2x A4500s |
| **API Framework** | FastAPI + Uvicorn | Async Python backend |
| **Database** | PostgreSQL + SQLAlchemy | Multi-tenant data + migrations |
| **Caching** | Redis | Token caching, rate limiting |
| **Vector DB** | Qdrant | RAG retrieval |
| **Frontend** | React + Shadcn UI | SaaS dashboard |
| **Reverse Proxy** | Nginx | SSL termination, static serving |
| **Networking** | WireGuard | Encrypted tunnel (GPU ↔ Cloud) |
| **Payments** | Stripe | Billing & subscriptions |
| **Orchestration** | Docker Compose | Local dev + cloud deployment |
| **Migrations** | Alembic | Database versioning |
| **CI/CD** | GitHub Actions | Automated testing & deployment |

## Key Configuration Files

1. **docker-compose.yml** - Local dev environment (PostgreSQL, Redis, FastAPI)
2. **src/main.py** - FastAPI application entry point
3. **.env.example** - Environment variables template
4. **cloud/docker-compose.yml** - Production cloud stack
5. **cloud/nginx.conf** - Nginx reverse proxy configuration
6. **alembic/versions/*.py** - Database migrations
7. **.github/workflows/deploy.yml** - GitHub Actions CI/CD

## Key Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| **POST** | /api/auth/signup | Create new tenant | None |
| **POST** | /api/auth/login | User login | None |
| **POST** | /api/knowledge-base | Create KB | JWT |
| **WS** | /ws/chat | Stream LLM responses | JWT/API Key |
| **POST** | /api/api-keys | Generate API key | JWT |
| **GET** | /api/dashboard | Tenant metrics | JWT |
| **POST** | /api/billing/checkout | Create Stripe session | JWT |
| **POST** | /webhooks/github | GitHub push event | Secret |
| **POST** | /webhooks/stripe | Stripe event | Secret |

## Environment Variables

```
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/saas_prod
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# GPU Inference
MODEL_ID=meta-llama/Llama-2-70b-chat-hf
TENSOR_PARALLEL_SIZE=2
GPU_MEMORY_UTILIZATION=0.85

# Frontend
FRONTEND_URL=https://app.yourdomain.com
API_URL=https://api.yourdomain.com
```

## Deployment Checklist

### Local Development
- [ ] Clone repository
- [ ] Copy `.env.example` → `.env` with local values
- [ ] Run `docker-compose up -d`
- [ ] Run `alembic upgrade head`
- [ ] Test `curl http://localhost:8000/health`

### Cloud Ubuntu Setup
- [ ] SSH key setup for deployment
- [ ] DNS A record pointed to cloud IP
- [ ] SSL certificate (Certbot)
- [ ] `.env` configured with production secrets
- [ ] `docker-compose up -d`

### Gentoo Home Server
- [ ] WireGuard keys generated
- [ ] `wg0.conf` configured
- [ ] vLLM running with tensor parallelism
- [ ] PostgreSQL accessible from cloud

### GitHub Integration
- [ ] Repository secrets configured
- [ ] GitHub webhook created
- [ ] CI/CD workflows enabled

### Go-Live
- [ ] DNS cutover
- [ ] SSL verification
- [ ] Smoke tests on production
- [ ] Monitoring active
- [ ] Slack notifications configured

## Quick Start Commands

```bash
# Local development
docker-compose up -d
alembic upgrade head

# Deploy to production
./cloud/deploy.sh

# View logs
docker logs -f portfolio-saas-api-1
docker exec portfolio-saas-api-1 tail -f /var/log/app.log

# Database
docker exec portfolio-saas-db-1 psql -U postgres -d saas_prod
```

## Resources & References

- **Architecture Docs**: See `docs/01-architecture.md`
- **Backend Setup**: See `docs/02-backend-setup.md`
- **Frontend Setup**: See `docs/03-frontend-setup.md`
- **Infrastructure**: See `docs/04-infrastructure.md`
- **Deployment**: See `docs/05-deployment.md`
- **Billing**: See `docs/06-billing.md`
- **Getting Started**: See `docs/07-checklist.md`

## Contact & Support

For issues during setup, refer to the troubleshooting section in each documentation file.

---

**Last Updated**: 2026-06-06
**Current Phase**: Scaffolding Complete, Ready for Implementation
