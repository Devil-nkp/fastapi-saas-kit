# Deployment

## Local Development

### Using Docker Compose

```bash
cp .env.example .env
docker compose up
```

This starts:
- PostgreSQL 16 on port 5432
- The FastAPI app on port 8000

### Without Docker

```bash
# Prerequisites: Python 3.11+, PostgreSQL running locally

python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your database URL
uvicorn fastapi_saas_kit.main:app --reload
```

## Deployment

### Generic Docker Runtime

```bash
# Build the image
docker build -t fastapi-saas-kit .

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e AUTH_PROVIDER="jwt" \
  -e AUTH_JWT_SECRET="replace-with-random-64-char-value" \
  -e BILLING_PROVIDER="mock" \
  -e ENVIRONMENT="production" \
  -e DEBUG="false" \
  fastapi-saas-kit
```

### Environment Variables for Production

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `AUTH_PROVIDER` | ✅ | Auth provider (jwt, mock) |
| `AUTH_JWT_SECRET` | ✅ | JWT signing secret (64+ chars) |
| `ENVIRONMENT` | ✅ | Set to `production` |
| `DEBUG` | ✅ | Set to `false` |
| `FRONTEND_URL` | ✅ | Your frontend origin for CORS |
| `BILLING_PROVIDER` | Optional | Payment provider |
| `CACHE_PROVIDER` | Optional | Cache backend |

### Hosting Platforms

This boilerplate works with any platform that supports Docker containers:

- **AWS**: ECS, Fargate, App Runner
- **Google Cloud**: Cloud Run, GKE
- **Azure**: Container Apps, AKS
- **Fly.io**: `fly launch`
- **Railway**: Connect repo, auto-deploy
- **DigitalOcean**: App Platform

### Deployment Checklist

- [ ] Set `ENVIRONMENT=production` and `DEBUG=false`
- [ ] Use a strong, random `AUTH_JWT_SECRET` (64+ characters)
- [ ] Configure `FRONTEND_URL` for CORS
- [ ] Set up a managed PostgreSQL instance with SSL
- [ ] Configure a real `AuthProvider` (not mock)
- [ ] Configure a real `BillingProvider` if accepting payments
- [ ] Set up Redis for caching if running multiple workers
- [ ] Enable HTTPS/TLS
- [ ] Set up health check monitoring on `/health/ready`
- [ ] Configure log aggregation
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Run with multiple workers: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker`
