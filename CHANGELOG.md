# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-01

### Added

- FastAPI application factory with lifespan management
- Pluggable `AuthProvider` interface with `MockAuthProvider`
- JWT token generation and verification utilities
- Role-based access control: `user`, `org_admin`, `main_admin`
- `require_role()` and `require_plan()` FastAPI dependencies
- Multi-tenant organization model with CRUD endpoints
- Tenant-scoped data access with org isolation
- Access tier configuration system with default internal tier values
- Feature gates and access tier hierarchy
- Quota enforcement with configurable limits and period reset
- Provider adapter interface with `MockBillingProvider`
- External provider stub for future integration
- `CacheProvider` interface with `InMemoryCacheProvider`
- Sliding-window rate limiter with in-memory fallback
- Security headers middleware (HSTS, X-Frame-Options, etc.)
- Global error handler with structured JSON responses
- Health check endpoints: `/health`, `/health/ready`
- Async PostgreSQL connection pool with migration runner
- Generic multi-tenant SQL schema
- Docker and docker-compose for local development
- Comprehensive test suite with pytest
- GitHub Actions CI pipeline
- Full documentation suite for architecture, auth, tenancy, roles, access tiers, deployment, and API usage
- Two example applications: basic backend starter and multi-tenant app
