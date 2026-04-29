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
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
cp .env.example .env
uvicorn fastapi_saas_kit.main:app --reload
```

## Generic Docker Runtime

```bash
docker build -t fastapi-backend .

docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e AUTH_PROVIDER="jwt" \
  -e AUTH_JWT_SECRET="replace-with-random-64-char-value" \
  -e BILLING_PROVIDER="mock" \
  -e ENVIRONMENT="production" \
  -e DEBUG="false" \
  fastapi-backend
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | yes | PostgreSQL connection string |
| `AUTH_PROVIDER` | yes | Auth provider (`jwt`, `mock`) |
| `AUTH_JWT_SECRET` | yes | JWT signing secret (64+ chars) |
| `ENVIRONMENT` | yes | Set to `production` |
| `DEBUG` | yes | Set to `false` |
| `FRONTEND_URL` | yes | Frontend origin for CORS |
| `BILLING_PROVIDER` | Optional | Provider adapter used by access gates |
| `CACHE_PROVIDER` | Optional | Cache backend |

## Hosting Platforms

This backend foundation works with any platform that supports Docker containers:

- AWS: ECS, Fargate, App Runner
- Google Cloud: Cloud Run, GKE
- Azure: Container Apps, AKS
- Fly.io: `fly launch`
- Railway: connect repo, auto-deploy
- DigitalOcean: App Platform

## Deployment Checklist

- [ ] Set `ENVIRONMENT=production` and `DEBUG=false`
- [ ] Use a strong, random `AUTH_JWT_SECRET` (64+ characters)
- [ ] Configure `FRONTEND_URL` for CORS
- [ ] Set up a managed PostgreSQL instance with SSL
- [ ] Configure a real `AuthProvider` instead of mock auth
- [ ] Configure a real provider adapter if your access gates depend on an external system
- [ ] Set up Redis for caching if running multiple workers
- [ ] Enable HTTPS/TLS
- [ ] Set up health check monitoring on `/health/ready`
- [ ] Configure log aggregation
- [ ] Set up error tracking
- [ ] Run with multiple workers: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker`
