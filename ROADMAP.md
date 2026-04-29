# Roadmap

## v0.1.0 — Foundation (Current)

- [x] FastAPI app factory
- [x] Pluggable auth with MockAuthProvider
- [x] JWT utilities
- [x] RBAC dependencies (user, org_admin, main_admin)
- [x] Multi-tenant organization model
- [x] Plan configuration (free, pro, business)
- [x] Quota enforcement
- [x] BillingProvider interface with mock
- [x] CacheProvider interface with in-memory
- [x] Rate limiting
- [x] Security headers
- [x] Health checks
- [x] PostgreSQL async pool + migrations
- [x] Docker local setup
- [x] Tests and CI
- [x] Documentation

## v0.2.0 — Production Adapters

- [ ] Redis cache adapter
- [ ] Stripe billing adapter (real implementation)
- [ ] OAuth2 / OIDC auth adapter
- [ ] Webhook handler framework
- [ ] Email notification interface
- [ ] Background task queue interface

## v0.3.0 — Advanced Features

- [ ] Machine-to-machine authentication
- [ ] Invitation system for organizations
- [ ] Audit log system
- [ ] Usage analytics dashboard data
- [ ] Pagination utilities
- [ ] Search and filtering helpers

## v0.4.0 — Enterprise

- [ ] SSO / SAML support interface
- [ ] Multi-region deployment guide
- [ ] Read replica database support
- [ ] Advanced rate limiting (per-endpoint, per-plan)
- [ ] Feature flags system
- [ ] A/B testing framework

## Future

- [ ] CLI tool for project scaffolding
- [ ] Plugin system for custom modules
- [ ] Admin dashboard template
- [ ] Terraform / Pulumi deployment templates
- [ ] Kubernetes deployment manifests
