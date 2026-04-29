# Multi-Tenant App Example

A multi-organization FastAPI backend using fastapi-saas-kit.

## Run

```bash
cd examples/multi_tenant_app
pip install -e ../../
python main.py
```

Then visit http://localhost:8001/docs to see the API.

## What This Demonstrates

- Organization-scoped endpoints
- Role-based access control (user, org_admin, main_admin)
- Tenant isolation patterns
- Provider adapter integration with MockBillingProvider
- Feature gates per access tier
